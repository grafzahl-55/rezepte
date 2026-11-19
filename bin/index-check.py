#!/usr/bin/env python3
"""
index-check.py — Prüft die Rezept-Übersichts-Datei (docs/index.md).

Was wird geprüft:
  1. Für jedes Rezept in docs/rezepte/ werden die Tags (#gut, #neu, ...) gelesen.
  2. Die Tabelle in docs/index.md wird Zeile für Zeile geprüft:
       - Der Verweis auf die Rezept-Datei (Original) existiert.
       - Der Verweis auf das Vorschaubild (images/...) existiert und passt.
       - Das Icon (✅/❓) stimmt mit den Tags der Rezept-Datei überein.
  3. Alle gefundenen Fehler/Probleme werden angezeigt (nur Anzeige, keine Änderung).

Aufruf:
    python3 project/index-check.py [--write]

Mit --write werden die gefundenen Icon-Fehler in docs/index.md korrigiert
(die Rezept-Dateien bleiben Autorität). Ohne --write läuft der Check im
Dry-Run-Modus und ändert nichts.
"""

import argparse
import os
import re
import sys

# Pfad relativ zum Projekt-Wurzelverzeichnis.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES_DIR = os.path.join(ROOT, "docs", "rezepte")
INDEX_FILE = os.path.join(ROOT, "docs", "index.md")

# Tag → Icon
TAG_ICON = {
    "gut": "✅",
    "neu": "❓",
    "untested": "❓",
}


