# CLAUDE.md — Rezeptesammlung

Dieses Projekt ist ein **dual-purpose** Setup: Es wird wie eine statische Website auf **GitHub Pages** veröffentlicht (nur die Inhalte in `docs/` werden publiziert), **wird aber lokal in Obsidian** bearbeitet (`~/.obsidian/`, lokal, nicht in Git). Die Dateien folgen den Regeln unten, nicht den Obsidian-Voreinstellungen.

## Ziel
Ein KI-Agent (Nyx) extrahiert Rezepte aus URLs und legt sie strukturiert ab: eine Markdown-Datei pro Rezept + ein Vorschaubild.

## Namenskonvention
- **Rezept-Markdown-Datei:** Kurzer Dateiname aus dem Rezept-Titel (alphanumerisch, Kleinbuchstaben, `-` als Trennzeichen). → `docs/rezepte/[name].md`
- **Vorschaubild:** Rezeptname + `-img` + Suffix. → `docs/images/[name]-img.jpg`

## Speicherorte
- Rezepte (`.md`) → `docs/rezepte/`
- Vorschaubilder → `docs/images/`
- Hauptseite/Übersicht → `docs/index.md`
- Projekt-Notizen → `project/`
- Rohdaten (noch nicht importiert) → `rohdaten/`

## Rezept-Markdown-Format
- Kopfzeile mit Titel
- Metadaten-Bulleted-Liste: Rezept, Quelle (als Link), Bewertung, Arbeits-/Gesamtzeit, Schwierigkeit, Portionen, Erstellungsdatum, Allergene
- Vorschaubild als Bild (`../images/[name]-img.jpg`)
- Abschnitte: Zutaten, Zubereitung, Kommentare, **Eigene Bemerkungen**
- Abschnitt **„Eigene Bemerkungen"** initiale Zeile `(noch keine)`
- Referenzformat: `docs/rezepte/birnenschmarrn.md`

## Import-Regeln (Rezept aus URL)
1. Rezept aus URL extrahieren (Zutaten, Zubereitung, Zeiten, Allergene).
2. **Portionierung auf 4 Personen** (Original oft für 2).
3. Vorschaubild nach `docs/images/[name]-img.jpg` kopieren.
3a. **Bildquellen-Reihenfolge:** 1) Die Quelle einlesen (eine URL oder ein Clipping, ggf. auch ein PDF). 2) Wenn sich dort ein passendes Bild findet, dann dieses Bild als Vorschau nehmen. 3) Erst wenn das nicht gelingt: **Mich fragen**, ob ich ein Bild beisteuern kann — dann lege ich es zu den Rohdaten (`rohdaten/`).
3b. **Rohdaten nur nach Aufforderung benutzen.** Bilder aus `rohdaten/` werden **nie** von selbst gesucht — nur, wenn ich (Nyx) nachfrage und Michael ein Bild bereitgestellt hat.
3c. **Keine automatische Web-Suche.** Eine Websuche nach einem passenden Bild führe ich **nur** nach ausdrücklicher Aufforderung von Michael durch.
4. WebP/VP8-Bilder ggf. mit `ffmpeg` in echtes JPEG (baseline) konvertieren.
5. Markdown-Datei unter `docs/rezepte/` anlegen.
6. Index (`docs/index.md`) aktualisieren.
7. **Kein Bewertungstags beim Import.** Neue Rezepte bekommen beim Import standardmäßig **kein** Bewertungstags (`#gut`, `#neu`, …) und landen damit im Index als ❓. Der **User** ist Autorität für das Tag: Er setzt es selbst nach dem Probieren in der Rezept-Datei (`#gut` = bewährt → ✅, `#neu` = noch nicht ausprobiert → ❓). **Nyx ergänzt danach nur das Icon im Index** (Dry-Run, dann nach Bestätigung) — er setzt keine Tags eigenständig.
8. **Scraping/Hinweise:** `curl` mit normalem Browser-Ursprung (`Mozilla/5.0`) funktioniert bei chefkoch.de, shibaskitchen.de und emmikochteinfach.de. **REWE (`rewe.de`) blockiert direktes Scraping** (WAF/Bot-Schutz), aber Rezepte sind über **WebClipper-Clipping** importierbar (Clipping in `Clippings/`, daraus Rezept rekonstruieren). Proseg-basierte Seiten (z. B. shibaskitchen) haben oft kein JSON-LD → Rezept aus Blogtext rekonstruieren. Details je Quelle: `project/sites.md`.

## Index (`docs/index.md`)
-  Spalten: **Rezept** (Icon) | **Vorschau** | **Titel** (Link zur Rezept-Datei) | **Autor** | **Quelle** (Link)
- **Titel als Link:** `[Titel](rezepte/[name].md)` — verlinkt zum jeweiligen Rezept.
- **Icon nach Tags:** `#gut` → ✅, kein Tag/`#neu` → ❓
- Vorschau-Bild: `<img src="images/[name]-img.jpg" alt="..." style="width:100px;height:auto;" />`
- **Sortierung der Tabelle:** Nach dem **Anzeigentext** des Titels (Link-Text des Markdown-Links), nicht nach der Ziel-Datei. Deutsche Wörterbuch-Reihenfolge: Umlaute ä/ö/ü als ae/oe/ue. De-facto-Regel: Bei **Neuimport** chronologisch (neue Zeile ans Ende anhängen); **Sortierung der Tabelle selbst ist ein separater Vorgang** (Skript `bin/index-sort.py`).
- **Sortierung ist eine Erfolg-Änderung:** Eine alphabetische Sortierung der Tabelle ist eine **erfolgreiche Änderung** → darf **nie** automatisch/ohne ausdrückliche Aufforderung ausgeführt werden. Nur manuell: (a) von Nyx, **nach** ausdrücklicher Aufforderung des Users, oder (b) vom User selbst per Skript.

## Projekt-Regeln
- `project/index-regeln.md` — Index-Regeln
- `project/Konzeption.md` — Besondere Tags (Icons/Tags)
- `project/Namenskonventionen.md` — Dateinamen
- `project/Struktur.md` — Verzeichnisstruktur
- `project/sites.md` — Website-Status: welche Quellen erfolgreich importiert, welche problematisch sind

## Veröffentlichung (GitHub Pages)
- Das Projekt wird als **statische Website** über **GitHub Pages** veröffentlicht.
- **Veröffentlichung ist eingerichtet und erfolgt automatisch** nach `git push` (GitHub Actions / Pages-Regel).
- **Ich muss nichts manuell deployen** — nach `git commit` + `git push` wird die neue Version automatisch veröffentlicht.
- Rohdaten (noch nicht importiert) → `rohdaten/`

## Sonstige Regeln
Anweisung: fazit 
1. Die den Inhalt der aktuellen session zusammenfassen.
2. Informationen über den Beginn der Sitzung und die Erstellung des Fazit müssen enthalten sein. 
3. Den Inhalt abspeichern in einer Datei session-logs/[YYYY]/[MM]/[YYYY-MM-DD].md Das Verzeichnis session-logs im Hauptverzeichnis des Projekts nutzen.
4. Falls diese Datei schon existiert: Den Inhalt am Ende der Datei anhängen.
5. Kein automatisches Fazit - nur nach Aufforderung,