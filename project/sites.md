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
| **kochbar.de** | ✅ | Importiert (Saltimbocca). Hat Portionierungs-Parameter (`?personen=4`). |
| **shibaskitchen.de** | ⚠️ | **proseg-basiert** → **kein JSON-LD**, Rezept aus Blogtext rekonstruiert. 2 Rezepte importiert. |
| **emmikochteinfach.de** | ✅ | Importiert. `curl` funktioniert. |
| **madamecuisine.de** | ✅ | Importiert (rotes Thai-Curry). |
| **edeka.de** | ✅ | Importiert (Thai-Curry mit Nudeln). |
| **daskochrezept.de** | ✅ | Importiert (Schnitzel mit Pfifferlingen). |
| **authentisch-italienisch-kochen.de** | ✅ | Importiert (Tagliatelle ai Cantarelli). |
| **gutekueche.de** | ✅ | Importiert (Hühnertopf mit Nudeln). |

## ✅ Importiert über Clipping (nicht über direktes Scraping)

| Site | Status | Details |
| --- | --- | --- |
| **rewe.de** | ✅ | **Kein direktes Scraping möglich** (WAF/Bot-Schutz). Import über **WebClipper-Clipping** aus dem `Clippings/`-Verzeichnis. Avocado Wrap Dill Dip (`Clippings/Avocado-Wrap mit Dill-Dip.md`) → Rezept-Datei + Bild. Link `[x]` in `Linksammlung.md` von Michael selbst gesetzt. **Dieser Weg funktioniert für REWE.** (Rezept erstellt 11.11.2025) |

## Anmerkungen

- **Clipping-Weg:** REWE ist nicht „blockiert" im Sinne von „nie importierbar" — der **WebClipper-Clipping-Weg** ist ein funktionierender Import-Weg für Seiten, die Bot-Schutz haben. Clippings in `Clippings/` zu legen und daraus das Rezept zu rekonstruieren, ist der Weg für REWE.
- **`[x]` von Michael gesetzt:** Beim REWE- und NDR-Import wurde das Kreuz in der `Linksammlung.md` von Michael selbst gesetzt (nicht automatisch von Nyx). Nyx ergänzt danach nur das Icon im Index.
- **NDR-Hinweis:** NDR hat JSON-LD, aber der Strukturgrad variiert je nach Rezept (siehe Grüne-Gemüse-Tarte — einmal war das Step-Array unvollständig). Bei NDR nicht immer allein darauf verlassen.
- **Bild-Formate:** og:image ist nicht immer Baseline. Progressive/WebP-Bilder mit `ffmpeg` in echtes Baseline-JPEG (`-vsync 1`) konvertieren (d.h. `ffmpeg` `profile baseline` wird von dieser ffmpeg-Version nicht unterstützt). Siehe CLAUDE.md Regel 3a/4.
- Diese Datei wird bei jedem Import ergänzt/anpasst.
