import json

d = json.load(open(r"..\FIFA2026Calendar\app\src\main\assets\matches.json", encoding="utf-8"))
team_group = {t["code"]: t["group"] for t in d["teams"]}
bad = []
for m in d["matches"]:
    if m["stage"] != "GROUP":
        continue
    for side in ("home", "away"):
        code = m[side]
        if team_group.get(code) != m["group"]:
            bad.append(f"match {m['id']}: {code} plays in group {m['group']} but teams[] says {team_group.get(code)}")
print("group mismatches:", len(bad))
for b in bad:
    print(" ", b)
# also check groups[] section
for g in d["groups"]:
    for code in g["teams"]:
        if team_group.get(code) != g["id"]:
            print(f"groups[] mismatch: {code} in group {g['id']} vs teams[] {team_group.get(code)}")
print("groups[] checked")
