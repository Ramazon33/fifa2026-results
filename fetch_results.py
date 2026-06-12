"""Fetch FIFA World Cup 2026 scores from api.fifa.com and write results.json.

Match ids in results.json are official FIFA match numbers (1-104), which are
also the ids used by the FIFA2026Calendar app. Only matches that have a score,
are live/finished, or have resolved knockout teams are included.

The file is rewritten only when the payload actually changes, so the calling
workflow can use `git diff` to decide whether to commit.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone

FIFA_URL = ("https://api.fifa.com/api/v3/calendar/matches"
            "?idCompetition=17&idSeason=285023&language=en&count=110")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")


def main():
    req = urllib.request.Request(FIFA_URL, headers={"User-Agent": "Mozilla/5.0"})
    fifa = json.load(urllib.request.urlopen(req, timeout=30))["Results"]

    results = []
    for f in sorted(fifa, key=lambda x: x["MatchNumber"]):
        n = f["MatchNumber"]
        home = (f.get("Home") or {}).get("Abbreviation")
        away = (f.get("Away") or {}).get("Abbreviation")
        has_score = f.get("HomeTeamScore") is not None
        finished = f.get("MatchStatus") == 0
        live = f.get("MatchStatus") == 3 or (has_score and not finished)
        resolved_knockout = n > 72 and (home or away)

        if not (has_score or finished or live or resolved_knockout):
            continue

        r = {"id": n, "status": "FINISHED" if finished else ("LIVE" if live else "SCHEDULED")}
        if home:
            r["home"] = home
        if away:
            r["away"] = away
        if has_score:
            r["homeScore"] = f["HomeTeamScore"]
            r["awayScore"] = f["AwayTeamScore"]
        hp, ap = f.get("HomeTeamPenaltyScore"), f.get("AwayTeamPenaltyScore")
        if hp is not None and ap is not None and (hp or ap):
            r["homePens"] = hp
            r["awayPens"] = ap
        if live and f.get("MatchTime"):
            r["minute"] = f["MatchTime"]
        results.append(r)

    payload = {"results": results}

    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
        old.pop("updated", None)
        if old == payload:
            print(f"no changes ({len(results)} matches in file)")
            return

    payload = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               **payload}
    with open(OUT, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=1)
        fp.write("\n")
    print(f"results.json updated ({len(results)} matches)")


if __name__ == "__main__":
    main()
