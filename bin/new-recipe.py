#!/usr/bin/env python3
"""
new-recipe.py — Kopiert eine Rezept-Vorlage für einen manuellen Import.

Manueller Rezept-Workflow:
  1. Rezepttext selbst in die Vorlage schreiben.
  2. Vorschaubild in template/Kochen.jpg tauschen.
  3. python3 bin/new-recipe.py --name "[name]" [--write]
  4. Index-Eintrag selbst ergänzen (kein Bewertungstags; nur Icon-Spiegel).

Das Skript tut:
  - Kopiert template/vorlage-rezept.md -> docs/rezepte/[name].md
  - Kopiert template/Kochen.jpg          -> docs/images/[name]-img.jpg
  - Setzt in der neuen Rezept-Datei den Bildlink: ![Vorschau](../images/[name]-img.jpg)

Es formatiert und portiert NICHT den Inhalt aus Rohdaten — den schreibst du selbst.

Aufruf:
    python3 bin/new-recipe.py --name "Mein Rezept" [--write]

Ohne --write läuft im Dry-Run-Modus und ändert nichts.
"""

import argparse
import os
import re
import sys

# Pfad relativ zum Projekt-Wurzelverzeichnis.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_MD = os.path.join(ROOT, "template", "vorlage-rezept.md")
TEMPLATE_IMG = os.path.join(ROOT, "template", "Kochen.jpg")
REZEPTE_DIR = os.path.join(ROOT, "docs", "rezepte")
IMAGES_DIR = os.path.join(ROOT, "docs", "images")


def normalize_name(name):
    """Bereinigt den Dateinamen: alphanumerisch, Kleinbuchstaben, - als Trennzeichen.

    Umlaute werden wie bei der Sortierung in ae/oe/ue umgewandelt, damit
    „Kaffeebrötchen" zu „kaffeebroetchen" wird (kein unleserliches „kaffeebr-tchen").
    „ß" (eszett) wird zu „ss" (kein unleserliches „hei-er").
    Bereits vorhandene Trennungs-Bindestriche (z. B. „chili-con-carne") bleiben erhalten.
    """
    name = name.strip().lower()
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    name = name.replace("ß", "ss")  # Eszett -> ss (z. B. „Soße" -> „Soese")
    name = re.sub(r"[^a-z0-9]+", "-", name)  # Leerzeichen/Punkte etc. -> Trennungs-Bindestrich
    name = re.sub(r"-{2,}", "-", name)  # Mehrfachbindestriche zusammen
    name = name.strip("-")
    return name


def name_exists(name):
    """Prüft, ob der Dateiname bereits eine Rezept-Datei oder ein Bild gibt."""
    if os.path.exists(os.path.join(REZEPTE_DIR, name + ".md")):
        return True
    if os.path.exists(os.path.join(IMAGES_DIR, name + "-img.jpg")):
        return True
    return False


def resolve_name(name):
    """Validiert und entgegengewählt, falls der Name doppelt belegt ist."""
    n = name
    i = 1
    while name_exists(n):
        n = "%s-%d" % (name, i)
        i += 1
    return n


def copy_file(src, dst):
    """Kopiert eine Datei und meldet Erfolg/Fehler. Erstellt Zielverzeichnis falls nötig."""
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


def insert_image_link(path, name, original_name=None):
    """Setzt den Bildlink in die Rezept-Datei und ersetzt den [name]-Platzhalter.

    Der Titel wird mit dem ORIGINAL-Namen ersetzt (z. B. „Marias Heißer Tomatensoße"),
    der Bildlink verwendet den normalisierten Namen (z. B. „marias-hei-er-tomatenso-e").
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    link = "![Vorschau](../images/%s-img.jpg)" % name
    title = original_name if original_name else name

    if "![Vorschau]" in content:
        # Bereits ein Link vorhanden (möglicherweise noch mit [name]-Platzhalter):
        # er wird ersetzt.
        content = re.sub(r"!\[Vorschau\]\([^)]*\)", link, content)
    else:
        # Kein Link vorhanden: einen nach den Metadaten-Einleitungen einfügen.
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("- **Rezept:**") or line.startswith("# "):
                lines.insert(i + 1, link)
                break
        else:
            lines.append("")
            lines.append(link)
        content = "\n".join(lines)

    # Titel ersetzen: „# [TITEL]" -> „# <Originaler Name>".
    content = content.replace("# [TITEL]", "# %s" % title)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  Bildlink gesetzt: %s" % link)


def render(rows):
    """Gibt die zu kopierenden Aktionen im Terminal aus."""
    for src, dst in rows:
        print("  %s -> %s" % (os.path.basename(src), os.path.basename(dst)))


def main():
    parser = argparse.ArgumentParser(description="Kopiert eine Rezept-Vorlage für einen manuellen Import.")
    parser.add_argument("--name", required=True, help="Dateiname des Rezepts (wird automatisch normalisiert)")
    parser.add_argument("--write", action="store_true", help="Dateien aufschreiben (ohne Flag: Dry-Run)")
    args = parser.parse_args()

    original_name = args.name
    name = resolve_name(normalize_name(args.name))
    print("Rezeptname: %s" % name)
    print("Original: %s" % original_name)
    print("Ziel-Datei: docs/rezepte/%s.md" % name)
    print("Ziel-Bild: docs/images/%s-img.jpg" % name)
    print()

    rows = [
        (TEMPLATE_MD, os.path.join(REZEPTE_DIR, name + ".md")),
        (TEMPLATE_IMG, os.path.join(IMAGES_DIR, name + "-img.jpg")),
    ]

    if not args.write:
        print("Dry-Run: Es wird NICHT geschrieben. Mit --write ausführen.")
        render(rows)
        return

    ok = True
    for src, dst in rows:
        ok = copy_file(src, dst) and ok

    if ok and os.path.exists(rows[0][1]):
        # insert_image_link braucht den ORIGINAL-Namen für den Titel-Tausch,
        # aber den normalisierten Namen für den Bildlink.
        insert_image_link(rows[0][1], name, original_name)
    else:
        print("Abgebrochen: Der Ziel-Rezeptpfad existiert nicht oder das Kopieren ist fehlgeschlagen.", file=sys.stderr)
        sys.exit(1)

    print("\nFertig. Jetzt: Index-Eintrag selbst in docs/index.md ergänzen (Icon ❓, kein Bewertungstags).")


if __name__ == "__main__":
    main()
