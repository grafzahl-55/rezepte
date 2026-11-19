# Import-Versuch: Avocado Wrap Dill Dip (REWE)

- **URL:** https://www.rewe.de/rezepte/avocado-wrap-dill-dip/
- **Datum des Versuchs:** 19. November 2025
- **Status:** ❌ NICHT importiert (REWE blockiert Scraping)

## Fehleranalyse
- **HTTP-Status:** 403 Forbidden
- **Ursache:** REWE blockiert Scraping via WAF/Bot-Schutz (Akamai-Challenge-Seite)
- **Fehlende Daten:** Rezept (Zutaten, Zubereitung, Zeiten, Allergene) und Vorschaubild konnten nicht abgerufen werden

## Versuche
- Browser-ähnlicher `curl` (Mozilla/5.0, Chrome-User-Agent, de-DE-Akzept-Sprache) → 403
- REWE-API-Endpunkt `/api/recipe/...` → 404
- Alternativquellen (chefkoch.de, Google, Bing, DuckDuckGo-Suche) → kein passendes Rezept gefunden

## Hinweis
Laut Projektregeln ist REWE bekanntlich nicht importierbar. Link bleibt offen.
