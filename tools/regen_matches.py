"""Rebuild the `matches` array of the app's matches.json from the official
FIFA API (source of truth), keeping the app's schema. id = FIFA MatchNumber.

Writes matches.json.new next to the original and prints a diff summary.
"""
import json
import urllib.request
from datetime import datetime, timedelta

FIFA_URL = ("https://api.fifa.com/api/v3/calendar/matches"
            "?idCompetition=17&idSeason=285023&language=en&count=110")
APP_JSON = r"..\FIFA2026Calendar\app\src\main\assets\matches.json"

STADIUM_MAP = {
    "Estadio Azteca": "mex_city", "Mexico City Stadium": "mex_city",
    "BC Place Vancouver": "vancouver", "BC Place": "vancouver",
    "San Francisco Bay Area Stadium": "sf_bay",
    "Monterrey Stadium": "monterrey", "Estadio Monterrey": "monterrey",
    "Philadelphia Stadium": "philadelphia",
    "Miami Stadium": "miami",
    "Guadalajara Stadium": "guadalajara", "Estadio Guadalajara": "guadalajara",
    "Atlanta Stadium": "atlanta",
    "New York/New Jersey Stadium": "ny_nj", "New York New Jersey Stadium": "ny_nj",
    "Los Angeles Stadium": "la",
    "Dallas Stadium": "dallas",
    "Kansas City Stadium": "kansas_city",
    "Houston Stadium": "houston",
    "Boston Stadium": "boston",
    "Seattle Stadium": "seattle",
    "Toronto Stadium": "toronto",
}


def stage_of(n):
    if n <= 72:
        return "GROUP"
    if n <= 88:
        return "R32"
    if n <= 96:
        return "R16"
    if n <= 100:
        return "QF"
    if n <= 102:
        return "SF"
    return "3RD_PLACE" if n == 103 else "FINAL"


def main():
    app = json.load(open(APP_JSON, encoding="utf-8"))
    old = {m["id"]: m for m in app["matches"]}

    req = urllib.request.Request(FIFA_URL, headers={"User-Agent": "Mozilla/5.0"})
    fifa = json.load(urllib.request.urlopen(req))["Results"]
    assert len(fifa) == 104, f"expected 104 matches, got {len(fifa)}"

    new_matches = []
    changes = []
    for f in sorted(fifa, key=lambda x: x["MatchNumber"]):
        n = f["MatchNumber"]
        stage = stage_of(n)
        et = datetime.strptime(f["Date"], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=4)

        st_name = (f.get("Stadium") or {}).get("Name", [{}])[0].get("Description", "")
        stadium = STADIUM_MAP.get(st_name)
        assert stadium, f"unknown stadium: {st_name!r} (match {n})"

        def norm(ph):
            # app convention: L101/L102 for SF losers, FIFA uses RU101/RU102
            return ph.replace("RU", "L") if ph and ph.startswith("RU") else ph

        def side(team, ph):
            ab = (team or {}).get("Abbreviation")
            return ab or norm(ph)

        home = side(f.get("Home"), f.get("PlaceHolderA"))
        away = side(f.get("Away"), f.get("PlaceHolderB"))

        m = {"id": n, "stage": stage}
        if stage == "GROUP":
            g = (f.get("GroupName") or [{}])[0].get("Description", "")
            m["group"] = g.replace("Group ", "")
        m["date"] = et.strftime("%Y-%m-%d")
        m["timeET"] = et.strftime("%H:%M")
        m["home"] = home
        m["away"] = away
        m["stadium"] = stadium
        if stage != "GROUP":
            m["matchup"] = f"{norm(f.get('PlaceHolderA'))} v {norm(f.get('PlaceHolderB'))}"
        new_matches.append(m)

        o = old.get(n, {})
        diffs = [k for k in ("date", "timeET", "home", "away", "stadium", "stage", "group")
                 if o.get(k) != m.get(k)]
        if diffs:
            changes.append(f"id {n}: " + ", ".join(
                f"{k}: {o.get(k)!r} -> {m.get(k)!r}" for k in diffs))

    # sanity: group stage must have exactly the same 48 team codes as before
    old_codes = {x[k] for x in old.values() if x["stage"] == "GROUP" for k in ("home", "away")}
    new_codes = {x[k] for x in new_matches if x["stage"] == "GROUP" for k in ("home", "away")}
    print("team codes identical:", old_codes == new_codes)
    if old_codes != new_codes:
        print("  only in old:", sorted(old_codes - new_codes))
        print("  only in new:", sorted(new_codes - old_codes))

    print(f"changed matches: {len(changes)}")
    for c in changes:
        print(" ", c)

    app["matches"] = new_matches
    out = APP_JSON + ".new"
    json.dump(app, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("written:", out)


if __name__ == "__main__":
    main()
