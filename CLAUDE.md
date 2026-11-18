# CLAUDE.md — Rezeptesammlung

Dieses Projekt ist eine **Rezeptesammlung**, die wie eine statische Website auf **GitHub Pages** veröffentlicht wird (nicht als Obsidian-Vault).

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
3. Vorschaubild suchen → nach `docs/images/[name]-img.jpg` kopieren.
4. WebP/VP8-Bilder ggf. mit `ffmpeg` in echtes JPEG (baseline) konvertieren.
5. Markdown-Datei unter `docs/rezepte/` anlegen.
6. Index (`docs/index.md`) aktualisieren.
7. **Kein `#gut`-Tag beim Import.** Neue Rezepte bekommen beim Import standardmäßig **kein** Bewertungstags (`#gut`, `#neu`, …) und landen damit im Index als ❓. Erst wenn ein Link geprüft/würdig ist, wird das Tag (und das Icon) nachträglich ergänzt.
8. **Scraping/Hinweise:** `curl` mit normalem Browser-Ursprung (`Mozilla/5.0`) funktioniert bei chefkoch.de, shibaskitchen.de und emmikochteinfach.de. **REWE (`rewe.de`) blockiert Scraping** (WAF/Bot-Schutz) → Rezepte dort nicht importierbar, Link bleibt offen. Proseg-basierte Seiten (z. B. shibaskitchen) haben oft kein JSON-LD → Rezept aus Blogtext rekonstruieren.

## Index (`docs/index.md`)
- **Alphabetisch sortiert nach Titel**, alle alten Zeilen behalten.
- Spalten: **Rezept** (Icon) | **Vorschau** | **Titel** (Link zur Rezept-Datei) | **Autor** | **Quelle** (Link)
- **Titel als Link:** `[Titel](rezepte/[name].md)` — verlinkt zum jeweiligen Rezept.
- **Icon nach Tags:** `#gut` → ✅, kein Tag/`#neu` → ❓
- Vorschau-Bild: `<img src="images/[name]-img.jpg" alt="..." style="width:100px;height:auto;" />`

## Projekt-Regeln
- `project/index-regeln.md` — Index-Regeln
- `project/Konzeption.md` — Besondere Tags (Icons/Tags)
- `project/Namenskonventionen.md` — Dateinamen
- `project/Struktur.md` — Verzeichnisstruktur

## Veröffentlichung (GitHub Pages)
- Das Projekt wird als **statische Website** über **GitHub Pages** veröffentlicht.
- **Veröffentlichung ist eingerichtet und erfolgt automatisch** nach `git push` (GitHub Actions / Pages-Regel).
- **Ich muss nichts manuell deployen** — nach `git commit` + `git push` wird die neue Version automatisch veröffentlicht.
- Rohdaten (noch nicht importiert) → `rohdaten/`

## Sonstige Regeln
Anweisung: fazit 
1. Die den Inhalt der aktuellen session zusammenfassen.
2. Informationen über den Beginn der Sitzung und die Erstellung des Fazit müssen enthalten sein. 
3. Den Inhalt abspeichern in einer Datei session-logs/[YYYY]/[MM]/[YYYY-MM-DD].md
4. Falls diese Datei schon existiert: Den Inhalt am Ende der Datei anhängen.