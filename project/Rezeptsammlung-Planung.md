# Rezeptesammlung – Planung & Konzept

- **Beginn der Planung:** 2026-11-18 ~15:10 Uhr
- **Erstellt am:** 2026-11-18 ~15:13 Uhr
- **Auftrag:** Detailliertere Planung der Rezeptsammlung (weiteres Projekt/Verzeichnis), basierend auf bisherigen Gesprächen hier im Wiki.
- **Quellen der bisherigen Gespräche:**
  - `02-Notizen/Projekte/Rezeptsammlung.md` (Idee + Machbarkeitsstudie)
  - `session-logs/2026/11/2026-11-16.md` (Feasibility-Studie: Rezept aus URL extrahieren)
  - `session-logs/2026/11/2026-11-17.md` (GitHub Hosting)

> **Fokus des Plans:** Das **Extrahieren eines Rezepts aus einer URL** — inklusive des **Vorschaubilds**.

---

## 1. Ziel des Projekts

Eine **Rezeptesammlung**, die ähnlich wie ein Obsidian-Vault funktioniert — Obsidian wird für die Verwaltung der Rezepte genutzt.

### Ausrichtung
- **Kein lokales Obsidian-Vault mehr** — das neue Projekt läuft in einem **eigenen Verzeichnis** (frisch angelegt).
- Ziel: Aus einer Rezept-URL → strukturierte `.md`-Datei + **Vorschaubild** extrahieren.
- Nächster Schritt nach dieser Planung: Nyx liest die Datei in das neue Verzeichnis ein, damit sie dort weitergearbeitet werden kann.

---

## 2. Kernfunktionalität: Rezept aus URL extrahieren

### Ablauf
1. **URL angeben** (Rezept auf einer Webseite).
2. **Inhalt extrahieren** — Zutaten, Zubereitung, Backzeit etc. in strukturiertes Markdown.
3. **Portionierung** — Umrechnung auf 4 Personen (Original oft für 2 P.). Funktioniert bereits.
4. **Vorschaubild finden** — Nyx findet passend zum Rezept ein Bild.
5. **Speichern** — `.md` + `.jpg` pro Rezept.

### Bekannte Fakten aus der Feasibility-Studie (16.11.)
- Nyx hat das bereits **erfolgreich getestet**: aus URLs extrahiert, Bild gefunden und eingefügt.
- **Umrechnung auf 4 Personen** funktioniert gut.
- **Bildformat beachten:** WebP/VP8-Mustern müssen ggf. mit `ffmpeg` in echtes JPEG (baseline) konvertiert werden, damit alle Vorschaubilder einheitlich sind.
- **Vorschau-Spalte im Index:** schlichtes `<img src=... />` (echtes Bild, **nicht** klickbar, auf 100px Breite skalierbar).

### Tools / Methodik
- Websuche/Recherche läuft über das **`free-search-mcp`-Plugin** (eingebaute `WebSearch` wird bewusst gemieden).
- Zur Bildkonvertierung: `ffmpeg`.

---

## 3. Struktur & Namenskonventionen

| Element | Speicherort |
|---------|-------------|
| Rezepte (`.md`) | Unter `` index/ `` → weiter nach `` rezepte/ `` |
| Vorschaubilder | Unter `` index/ `` → weiter nach `` images/ `` |

- **Namenskonvention:** `[REZEPT].md` und `[IMAGE].md` (Bilder gleichen Rezepts).
- Im Rezept: **Platz für eigene Bemerkungen** (z. B. „war gut", „Salz reduzieren").

---

## 4. Index / Übersicht

- Alphabetisch sortierte **Tabelle** mit Rezeptnamen + Vorschaubild.
- **Rückverweise** auf den Index (Link von jeder Rezeptseite zum Index).
- **Bewertung** (Bewährt / noch nicht ausprobiert / ❓):
  - Angezeigt im Index.
  - Hinterlegt im `.md` des Rezepts (besser als `tag`).
  - **Keine Checkbox** (wird durchgestrichen).

---

## 5. Weitere Features / Roadmap

- **Import von PDF** (z. B. aus Google-Drive).
- Umgang mit Screenshots / händisch erstellten Rezepten → ggf. leere Vorlage erstellen lassen.

---

## 6. Hosting / Publikation (Entscheidungsgeschichte)

| Variante | Status | Anmerkung |
|----------|--------|-----------|
| Obsidian „Website"-Export (Online Website) | ⚠️ Probleme | Dateien für Rezept und Vorschaubild unterschieden sich nur in der Endung → Export-Problem; händisch korrigiert. |
| **GitHub Pages** ⭐ | ✅ Empfohlen | Sehr gut & leicht: `.md`-Dateien in ein Git-Repo, Unterordner `docs/` als Website publizieren. |
| GitHub Site | — | Muss erst mal studiert werden. |
| Nachteil GitHub | — | Rezeptsammlung **nicht immer online** (z. B. für den Einkaufszettel). |

---

## 7. Nächste Schritte (für Nyx im neuen Projekt)

1. Nyx liest die Datei in das neue Projektverzeichnis ein.
2. Frisches, leeres Projekt anlegen (bzw. bestehende `tmp/rezepte/`-Struktur als Vorlage nutzen).
3. **Fokus: Rezept aus URL extrahieren + Vorschaubild** als Kernfeature ausbauen.
4. Struktur nach Konvention (`rezepte/` + `images/`, Index mit Rückverweisen & Bewertung).
5. Hosting auf **GitHub Pages** planen.

---

## 8. Referenzquellen

- Idee & Machbarkeitsstudie: `02-Notizen/Projekte/Rezeptsammlung.md`
- Feasibility-Studie (Rezept aus URL extrahieren): `session-logs/2026/11/2026-11-16.md`
- GitHub Hosting: `01-Journal/2026/11/2026-11-17.md`
- Publish-Recherche: `03-Import/Recherche/Recherche-Obsidian-Publish.md`
