# Skripte

Die Skripte helfen beim **manuellen Import** und der **Pflege** der Rezept-Sammlung.
Alle sind Python 3 und laufen aus dem Projekt-Wurzelverzeichnis.

> **Dry-Run-Standard:** Alle Skripte ändern **nichts**, bis du `--write` (bzw. bei
> `index-sort.py` das Schreiben) angibst. Ohne Flag zeigen sie nur an, was passieren
> würde. Ein Durchlesen der Ausgabe vor dem Speichern ist also immer möglich.

## Übersicht

Alle Skripte liegen im `bin/`-Verzeichnis.

| Skript | Zweck |
| --- | --- |
| `new-recipe.py` | Kopiert eine Rezept-Vorlage für einen manuellen Import |
| `index-check.py` | Prüft und pflegt `docs/index.md` (Icons, fehlende Einträge) |
| `index-sort.py` | Sortiert die Index-Tabelle alphabetisch |
| `scale-images.py` | Skalziert Vorschaubilder auf max. 800 px |

---

## 1. `new-recipe.py` — Rezept-Vorlage kopieren

Kopiert eine leere Rezept-Vorlage an die richtige Stelle, damit du nur noch den Inhalt
schreibst. Es formatiert und portiert **nicht** aus Rohdaten — das machst du selbst.

- Kopiert `template/vorlage-rezept.md` → `docs/rezepte/[name].md`
- Kopiert `template/Kochen.jpg` → `docs/images/[name]-img.jpg`
- Setzt den Bildlink in der neuen Datei
- Normalisiert den Dateinamen (Umlaute → ae/oe/ue, `ß` → ss, Trenner als `-`)

**Aufruf:**
```bash
python3 bin/new-recipe.py --name "Mein Rezept" [--write]
```
- `--write` : Dateien aufschreiben (ohne Flag: nur Dry-Run)
- Bei doppeltem Namen wird automatisch eine Nummer angehängt (`name-1`, `name-2`, …)

Danach musst du selbst den Index-Eintrag in `docs/index.md` ergänzen. **Kein Bewertungstags**
setzen (das machst du nach dem Probieren).

---

## 2. `index-check.py` — Index prüfen und pflegen

Prüft `docs/index.md` gegen die Rezept-Dateien und die Vorschaubilder.

**Was es prüft:**
- Rezept-Dateien, die im Index verlinkt sind, aber auf der Festplatte fehlen
- Vorschaubilder: Existenz **und** korrekter Name (`[rezeptname]-img.jpg`)
- Icons im Index (`✅`/`❓`) stimmen mit den Tags in den Rezept-Dateien überein
- Optional: Rezepte, die auf der Festplatte liegen, aber noch **nicht** im Index sind

**Aufruf:**
```bash
python3 index-check.py [--write] [--add]
```
(Direkt aus dem Projekt-Wurzelverzeichnis aufrufbar.)

- `--write` : Korrigiert Icon-Fehler in der Index-Datei automatisch.
  Die **Rezept-Dateien bleiben Autorität** — nur das Icon im Index wird nachgeführt.
- `--add` : Hängt alle Rezepte an, die im Index noch fehlen, als neue Zeile an.
  (Autor/Quelle werden aus den Rezept-Dateien übernommen; leer, wenn dort keine Infos.)
  **Nur anhängen, nicht sortieren.**

> ⚠️ `--write` mit `--add` schreibt die fehlenden Einträge. Prüfe vorher die Ausgabe,
> dass Autor/Quelle korrekt sind. Neue Rezepte landen ans Ende.

---

## 3. `index-sort.py` — Index alphabetisch sortieren

Sortiert die Tabellenzeilen nach dem **Anzeigetext** des Titels (dem Link-Text des
Markdown-Links), nicht nach der Ziel-Datei. Deutsche Wörterbuch-Reihenfolge: Umlaute als
ae/oe/ue (z. B. „Käse" vor „Keim"). Alle Daten (Icon, Bild, Autor, Quelle) bleiben erhalten.

**Wichtig:** Eine alphabetische Sortierung ist eine **Erfolg-Änderung** — darf **nie**
automatisch ausgeführt werden.

**Aufruf:**
```bash
python3 bin/index-sort.py [--write]
```
- Ohne `--write` : Dry-Run, zeigt die neue Reihenfolge an, ändert nichts.
- Mit `--write` : Speichert die neue (alphabetische) Reihenfolge.

---

## 4. `scale-images.py` — Vorschaubilder skalieren

Skalziert alle JPGs in `docs/images/` proportional auf max. 800 px (längere Seite),
Baseline-JPEG, Qualität 90. Vorschaubilder werden quadratisch auf 800×800 skaliert.
Bilder, die schon ≤ 800 px sind, bleiben unverändert.

**Aufruf:**
```bash
python3 bin/scale-images.py [--max 800] [--check]
```
- `--check` : Nur prüfen, ob Bilder zu groß sind — **nichts schreiben**.
- `--max 800` : Max. Abmessung (Default 800 px).
- Ohne Flag : Skaliert alle > 800 px neu (kein `--write` nötig — das Skalieren ist kein
  Erfolgsschritt, sondern Pflege).

**Tipp:** Nutze zuerst `--check`, um zu sehen, welche Bilder zu groß sind, dann ohne Flag
skalieren.

---

## Häufige Abläufe

**Neues Rezept manuell importieren:**
```bash
python3 bin/new-recipe.py --name "Mein Rezept"
# Inhalt selbst in docs/rezepte/Mein-Rezept.md schreiben
python3 bin/index-check.py --add --write
```

**Nach dem Probieren bewähren (Tag setzen + Icon im Index korrigieren):**
```bash
# In der Rezept-Datei: - **Bewertung:** #gut
python3 index-check.py --write
```

**Index alphabetisch sortieren (nach ausdrücklicher Aufforderung):**
```bash
python3 bin/index-sort.py --write
```

**Alle Vorschaubilder auf 800 px prüfen:**
```bash
python3 bin/scale-images.py --check
```
