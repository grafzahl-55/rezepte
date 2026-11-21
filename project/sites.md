# Website-Status

Welche Quellen im Import bisher **erfolgreich** waren und welche **problematisch** sind.
Aktualisiert beim Import (Zeile/Rezept + Datum).

> **Legende:**
> - ✅ = Import erfolgreich abgeschlossen (Rezept-Datei existiert, Bild da)
> - ⚠️ = Importbar, aber mit Problemen (z. B. kein JSON-LD, Bild nicht als Baseline)
> - ❌ = Blockiert / nicht importierbar
> - _(geprüft)_ = von Nyx direkt in dieser Sitzung getestet

## ✅ Erfolgreich importiert

| Site | Status | Details |
| --- | --- | --- |
| **chefkoch.de** | ✅ | WebFetch funktioniert. Klassischer Import. Viele Rezepte. |
| **gaumenfreundin.de** | ✅ | `curl` mit `Mozilla/5.0` + og:image. (geprüft 20.11.2026) |
| **malteskitchen.de** | ✅ | WebFetch funktioniert. og:image liegt als **Baseline** vor (kein Konvertieren nötig). (geprüft 20.11.2026) |
| **sabrinastable.com** | ✅ | WebFetch + strukturierte Rezeptdaten. og:image war **progressiv** → mit `ffmpeg -vsync 1` in Baseline konvertiert. (geprüft 20.11.2026) |
| **ndr.de** | ✅ | **JS-generiert** — WebFetch schlägt fehl, aber `curl` + extrahiertes **JSON-LD** (`recipeIngredient` + Step-Array) reicht. Bild aus `images.ndr.de` (Baseline). Link `[x]` von Michael selbst gesetzt. (geprüft 20.11.2026) |
| **gewuerze-der-welt.net** | ✅ | Importiert (Ofenschlupfer). |
| **kochbar.de** | ✅ | Importiert (Saltimbocca, Szegediner-Gulasch). Hat Portionierungs-Parameter (`?personen=4`). **Kein JSON-LD** — Zutaten liegen in einer **`<table>`** (Name-Zellen + `amount-cell`-Zellen mit Mengen), Zubereitung in nummerierten **`<p>`**-Absätzen. (geprüft 21.11.2026, Szegediner-Gulasch) |
| **shibaskitchen.de** | ⚠️ | **proseg-basiert** → **kein JSON-LD**, Rezept aus Blogtext rekonstruiert. 2 Rezepte importiert. |
| **emmikochteinfach.de** | ✅ | `curl` + og:image funktioniert. Kein JSON-LD → Zubereitung aus Fließtext (geordnete `<li>`). 2 Rezepte importiert. (aktualisiert 21.11.2026, Hühnerfrikassee) |
| **eatbetter.de** | ⚠️ | **Kein JSON-LD**, keine `<li>`-Listen — app-ähnliche „Kochmodus"-Darstellung. Rezept aus Fließtext (`[Menge] [Zutat]` + Schritte) rekonstruiert. (geprüft 21.11.2026) |
| **madamecuisine.de** | ✅ | Importiert (rotes Thai-Curry). |
| **edeka.de** | ✅ | Importiert (Thai-Curry mit Nudeln). |
| **daskochrezept.de** | ✅ | Importiert (Schnitzel mit Pfifferlingen). |
| **authentisch-italienisch-kochen.de** | ✅ | Importiert (Tagliatelle ai Cantarelli). |
| **gutekueche.de** | ✅ | Importiert (Hühnertopf mit Nudeln). |
| **eatsmarter.de** | ✅ | **JSON-LD** (`recipeIngredient`, `datePublished`, `recipeCategory`) funktioniert. Achtung: Das **og:image im `<head>` ist ein Facebook-Thumbnail** — das echte Bild liegt im **JSON-LD** (`image` + `styles/max_size`). Bild aus `images.eatsmarter.de` (groß) heruntergeladen, mit `PIL` auf 1200 px Breite + Baseline-JPEG resized. (geprüft 21.11.2026) |
| **kochenausliebe.com** | ✅ | **Inline-JSON-LD** (`recipeJSON-LD`, `@type":"Recipe"`) funktioniert — `recipeIngredient`, `recipeStep`/`HowToStep`-Texte, `datePublished`, `totalTime`. Bild aus `og:image` (Baseline-`file`-URL, progressive → mit `PIL` in Baseline konvertiert). Rezept ist für **2 Portionen** → hier auf 4 verdoppelt. (geprüft 21.11.2026, Ratatouille) |
| **einfachkochen.de** | ✅ | **Inline-JSON-LD** (`recipeJSON-LD`, `@type":"Recipe"`), **nicht** in einem `<script type="application/ld+json">`-Tag — als **`<div>`-Block** im HTML. Extrahiert durch Brace-Matching um das erste `{` vor `"recipeInstructions"`. `recipeIngredient` (Grid-Struktur: `col-span-2`-Zellen), `recipeInstructions` (HowToStep-Texte), `totalTime`/`prepTime`/`cookTime`, `recipeYield=4`. **Bild-Download:** `og:image`-URL schlägt mit **HTTP 403** ab (Browser-Header nötig) → mit `User-Agent: Mozilla/5.0 ...` + `Accept: image/*` per `urllib` runtergeladen. Rezept ist für **4 Portionen** → kein Skalieren nötig. (geprüft 21.11.2026, Käse-Lauch-Suppe mit Hackfleisch) |

