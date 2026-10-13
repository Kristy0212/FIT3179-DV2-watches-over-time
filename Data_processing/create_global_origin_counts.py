
import json
from collections import Counter

# Load global watch brand data
with open(
    "data/global-watch-brand-history-index-2026-08-24.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

# Count watch brands by historical origin
counts = Counter()

for manufacturer in data:
    origin = manufacturer.get("historical_origin")

    if origin:
        # If multiple origins are listed, use the first one
        origin = origin.split("/")[0].strip()

        # Make country names consistent with the world map
        if origin.endswith(" origin"):
            origin = origin.replace(" origin", "")
        elif origin.endswith(" heritage"):
            origin = origin.replace(" heritage", "")
        elif origin.endswith(" identity"):
            origin = origin.replace(" identity", "")
        elif origin.endswith(" founder"):
            origin = origin.replace(" founder", "")

        if origin == "England" or origin == "Scotland":
            origin = "United Kingdom"
        elif origin == "Soviet Union":
            origin = "Russia"
        elif origin == "United States":
            origin = "United States of America"

        counts[origin] += 1

# Calculate total brands with recorded historical origins
total_brands = sum(counts.values())

# Convert to the format needed by Vega-Lite
origin_counts = []

for country, count in counts.items():
    percentage = (count / total_brands) * 100

    item = {
        "origin": country,
        "manufacturerCount": count,
        "manufacturerPercentage": round(percentage, 2)
    }

    origin_counts.append(item)

# Sort from highest to lowest brand count
origin_counts.sort(
    key=lambda x: x["manufacturerCount"],
    reverse=True
)

# Save the result
with open(
    "data/globalOriginCounts.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        origin_counts,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Created data/globalOriginCounts.json")
print(f"Countries: {len(origin_counts)}")
print(f"Brands with recorded origins: {total_brands}")

for item in origin_counts:
    print(item)
