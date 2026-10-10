import json
import pandas as pd

df = pd.read_json("data/graveyard.json")

df = df.dropna(subset=["founded"])


def get_period(year):
    if year < 1800:
        return "Before 1800", 1
    elif year < 1850:
        return "1800-1849", 2
    elif year < 1900:
        return "1850-1899", 3
    elif year < 1950:
        return "1900-1949", 4
    elif year < 2000:
        return "1950-1999", 5
    else:
        return "2000 onwards", 6


df[["foundingPeriod", "periodOrder"]] = (
    df["founded"].apply(
        lambda year: pd.Series(get_period(year))
    )
)

counts = (
    df.groupby(["foundingPeriod", "periodOrder"])
    .size()
    .reset_index(name="brandCount")
)

icons = []

for _, row in counts.iterrows():
    count = int(row["brandCount"])

    # One watch represents 5 brands.
    full_icons = count // 5

    for i in range(full_icons):
        icons.append({
            "foundingPeriod": row["foundingPeriod"],
            "periodOrder": int(row["periodOrder"]),
            "iconIndex": i,
            "icon": "images/watch.svg",
            "brandCount": count
        })

with open(
    "data/watchFoundingIcons.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(icons, f, indent=2, ensure_ascii=False)

print("Created data/watchFoundingIcons.json")
print(counts)