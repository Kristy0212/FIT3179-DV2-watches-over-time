import json
from collections import Counter 

# Load global watch brand data
with open(
    "data/global-watch-brand-history-index-2026-08-24.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

# Counts currently active watch brands by historical origin 
counts = Counter()

for manufacturer in data:
    status = manufacturer.get("status_as_of_2026_08_24", "").lower()

    # Include active brands, including statuses such as:
    # "active/limited", "active revival", "active under license", etc.
    if "active" not in status:
        continue

    origin = manufacturer.get("historical_origin")

    # Skip records without an origin 
    if not origin:
        continue 
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
            
    if origin == "England":
        origin = "United Kingdom"
    elif origin == "Scotland":
        origin = "United Kingdom"
    elif origin == "Soviet Union":
        origin = "Russia"
    counts[origin] += 1

# Convert to the format needed by Vega-Lite
active_counts = []

for country, count in counts.items():
    item = {
        "origin": country,
        "activeCount": count
    }
    active_counts.append(item)

# Sort from the highest to the lowest 
active_counts.sort(
    key=lambda x:x["activeCount"],
    reverse= True 
)

# Save the result
with open("data/globalActiveCounts.json", "w", encoding="utf-8") as f:
    json.dump(active_counts, f, indent=2, ensure_ascii = False)

print("Created data/globalActiveCounts.json")
print(f"Countries:{len(active_counts)}")

for item in active_counts:
    print(item)