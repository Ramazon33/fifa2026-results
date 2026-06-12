# FIFA 2026 Results Feed

Auto-updated live scores for the FIFA World Cup 2026, consumed by the
**FIFA2026Calendar** Android app.

A GitHub Action polls the public `api.fifa.com` endpoint roughly every minute
during the tournament and commits [`results.json`](results.json) whenever
something changes (goal, final whistle, knockout teams resolved).

## Consume

```
https://raw.githubusercontent.com/Ramazon33/fifa2026-results/main/results.json
```

## Format

```json
{
  "updated": "2026-06-12T05:05:42Z",
  "results": [
    { "id": 1, "status": "FINISHED", "home": "MEX", "away": "RSA", "homeScore": 2, "awayScore": 0 },
    { "id": 95, "status": "LIVE", "home": "FRA", "away": "BRA", "homeScore": 1, "awayScore": 1, "minute": "67'" }
  ]
}
```

- `id` — official FIFA match number (1–104), same as the app's match ids
- `status` — `SCHEDULED` | `LIVE` | `FINISHED`
- `home` / `away` — present once teams are known (resolves knockout placeholders)
- `homePens` / `awayPens` — penalty shoot-out score, knockout only
- `minute` — current match minute, only while `LIVE`
- Matches with no information yet are omitted

## Tools

`tools/regen_matches.py` rebuilds the app's `matches.json` from the FIFA API
(source of truth) — rerun it if FIFA reschedules matches.
