#!/usr/bin/env python3
"""
index-sort.py — Sortiert die Rezept-Übersichts-Datei (docs/index.md) alphabetisch.

Sortierung:
  - Sortiert wird die „Titel"-Spalte nach dem Anzeigentext (Link-Text) des Markdown-Links.
    Beispiel: [Birnenschmarrn (Ofenvariante)](rezepte/birnenschmarrn.md) → sortiert nach
    „Birnenschmarrn (Ofenvariante)", NICHT nach der Ziel-Datei „birnenschmarrn".
  - Deutsche Wörterbuch-Reihenfolge: Umlaute ä/ö/ü werden als ae/oe/ue behandelt
    (z. B. „Käse" vor „Keim").

Hinweis zur chronologischen Reihenfolge: Diese Projekt-Regel (Neue Einträge ans Ende)
gilt beim Import. Beim Sortieren wird rein alphabetisch sortiert; ein neu hinzugefügter
Eintrag landet dann in seiner korrekten alphabetischen Position.

Aufbau:
  - Die Tabelle wird sauber neu aufgebaut (ausgerichtete Spalten).
  - Alle Daten werden erhalten: Icon, Vorschaubild (vollständiger <img>-Tag),
    Titel-Link, Autor, Quelle.

Aufruf:
    python3 bin/index-sort.py [--write]

Ohne --write läuft der Sort-Vorgang im Dry-Run-Modus und ändert nichts.
"""

import argparse
import os
import re
import sys

# Pfad relativ zum Projekt-Wurzelverzeichnis.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_FILE = os.path.join(ROOT, "docs", "index.md")

COLS = ["Icon", "Bild", "Titel", "Autor", "Quelle"]


def de_dict_key(text):
    """Sortier-Schlüssel für die deutsche Wörterbuch-Reihenfolge.

    Umlaute werden auf die Nachbarn zurückgeführt (ä→ae, ö→oe, ü→ue),
    damit „Käse" vor „Keim" kommt. Klein-/Großschreibung wird ignoriert.
    """
    key = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    return key.lower()


def parse_rows(path):
    """Parst die Datenseiten der Tabelle aus index.md.

    Gibt eine Liste von Dictionaries zurück:
      {icon, img, title, target, author, source}
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().split("\n")

    rows = []
    header_done = False
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        if not header_done:
            header_done = True  # erste Tabellenzeile = Header
            continue
        # Trennzeile (nur Bindestriche) überspringen
        if all(re.match(r"^-\s*$", c) for c in cells):
            continue
        # Datenzeile muss ein Vorschaubild in Spalte 1 haben
        if not cells[1].startswith("<img"):
            continue
        # Titel als Markdown-Link [Anzeigentext](rezepte/name.md)
        m = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", cells[2])
        if not m:
            continue
        rows.append({
            "icon": cells[0],
            "img": cells[1],
            "title": m.group(1),
            "target": m.group(2),
            "author": cells[3],
            "source": cells[4],
        })
    return rows


def sort_rows(rows):
    """Sortiert nach dem Titel (Anzeigentext), deutsche Reihenfolge, stabil."""
    return sorted(rows, key=lambda r: de_dict_key(r["title"]))


def build_table(rows):
    """Baute eine sauber formatierte Tabelle (Header, Trennzeile, Datenseiten)."""
    # Spaltenbreiten (linksbündig), keyed by the header name (COLS).
    # Icon auf feste Breite. ROW_KEYS enthält die passenden row-Schlüssel.
    ROW_KEYS = ["icon", "img", "title", "author", "source"]
    widths = {}
    for i, h in enumerate(COLS):
        widths[h] = max((len(r[ROW_KEYS[i]]) for r in rows), default=0)
    widths["Icon"] = 4  # „❓  "

    def fmt(col):
        return col.ljust(widths[col])

    header = "| " + " | ".join(fmt(c) for c in COLS) + " |"
    sep = "| " + " | ".join("-" * max(widths[c], 10) for c in COLS) + " |"
    data = []
    for r in rows:
        row = "| " + " | ".join([
            r["icon"],
            r["img"],
            "[%s](%s)" % (r["title"], r["target"]),
            r["author"],
            r["source"],
        ]) + " |"
        data.append(row)
    return header, sep, data


def render(table):
    """Verschmilte Header, Trennzeile und Datenseiten zu Markdown-Text."""
    header, sep, data = table
    body = "\n".join(data)
    return header + "\n" + sep + "\n" + body + "\n"


def preview(rows):
    """Gibt die neue (sortierte) Reihenfolge der Titel im Terminal aus."""
    print("Neue Reihenfolge (Titel, sortiert):")
    for i, r in enumerate(rows, 1):
        print("  %2d. %s" % (i, r["title"]))


def main():
    parser = argparse.ArgumentParser(description="Sortiert die Rezept-Übersichts-Datei (docs/index.md) alphabetisch.")
    parser.add_argument("--write", action="store_true", help="Sortierung in der Index-Datei speichern")
    args = parser.parse_args()

    rows = parse_rows(INDEX_FILE)
    if not rows:
        print("Fehler: Keine Rezept-Datenseiten in %s gefunden." % INDEX_FILE, file=sys.stderr)
        sys.exit(1)

    sorted_rows = sort_rows(rows)
    preview(sorted_rows)
    print()
    print("Einträge: %d → %d" % (len(rows), len(sorted_rows)))

    old = render(build_table(rows))
    new = render(build_table(sorted_rows))

    if rows == sorted_rows:
        print("Index ist bereits alphabetisch sortiert. Nichts zu tun.")
        sys.exit(0)

    print("Änderungen: %d Einträge bewegen sich." % (len(rows) - 1))
    if args.write:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new)
        print("Schreibmodus: Index gespeichert (%s)." % INDEX_FILE)
    else:
        print("Dry-Run: Index wird NICHT gespeichert. Mit --write speichern.")


if __name__ == "__main__":
    main()
