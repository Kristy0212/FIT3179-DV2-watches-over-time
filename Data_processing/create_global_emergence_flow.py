import json
import re
from collections import Counter 

# Load global watch brand data 
with open(
    "data/global-watch-brand-history-index-2026-08-24.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

def extract_year(text):
    """
    Extract the first four-digit year from the date description.
    """
    match = re.search(r"(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)", str(text))
    if match:
        return int(match.group())
    return None

def normalize_country(origin):
    """
    Convert the first-listed historical origin into
    a country name suitable for the world map.
    """
    origin = origin.split("/")[0].strip()

    # Remove descriptive suffixes 
    suffixes = [
        "origin",
        "heritage",
        "identity",
        "founder"
    ]

    for suffix in suffixes:
        if origin.endswith(suffix):
            origin = origin[:-len(suffix)].strip()

    # Normalize means
    if origin == "England" or origin == "Scotland":
        origin = "United Kingdom"
    elif origin == "Soviet Union":
        origin = "Russia"
    elif origin == "Isle of Man":
        origin = "United Kingdom"
    elif origin in ["United States", "United States of America"]:
        origin = "United States of America"
    elif origin in ["Czech Republic", "Czechia"]:
        origin = "Czechia"
    return origin 

# Store precossed records
records = []

for manufacturer in data:
    origin = manufacturer.get("historical_origin")
    date_text = manufacturer.get("origin_or_brand_date")
    brand = manufacturer.get("brand")

    if not origin or not date_text or not brand:
        continue

    country = normalize_country(origin)
    year = extract_year(date_text)

    if year is None:
        continue 

    records.append({
        "country": country,
        "year": year,
        "brand": brand
    })

# Count brands by country
brand_counts = Counter(
    record["country"]
    for record in records
)

# Find the earliest recorded brand for each country
earliest_by_country = {}
for record in records:
    country = record["country"]
    if country not in earliest_by_country:
        earliest_by_country[country] = record
    elif record["year"] < earliest_by_country[country]["year"]:
        earliest_by_country[country] = record

# Build final dataset
emergence_flow = []
for country, record in earliest_by_country.items():
    emergence_flow.append({
        "country": country,
        "earliestYear": record["year"],
        "earliestBrand": record["brand"],
        "brandCount": brand_counts[country]
    })

# Sort countries from earliest to latest emergence 
emergence_flow.sort(
    key=lambda x:(x["earliestYear"], x["country"])
)

# Add chronological order 
for i, record in enumerate(emergence_flow, start=1):
    record["order"] = i

# Save precossed data 
with open(
    "data/globalEmergenceFlow.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        emergence_flow,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Created data/globalEmergenceFlow.json")
print(f"Countries: {len(emergence_flow)}")
print()

for record in emergence_flow:
    print(
        f"{record['order']:>2}. "
        f"{record['country']:<20} "
        f"{record['earliestYear']} - "
        f"{record['earliestBrand']} "
        f"({record['brandCount']} brands)"
    )