def read_icon_map(recipes_dir):
    """Liest für jedes Rezept in recipes_dir die Tags und das zugehörige Icon."""
    icon_map = {}
    for fname in sorted(os.listdir(recipes_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(recipes_dir, fname)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue
        icon = "❓"
        for tag, ic in TAG_ICON.items():
            if re.search(rf"^\s*#\s*{tag}\b", content, re.MULTILINE):
                icon = ic
                break
        icon_map[fname] = icon
    return icon_map


def parse_table_rows(index_path):
    """
    Parset die Tabellenzeilen aus index.md.
    Gibt eine Liste von Dictionaries zurück:
      {row, icon, img, link, author, source, recipe, title}
    """
    with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().split("\n")

    rows = []
    header_done = False
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if not header_done:
            header_done = True  # erste Tabellenzeile = Header
            continue
        if cells[0].startswith("Rezept") or cells[0] in ("❓", "✅") and cells[1].startswith("<img"):
            # Prüfe, ob es sich um eine Datenzeile handelt
            if not cells[1].startswith("<img"):
                # Zeile mit Header-Text
                header_done = True
                continue

        recipe = None
        title = None
        for c in cells:
            m = re.search(r"(rezepte/[^)]+\.md)", c)
            if m:
                recipe = m.group(1).replace("rezepte/", "")
                break
        if recipe:
            rows.append({
                "icon": cells[0],
                "img": None,
                "recipe": recipe,
                "author": cells[3] if len(cells) > 3 else "",
                "source": cells[4] if len(cells) > 4 else "",
                "title": cells[1] if cells[1].startswith("<img") else "",
            })
            # Vorschaubild-Url aus der img-Quelle extrahieren
            for c in cells:
                m = re.search(r'(images/[^"]+\.jpg)', c)
                if m:
                    rows[-1]["img"] = m.group(1)
                    break
        else:
            # Zeile ohne Rezept-Verweis (z. B. Trennzeile)
            continue
    return rows


def check_all(icon_map, rows, write=False):
    """Führt alle Checks durch und gibt Ergebnisse aus."""
    issues = []

    # 1. Rezept-Dateien, die im Index verlinkt, aber nicht existieren
    missing_recipes = []
    for r in rows:
        if r["recipe"] and not os.path.exists(os.path.join(RECIPES_DIR, r["recipe"])):
            missing_recipes.append(r)

    # 2. Vorschaubilder: Existenz + Namensübereinstimmung
    missing_images = []
    mismatched_images = []
    for r in rows:
        if not r["img"]:
            missing_images.append(r)
            continue
        # img enthält bereits den "images/"-Prefix; nur den Dateinamen für den Pfad verwenden
        img_name = os.path.basename(r["img"])
        img_path = os.path.join(ROOT, "docs", "images", img_name)
        if not os.path.exists(img_path):
            missing_images.append(r)
            continue
        # Erwarteter Dateiname: [rezeptname]-img.jpg (rezeptname ohne .md)
        expected = os.path.splitext(r["recipe"])[0] + "-img.jpg"
        if img_name != expected:
            mismatched_images.append(r)

    # 3. Icon-Prüfung: Tag in Rezept-Datei vs Icon im Index
    icon_mismatches = []
    for r in rows:
        expected_icon = icon_map.get(r["recipe"], "❓")
        if r["icon"] != expected_icon:
            icon_mismatches.append(r)

    # Ergebnisse zusammenstellen
    print("=" * 70)
    print("INDEX-PRÜFUNG: docs/index.md")
    print("=" * 70)
    print(f"Rezept-Dateien im Verzeichnis: {len(icon_map)}")
    print(f"Rezept-Verweise im Index:      {len(rows)}")
    print(f"Modus: {'Schreibmodus (--write)' if write else 'Dry-Run (nur Anzeige)'}")
    print("-" * 70)

    total_issues = 0

    print("\n[1] Fehlende Rezept-Dateien:")
    if missing_recipes:
        for r in missing_recipes:
            print(f"   FEHLER: {r['recipe']} existiert nicht")
            total_issues += 1
    else:
        print("   OK: Alle Rezept-Dateien existieren.")

    print("\n[2] Fehlende/fehllndige Vorschaubilder:")
    if missing_images:
        for r in missing_images:
            print(f"   FEHLER: Bild {r['img']} existiert nicht für {r['recipe']}")
            total_issues += 1
    if mismatched_images:
        for r in mismatched_images:
            print(f"   FEHLER: Bildname passt nicht: {r['img']} (erwartet {r['recipe']}-img.jpg)")
            total_issues += 1
    if not missing_images and not mismatched_images:
        print("   OK: Alle Vorschaubilder existieren und passen.")

    print("\n[3] Icon-Übereinstimmung (Tag vs Icon):")
    if icon_mismatches:
        for r in icon_mismatches:
            expected = icon_map.get(r["recipe"], "❓")
            print(f"   FEHLER: {r['recipe']} hat Icon {r['icon']} im Index, aber {expected} in der Rezept-Datei")
            total_issues += 1
    else:
        print("   OK: Alle Icons stimmen mit den Tags überein.")

    print("\n" + "=" * 70)
    print(f"GESAMT: {total_issues} Problem(e) gefunden.")
    print("=" * 70)

    # Automatische Korrektur im Schreibmodus
    if write and icon_mismatches:
        _fix_icons_in_index(icon_map, rows, icon_mismatches)

    return total_issues


def _fix_icons_in_index(icon_map, rows, mismatches):
    """Korrigiert die Icons in der Index-Datei basierend auf den Rezept-Tags."""
    fixed = len(mismatches)
    with open(INDEX_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().split("\n")

    # Build a lookup from filename -> row index (1-based line number)
    for r in rows:
        if r["recipe"] not in icon_map:
            continue
        expected = icon_map[r["recipe"]]
        # Find the row by matching the recipe filename in any cell (the link),
        # then replace the icon at position 0.
        for i, line in enumerate(lines):
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            for c in cells:
                if r["recipe"] in c:
                    cells[0] = expected
                    lines[i] = "| " + " | ".join(cells)
                    break

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nSchreibmodus: {fixed} Icon(e) in {INDEX_FILE} korrigiert.")


def main():
    parser = argparse.ArgumentParser(description="Prüft die Rezept-Übersichts-Datei (docs/index.md).")
    parser.add_argument("--write", action="store_true", help="Icon-Fehler in der Index-Datei korrigieren")
    args = parser.parse_args()

    icon_map = read_icon_map(RECIPES_DIR)
    rows = parse_table_rows(INDEX_FILE)
    check_all(icon_map, rows, write=args.write)


if __name__ == "__main__":
    main()
