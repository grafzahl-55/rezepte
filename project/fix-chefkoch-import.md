

Das Skript import-chefkoch-jsonld.py wird auch für andere Quellen benutzt, daher sind einige Änderungen notwendig
- Als Quelle des erzeugten Rezepts darf nicht automatisch Chefkoch eingetragen werden sondern die Domain der tatsächlich benutzen Quelle, z.B. "gaumenfreundin.de" als Anzeigename des Links.
- Sofern sich ein Autor aus der heruntergeladenen HTML-Datei ermitteln lässt, diesen als Autor des Rezepts eintragen, ansonsten ein einfaches '-' Zeichen.
- Quelle und Autor sowohl im Rezept als auch in der index auf diese Weise setzen. 

Als Test verwende bitte das nächste offene Rezept von gaumenfreundin.de aus der Linksammlung.

## Abgeschlossen (23.11.2026)

- **Tortilla-Wraps selber machen** importiert. Quelle = „Gaumenfreundin" (aus WebSite-Node im JSON-LD), Autor = „Steffi (Gaumenfreundin)" (aus JSON-LD).
- **Nasi Goreng** importiert. Gleiche Metadaten.
- In `Linksammlung.md` jeweils `[x]` gesetzt.
- `bin/import-chefkoch-jsonld.py`: `resolve_author()` (JSON-LD → HTML-Meta → `-`), `resolve_source_name()` (WebSite-Node → Domain), Index-Zeile mit Quelle + Autor.