## ✅ Importiert über Clipping (nicht über direktes Scraping)

| Site | Status | Details |
| --- | --- | --- |
| **rewe.de** | ✅ | **Kein direktes Scraping möglich** (WAF/Bot-Schutz). Import über **WebClipper-Clipping** aus dem `Clippings/`-Verzeichnis. Zutaten in Markdown-Tabelle, Zubereitung als Aufzählung, Bild als `img`-Tag im Clipping. **Irish Stew** (`Clippings/Irish Stew.md`, Rezept für 4 Portionen → kein Skalieren nötig) → Rezept-Datei + Bild. Irish Stew-Bild (`c.rewe-static.de` PNG-URL → tatsächlich JPEG, progressive → mit `PIL` in Baseline konvertiert). Avocado Wrap Dill Dip (`Clippings/Avocado-Wrap mit Dill-Dip.md`) → Rezept-Datei + Bild. Link `[x]` in `Linksammlung.md` von Michael selbst gesetzt. **Dieser Weg funktioniert für REWE.** (Rezept erstellt 11.11.2025; Irish Stew geprüft 21.11.2026) |

## Anmerkungen

- **Clipping-Weg:** REWE ist nicht „blockiert" im Sinne von „nie importierbar" — der **WebClipper-Clipping-Weg** ist ein funktionierender Import-Weg für Seiten, die Bot-Schutz haben. Clippings in `Clippings/` zu legen und daraus das Rezept zu rekonstruieren, ist der Weg für REWE.
- **`[x]` von Michael gesetzt:** Beim REWE- und NDR-Import wurde das Kreuz in der `Linksammlung.md` von Michael selbst gesetzt (nicht automatisch von Nyx). Nyx ergänzt danach nur das Icon im Index.
- **NDR-Hinweis:** NDR hat JSON-LD, aber der Strukturgrad variiert je nach Rezept (siehe Grüne-Gemüse-Tarte — einmal war das Step-Array unvollständig). Bei NDR nicht immer allein darauf verlassen.
- **Bild-Formate:** og:image ist nicht immer Baseline. Progressive/WebP-Bilder mit `ffmpeg` in echtes Baseline-JPEG (`-vsync 1`) konvertieren (d.h. `ffmpeg` `profile baseline` wird von dieser ffmpeg-Version nicht unterstützt). Siehe CLAUDE.md Regel 3a/4.
- Diese Datei wird bei jedem Import ergänzt/anpasst.
