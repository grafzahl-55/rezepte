#!/usr/bin/env python3
"""
import-chefkoch-jsonld.py — Importiert ein Rezept aus chefkoch.de über das
JSON-LD (`<script type="application/ld+json">`).

chefkoch liefert das Rezept als **`@type:"Recipe"`**-Objekt im JSON-LD (im
`<script>`-Block, oft **verschachtelt** innerhalb eines Arrays). Die
Zutaten (`recipeIngredient`) und Schritte (`recipeInstructions`,
`HowToSection`/`HowToStep`) liegen als Arrays vor.

Bild: Das **`og:image`** im `<head>` ist das Primärbild. Es wird heruntergeladen
und ggf. mit PIL auf 800 px Breite + Baseline-JPEG resized.

Workflow:
  1. Rohdaten-HTML liegt in `rohdaten/[name].html` (von `curl` mit `Mozilla/5.0`).
  2. Bild wird aus dem CDN heruntergeladen.
  3. Markdown wird unter `docs/rezepte/[name].md` angelegt.
  4. `--index` ergänzt den Index-Eintrag (Icon ❓, kein Bewertungstags).

Kein Bewertungstags beim Import (CLAUDE.md Regel 7).

Aufruf:
    python3 bin/import-chefkoch-jsonld.py --url "https://www.chefkoch.de/rezepte/..." [--rohdaten name] [--index] [--write]

Ohne --write läuft im Dry-Run-Modus.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

import urllib.error

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REZEPTE_DIR = os.path.join(ROOT, "docs", "rezepte")
IMAGES_DIR = os.path.join(ROOT, "docs", "images")
INDEX_FILE = os.path.join(ROOT, "docs", "index.md")

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def normalize_name(name):
    """Bereinigt den Dateinamen: alphanumerisch, Kleinbuchstaben, - als Trennzeichen.

    Umlaute wie bei der Sortierung in ae/oe/ue, „ß" -> „ss". Bereits vorhandene
    Trennungs-Bindestriche bleiben erhalten.
    """
    name = name.strip().lower()
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    name = name.replace("ß", "ss")
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-{2,}", "-", name)
    name = name.strip("-")
    return name


def name_exists(name):
    return (os.path.exists(os.path.join(REZEPTE_DIR, name + ".md"))
            or os.path.exists(os.path.join(IMAGES_DIR, name + "-img.jpg")))


def resolve_name(name):
    n = name
    i = 1
    while name_exists(n):
        n = "%s-%d" % (name, i)
        i += 1
    return n


def extract_jsonld_recipe(html):
    """Extrahiert das erste `@type:"Recipe"`-Objekt aus dem JSON-LD.

    Der `<script type="application/ld+json">`-Block enthält oft mehr als das
    Rezept (z. B. Kommentare, Reviews). Das Rezept-Objekt wird über
    geschweifte-Klammern ausbalanciert gefunden.
    """
    m = re.search(r'<script type="application/ld\+json">(.+)</script>', html, re.S)
    if not m:
        return None
    s = m.group(1)
    start = s.find('{"@type":"Recipe"')
    if start == -1:
        return None
    depth = 0
    end = None
    for idx in range(start, len(s)):
        if s[idx] == "{":
            depth += 1
        elif s[idx] == "}":
            depth -= 1
            if depth == 0:
                end = idx + 1
                break
    if end is None:
        return None
    return json.loads(s[start:end])


def extract_og_image(html):
    """Das `og:image` im `<head>` (Primärbild)."""
    og = re.findall(r'og:image" content="([^"]+)"', html)
    if og:
        return og[0]
    return None


def extract_html_author(html):
    """Autor aus `<meta name="author" content="...">` (z. B. „Steffi (Gaumenfreundin)").

    Fallback: nur wenn kein JSON-LD-Autor gefunden wurde (Regel 1 des fix-chefkoch-import).
    """
    m = re.findall(r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']', html)
    if m:
        return m[0].strip()
    return None


def resolve_author(recipe, html):
    """Autor: JSON-LD-`author.name` -> HTML-Meta -> '-'.

    Vorrang (Regel 1 fix-chefkoch-import): JSON-LD, sonst HTML, sonst '-'.
    """
    author = recipe.get("author")
    if isinstance(author, dict) and author.get("name"):
        return author["name"].strip()
    html_author = extract_html_author(html)
    if html_author:
        return html_author.strip()
    return "-"


def extract_recipe_url(html):
    """Die canonical-URL des Rezepts (für den Index-„Quelle"-Link).

    Erst nach `og:url`, dann nach einem `<link rel="canonical">`, dann
    dem ersten JSON-LD-Objekt-`url`. Falls nichts: „https://www.chefkoch.de".
    """
    # og:url
    ogu = re.findall(r'og:url" content="([^"]+)"', html)
    if ogu:
        return ogu[0]
    # canonical
    can = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
    if can:
        return can[0]
    # JSON-LD url
    try:
        recipe = extract_jsonld_recipe(html)
        if recipe and recipe.get("url"):
            return str(recipe["url"]).rstrip("/")
    except Exception:
        pass
    return "https://www.chefkoch.de"


def resolve_source_name(html, url):
    """Name der tatsächlich genutzten Quelle (nicht „Chefkoch").

    Vorrang (fix-chefkoch-import):
      1) Der im HTML-Code genannte Site-Name (z. B. „Gaumenfreundin" in og-site
         oder einem JSON-LD-Feld), wenn leicht zu ermitteln.
      2) Sonst die Domain der URL (z. B. „gaumenfreundin.de").
    """
    # og:site-Tag (z. B. <meta name="og:site_name" content="Gaumenfreundin ...">)
    site = re.findall(r'og:site_name"?\s*content="([^"]+)"', html)
    if site:
        return re.split(r"[\s–-]", site[0].strip())[0]
    # WebSite-Node im JSON-LD-@graph (nicht der Rezept-Titel!).
    # Der WebSite-Node kann verschachtelte Objekte enthalten, daher wird er über
    # geschweifte-Klammern ausbalanciert gefunden (wie extract_jsonld_recipe).
    try:
        for block in re.findall(r'<script type="application/ld\+json">(.+)</script>', html, re.S):
            for m in re.finditer(r'\s*{"@type":"WebSite"', block):
                # Der Regex enthält das „{"@type":"WebSite""; der „{" liegt bei m.start().
                start = m.start()
                depth = 0
                end = None
                for idx in range(start, len(block)):
                    if block[idx] == "{":
                        depth += 1
                    elif block[idx] == "}":
                        depth -= 1
                        if depth == 0:
                            end = idx + 1
                            break
                if end is None:
                    continue
                o = json.loads(block[start:end])
                name = str(o.get("name", "")).strip()
                if name:
                    # Kürze lange Blog-Tagebuch-Namen auf den ersten Wortteil (z. B.
                    # „Gaumenfreundin Foodblog – ..." -> „Gaumenfreundin").
                    return re.split(r"[\s–-]", name)[0]
    except Exception:
        pass
    # Domain der URL
    if url:
        host = re.split(r"[/?#]", url, 1)[0]
        host = re.sub(r"^https?://", "", host)
        if host:
            return host
    return "Chefkoch"


def download_image(url, dst):
    """Lädt das Bild mit Browser-Header herunter."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            ctype = r.headers.get("Content-Type", "")
            print("  Bild heruntergeladen: %s (%d B, %s)" % (url, len(data), ctype))
    except urllib.error.HTTPError as e:
        print("  Fehler beim Download: HTTP %d" % e.code, file=sys.stderr)
        return False
    except Exception as e:
        print("  Fehler beim Download: %s" % e, file=sys.stderr)
        return False
    with open(dst, "wb") as f:
        f.write(data)
    return True


def ensure_baseline(path, max_dim=800, quality=90):
    """Skalziert auf max_dim px und schreibt Baseline-JPEG.

    - Bild ist schon Baseline und <= max_dim: unverändert.
    - Bild ist progressiv/WebP zu groß: skaliert + Baseline-JPEG.
    """
    with Image.open(path) as im:
        fmt = im.format
        w, h = im.size
        dim = max(w, h)
        if fmt in ("JPEG",) and dim <= max_dim:
            # Baseline-Check
            is_baseline = im.info.get("baseline", True)
            if is_baseline:
                print("  Bild OK: Baseline, %d px (<= %d), unverändert." % (dim, max_dim))
                return False
            print("  Bild progressiv: skaliere + Baseline.")
            im = im.convert("RGB")
        elif fmt not in ("JPEG",):
            im = im.convert("RGB")
            print("  Bild %s -> konvertiere." % fmt)
        nw, nh = int(max_dim * w / dim), int(max_dim * h / dim)
        im = im.resize((nw, nh), Image.LANCZOS)
        im.save(path, "JPEG", quality=quality)
        print("  skaliert: %d -> %d px, Baseline-JPEG (q=%d)." % (dim, max(nw, nh), quality))
        return True
    return True


def normalize_ingredients(recipe):
    """Bereinigt `recipeIngredient`-Strings (Mengen + Zutat).

    - Mengenangabe von Zutat trennen (z. B. "300 g Möhren").
    - Mengenplural-Notationen auflösen: "Scheibe/n" -> "Scheibe".
    - Alle Klammern entfernen: "Möhren(n)", "Ei(er)", "Margarine (oder Butter)",
      "(am besten Nacken)", "(reif)".

    Achtung: Die Mengeneinheit muss als eigenes Wort erkannt werden, damit z. B.
    "gelbe" nicht zu Menge "g" + Zutat "elbe" zerlegt wird.
    """
    # Mengeneinheiten als eigenständige Wörter (mit Wortgrenze), z. B. „g" in „gelb".
    UNIT = r"\b(?:g|kg|ml|l|EL|TL|Stk|Scheibe|Stück|Bd|Bund|Pck|Gl)\b\.?"
    out = []
    for ing in recipe.get("recipeIngredient", []):
        text = ing.strip()
        if not text:
            continue
        # Trenne Mengenangabe von Zutat (z. B. "300 g Möhren" / "1 Avocado")
        match = re.match(r"^(\d+(?:[.,]\d+)?\s*%s)?\s*(.+)$" % UNIT, text)
        if match and match.group(1):
            amount, zutat = match.group(1).strip(), match.group(2).strip()
        else:
            amount, zutat = "", text

        # Mengenplural: "Scheibe/n" -> "Scheibe"
        zutat = re.sub(r"/n", "", zutat)
        # Alle Klammern entfernen (Variablen, Alternativen, Beschreibungen):
        # "Möhren(n)", "Ei(er)", "Margarine (oder Butter)", "(am besten Nacken)", "(reif)".
        # Hinweis: Es werden alle Klammern-zeichen entfernt, nicht nur ausgewogene Paare —
        # das vermeidet ein „)"-Überbleibsel bei verschachtelten Klammern wie „((6 Stück))".
        zutat = re.sub(r"[()]", "", zutat)
        # Doppelte Leerzeichen zusammenziehen.
        zutat = re.sub(r"\s+", " ", zutat).strip()

        if amount:
            out.append("%s %s" % (amount, zutat))
        else:
            out.append(zutat)
    return out


def normalize_steps(recipe):
    """Extrahiert Schritt-Texte aus `recipeInstructions` (HowToSection/HowToStep)."""
    out = []
    instructions = recipe.get("recipeInstructions", [])
    if not instructions:
        return out
    # Oft ein HowToSection mit itemListElement[]
    for section in instructions:
        if isinstance(section, dict):
            items = section.get("itemListElement", [])
            if not items and "text" in section:
                items = [section]
        else:
            items = [section]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "HowToStep":
                out.append(item.get("text", "").strip())
            elif isinstance(item, str) and item.strip():
                out.append(item.strip())
    return [s for s in out if s]


def diet_names(recipe):
    """Wandelt `suitableForDiet` in eine lesbare Allergen-/Diet-Liste.

    Nur die klassischen Allergene/Ernährungsetiketten, die dem Format
    (`#gut` / Allergene-Zeile) entsprechen. `suitableForDiet` ist ein URI oder
    eine Liste von DietaryRequirements.
    """
    import urllib.parse

    def clean_uri(s):
        # Entferne URI-Präfix (z. B. "https://schema.org/VegetarianDiet") -> "VegetarianDiet"
        s = s.split("#", 1)[-1]
        try:
            s = urllib.parse.urlsplit(s).path.lstrip("/")
        except Exception:
            s = s.split("://", 1)[-1].split("/", 1)[-1]
        return s

    val = recipe.get("suitableForDiet")
    if val is None:
        return []
    if isinstance(val, str):
        val = [clean_uri(val)]
    if isinstance(val, list):
        names = []
        for v in val:
            if isinstance(v, dict):
                names.append(clean_uri(v.get("name", v.get("@id", ""))))
            else:
                names.append(clean_uri(str(v)))
        val = names
    else:
        val = [clean_uri(str(val))]

    # Auf Allergene / Ernährungsetikette filtern
    known = {"allergens": ("Gluten", "Eier", "Milch", "Fisch", "Schalenfrüchte",
                           "Sojafutter", "Senf", "Sulfit", "Krebstiere", "Nüsse",
                           "Sesamsamen", "Weizen", "Erdnuss", "Laktose"),
             "diet": ("Vegetarisch", "Vegan", "Laktosefrei", "Glutenfrei",
                      "Kalorienarm", "Low Carb", "Diabetiker", "Zöliakie",
                      "Fruktoseunverträglichkeit", "Rohkost")}
    # Zusätzliche Zuordnungen für Schema.org-Diet-Typen (z. B. "VegetarianDiet" -> "Vegetarisch")
    # Keys in Kleinbuchstaben (low ist schon lowercased).
    diet_aliases = {
        "vegetariandiet": "Vegetarisch",
        "vegetarian": "Vegetarisch",
        "vegandiet": "Vegan",
        "vegan": "Vegan",
        "diabeticdiet": "Diabetiker",
        "diabetiker": "Diabetiker",
        "lowfatdiet": "Low Carb",
        "lowfat": "Low Carb",
        "glutenfree": "Glutenfrei",
        "glutenfreediet": "Glutenfrei",
        "lowcarb": "Low Carb",
        "ketodiet": "Low Carb",
        "dairyfreediet": "Laktosefrei",
    }
    out = []
    for v in val:
        v = v.strip()
        if not v:
            continue
        low = v.lower()
        # Zuerst direkte Zuordnung (inkl. Schema.org-Diet-Typen)
        if low in diet_aliases:
            out.append(diet_aliases[low])
            continue
        matched = False
        for grp, words in known.items():
            for w in words:
                wl = w.lower()
                # Wortgrenzen: „Gluten" darf nicht mit „Glutenfrei" zusammengeführt werden.
                # Bindestrich, Leerzeichen oder camelCase-Trennung gelten als Wortgrenze.
                m = re.search(r"(^|[^a-z0-9])" + re.escape(wl) + r"([^a-z0-9])", low)
                if m:
                    out.append(w)
                    matched = True
                    break
            if matched:
                break
        # Sonst als Ernährungs-/Diät-Label behalten
        if not matched and v not in ("", "VegetarianDiet", "VeganDiet"):
            out.append(v)
    return out


def build_markdown(recipe, name, image_url, original_name=None, source_url="https://www.chefkoch.de", source_name=None, author_name=None):
    """Erzeugt die Markdown-Datei aus den extrahierten Feldern."""
    original_name = original_name or recipe.get("name", name)

    # Titel bereinigen: „... von <Autor>" entfernen (z. B. „... von Stolperfee30").
    title = recipe.get("name", name)
    if " von " in title:
        title = title.split(" von ", 1)[0].strip()

    date = recipe.get("datePublished")
    date_str = datetime.fromisoformat(date).strftime("%d.%m.%Y") if date else "—"

    _yield = recipe.get("recipeYield", [])
    if isinstance(_yield, list):
        yield_str = " / ".join(str(y) for y in _yield)
    else:
        yield_str = str(_yield)

    total_time = recipe.get("totalTime")
    prep = recipe.get("prepTime")
    cook = recipe.get("cookTime")

    # Zeitformatierung: PT1H30M -> 1 Std. 30 Min.
    def fmt_time(pt):
        if not pt:
            return "—"
        try:
            # ISO-8601: PT1H30M -> 1h 30m, PT40M -> 40m
            h = int(re.search(r"(\d+)H", pt or "").group(1)) if "H" in (pt or "") else 0
            m = int(re.search(r"(\d+)M", pt or "").group(1))
            seconds = h * 3600 + m * 60
        except Exception:
            return "—"
        parts = []
        if h:
            parts.append("%d Std." % h)
        if m:
            parts.append("%d Min." % m)
        return " · ".join(parts) if parts else "—"

    # Schwierigkeit aus keywords/typ ableiten (optional, sonst —)
    difficulty = "—"
    keywords = recipe.get("keywords", "")
    if isinstance(keywords, list):
        keywords = ", ".join(str(k) for k in keywords)
    if "leichte küche" in str(keywords).lower() or "einfach" in str(keywords).lower():
        difficulty = "Leicht"
    elif "schwierig" in str(keywords).lower():
        difficulty = "Schwer"
    else:
        difficulty = "Normal"

    allergens = diet_names(recipe)
    allergen_str = " · ".join(allergens) if allergens else "—"

    author_name = author_name or resolve_author(recipe, html)

    lines = []
    lines.append("# %s" % title)
    lines.append("")
    lines.append("- **Rezept:** %s" % original_name)
    lines.append("- **Autor:** %s" % author_name)
    lines.append("- **Quelle:** [%s](%s)" % (source_name, source_url))
    lines.append("- **Bewertung:** —")
    lines.append("- **Arbeitszeit:** %s · **Gesamtzeit:** %s · **Schwierigkeit:** %s"
                  % (fmt_time(prep), fmt_time(total_time), difficulty))
    lines.append("- **Für:** %s Portionen · **Erstellt:** %s"
                  % (int(float(re.sub(r"[^0-9,]", "", yield_str.split(" / ")[0])) if yield_str else 4), date_str))
    lines.append("- **Allergene:** %s" % allergen_str)
    lines.append("")
    lines.append("![Vorschau](../images/%s-img.jpg)" % name)
    lines.append("")
    lines.append("## Zutaten")
    lines.append("")
    for ing in normalize_ingredients(recipe):
        lines.append("- %s" % ing)
    lines.append("")
    lines.append("## Zubereitung")
    lines.append("")
    for i, step in enumerate(normalize_steps(recipe), 1):
        lines.append("%d. %s" % (i, step))
    lines.append("")
    lines.append("## Kommentare")
    lines.append("")
    lines.append("(noch keine)")
    lines.append("")
    lines.append("## Eigene Bemerkungen")
    lines.append("(noch keine)")
    lines.append("")

    # Nährwerte-Nachweis (wenn vorhanden)
    nutrition = recipe.get("nutrition") or {}
    if nutrition and nutrition.get("calories"):
        cal = nutrition.get("calories", "")
        prot = nutrition.get("proteinContent", "")
        fat = nutrition.get("fatContent", "")
        carbs = nutrition.get("carbohydrateContent", "")
        parts = []
        if cal:
            parts.append(cal)
        if prot:
            parts.append(prot)
        if fat:
            parts.append(fat)
        if carbs:
            parts.append(carbs)
        if parts:
            lines.append("---")
            lines.append("")
            lines.append("*Nährwerte (pro Portion): %s.*" % " · ".join(parts))
            lines.append("")

    return "\n".join(lines)


def add_index_row(name, title, source_url, source_name="Chefkoch", author_name="—"):
    """Fügt eine Index-Zeile an (Dry-Run: nur in Memory; --write: in Datei).

    Format folgt der bestehenden Tabelle. Icon = ❓ (kein Bewertungstags).
    Quelle/Autor = Name der tatsächlich genutzten Quelle (fix-chefkoch-import).
    """
    img = "<img src=\"images/%s-img.jpg\" alt=\"%s\" style=\"width:100px;height:auto;\" />" % (name, title)
    link = "[%s](rezepte/%s.md)" % (title, name)
    row = "| ❓    | %s | %s | %s | [%s](%s) |" % (img, link, source_name, source_name, source_url)
    return row


def main():
    parser = argparse.ArgumentParser(description="Importiert ein Rezept aus chefkoch.de über JSON-LD.")
    parser.add_argument("--url", help="URL des Rezepts auf chefkoch.de (wird heruntergeladen)")
    parser.add_argument("--html", help="Pfad zu Rohdaten-HTML (oder HTML-Inhalt per stdin, wenn '-'")
    parser.add_argument("--rohdaten", help="Pfad zum Rohdaten-HTML (Standard: rohdaten/[name].html)")
    parser.add_argument("--index", action="store_true", help="Index-Eintrag ergänzen")
    parser.add_argument("--write", action="store_true", help="Dateien aufschreiben (ohne Flag: Dry-Run)")
    args = parser.parse_args()

    source_url = args.url
    if args.html:
        if args.html == "-":
            html = sys.stdin.read()
        else:
            with open(args.html, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()
    elif args.rohdaten:
        with open(args.rohdaten, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    elif args.url.startswith("http"):
        import urllib.request as req
        try:
            r = req.Request(args.url, headers={"User-Agent": USER_AGENT})
            with req.urlopen(r, timeout=30) as r2:
                html = r2.read().decode("utf-8", "replace")
        except Exception as e:
            print("Fehler beim Abrufen der URL: %s" % e, file=sys.stderr)
            sys.exit(1)
    elif args.url:
        with open(args.url, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    else:
        print("Fehler: --url oder --html fehlt.", file=sys.stderr)
        sys.exit(1)

    recipe = extract_jsonld_recipe(html)
    if not recipe:
        print("Fehler: Kein JSON-LD Rezept gefunden.", file=sys.stderr)
        sys.exit(1)

    # Titel bereinigen: „... von <Autor>" entfernen (z. B. „... von Stolperfee30").
    # Der Dateiname + Index-Link verwenden den bereinigten Titel; „Rezept:"-Zeile
    # behält den vollen Originaltitel (inkl. Autor).
    title = recipe.get("name", "").strip()
    original_name = title
    if " von " in title:
        title = title.split(" von ", 1)[0].strip()
    name = resolve_name(normalize_name(title))

    # Quelle des Rezepts = Name der tatsächlich genutzten Quelle (nicht „Chefkoch").
    # 1) Name, wenn leicht zu ermitteln; sonst Domain der URL.
    source_name = resolve_source_name(html, args.url)

    # Autor: JSON-LD -> HTML-Meta -> "-".
    author_name = resolve_author(recipe, html)

    image_url = extract_og_image(html)

    if not image_url:
        print("Fehler: Kein og:image gefunden.", file=sys.stderr)
        sys.exit(1)

    src_file = args.rohdaten or os.path.join(ROOT, "rohdaten", normalize_name(title) + ".html")
    img_dst = os.path.join(IMAGES_DIR, name + "-img.jpg")
    md_dst = os.path.join(REZEPTE_DIR, name + ".md")

    # Quelle-URL für den Index-Link (aus og:url / canonical / JSON-LD url).
    source_url = extract_recipe_url(html)

    print("Rezept:   %s" % original_name)
    print("Dateiname: %s" % name)
    print("Bild:      %s" % image_url)
    print("  Quelle:  %s (%s)" % (source_name, source_url))
    print()

    if not args.write:
        print("Dry-Run: Es wird NICHT geschrieben. Mit --write ausführen.")
        print("  Ziel: %s" % md_dst)
        print("  Ziel: %s" % img_dst)
        if args.index:
            print("  Index-Zeile:")
            print("  " + add_index_row(name, title, source_url, source_name, author_name))
        return

    # Bild herunterladen
    tmp_img = "/tmp/%s.jpg" % name
    if not download_image(image_url, tmp_img):
        sys.exit(1)

    # Skaliere + Baseline
    ensure_baseline(tmp_img, max_dim=800, quality=90)

    ok = copy_file(tmp_img, img_dst)
    if ok:
        md = build_markdown(recipe, name, image_url, original_name, source_url, source_name, author_name)
        with open(md_dst, "w", encoding="utf-8") as f:
            f.write(md)
        print("\n  Rezept-Datei geschrieben: %s" % md_dst)

    if args.index:
        row = add_index_row(name, title, source_url, source_name, author_name)
        # Keine Leerzeile vor der neuen Zeile: die kommt direkt unter der letzten
        # Tabellenzeile. Prüfe, ob die Datei (außer dem letzten Zeilencode) leer ist
        # bzw. ohne Endzeilencode endet — sonst nur die neue Zeile anhängen.
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        trailing = "" if content.endswith("\n") else "\n"
        with open(INDEX_FILE, "a", encoding="utf-8") as f:
            f.write(trailing + row + "\n")
        print("  Index-Zeile ergänzt: %s" % INDEX_FILE)

    print("\nFertig. Kein Bewertungstags beim Import (Regel 7).")


def copy_file(src, dst):
    if not os.path.exists(src):
        print("Fehler: Quelldatei nicht gefunden: %s" % src, file=sys.stderr)
        return False
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, "rb") as fin, open(dst, "wb") as fout:
            fout.write(fin.read())
        print("  kopiert: %s -> %s (%d B)" % (os.path.basename(src), os.path.basename(dst), os.path.getsize(dst)))
        return True
    except (OSError, IOError) as e:
        print("Fehler beim Kopieren %s -> %s: %s" % (src, dst, e), file=sys.stderr)
        return False


if __name__ == "__main__":
    main()
