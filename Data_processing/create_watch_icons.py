
import json
import pandas as pd
from pathlib import Path
import re


# ============================================================
# 1. SET PROJECT PATHS
# ============================================================

# Locate the project root automatically based on this script's
# location: Data_processing/create_watch_icons.py
ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
IMAGES_DIR = ROOT / "images"

INPUT_JSON = DATA_DIR / "graveyard.json"
WATCH_SVG = IMAGES_DIR / "watch.svg"
OUTPUT_JSON = DATA_DIR / "watchFoundingIcons.json"


# ============================================================
# 2. LOAD AND CLEAN DATA
# ============================================================

if not INPUT_JSON.exists():
    raise FileNotFoundError(
        f"Could not find the input file: {INPUT_JSON}"
    )

df = pd.read_json(INPUT_JSON)

# Remove brands without a founding year
df = df.dropna(subset=["founded"]).copy()

# Ensure founding years are numeric
df["founded"] = pd.to_numeric(df["founded"], errors="coerce")
df = df.dropna(subset=["founded"])


# ============================================================
# 3. GROUP BRANDS INTO FOUNDING PERIODS
# ============================================================

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


df[["foundingPeriod", "periodOrder"]] = df["founded"].apply(
    lambda year: pd.Series(get_period(year))
)

counts = (
    df.groupby(["foundingPeriod", "periodOrder"])
    .size()
    .reset_index(name="brandCount")
    .sort_values("periodOrder")
)

print("\nBrand counts by founding period:")
print(counts.to_string(index=False))


# ============================================================
# 4. READ THE ORIGINAL WATCH SVG
# ============================================================

if not WATCH_SVG.exists():
    raise FileNotFoundError(
        f"Could not find {WATCH_SVG}. "
        "Please check that images/watch.svg exists."
    )

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

svg = WATCH_SVG.read_text(encoding="utf-8")

# Extract the SVG attributes and content
match = re.search(
    r"<svg\b([^>]*)>(.*?)</svg\s*>",
    svg,
    re.DOTALL | re.IGNORECASE
)

if not match:
    raise ValueError(
        "Could not read the SVG structure in images/watch.svg."
    )

svg_attributes = match.group(1)
watch_content = match.group(2)

# Read viewBox dimensions
viewbox_match = re.search(
    r"""viewBox\s*=\s*["']\s*
    ([-\d.]+)\s+([-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*["']""",
    svg_attributes,
    re.VERBOSE
)

if not viewbox_match:
    raise ValueError(
        "images/watch.svg must have a valid viewBox attribute."
    )

origin_x, origin_y, view_width, view_height = map(
    float, viewbox_match.groups()
)


# ============================================================
# 5. GENERATE CLEARER PARTIAL WATCH ICONS
# ============================================================

# One full watch represents 5 brands.
# Generate partial watches for remainders of 1, 2, 3 and 4.
#
# Each partial SVG retains the original watch outline:
# - The complete watch is shown in a faded colour.
# - The fractional portion is shown at full opacity.
# - A boundary line helps distinguish the fraction.

for remainder in range(1, 5):

    fraction = remainder / 5
    filled_width = view_width * fraction

    clip_id = f"watchClip{remainder}"

    partial_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{view_width}"
     height="{view_height}"
     viewBox="{origin_x} {origin_y} {view_width} {view_height}">

    <defs>
        <clipPath id="{clip_id}">
            <rect
                x="{origin_x}"
                y="{origin_y}"
                width="{filled_width}"
                height="{view_height}"
            />
        </clipPath>
    </defs>

    <!-- Full watch outline shown in a faded colour -->
    <g opacity="0.25">
        {watch_content}
    </g>

    <!-- Fractional section shown at full opacity -->
    <g clip-path="url(#{clip_id})">
        {watch_content}
    </g>

    <!-- Boundary indicating the fractional amount -->
    <line
        x1="{origin_x + filled_width}"
        y1="{origin_y + view_height * 0.15}"
        x2="{origin_x + filled_width}"
        y2="{origin_y + view_height * 0.85}"
        stroke="#8B5E3C"
        stroke-width="{max(view_width * 0.025, 0.5)}"
    />

</svg>
"""

    output_path = IMAGES_DIR / f"watch-partial-{remainder}.svg"

    output_path.write_text(
        partial_svg,
        encoding="utf-8"
    )

    print(f"Created: {output_path.relative_to(ROOT)}")

print("\nPartial watch SVG files created successfully.")


# ============================================================
# 6. GENERATE WATCH ICON RECORDS
# ============================================================

icons = []

for _, row in counts.iterrows():

    count = int(row["brandCount"])

    # One complete watch represents 5 brands
    full_icons = count // 5

    # Remaining brands: 1, 2, 3 or 4
    remainder = count % 5

    # Add full watches
    for i in range(full_icons):
        icons.append({
            "foundingPeriod": row["foundingPeriod"],
            "periodOrder": int(row["periodOrder"]),
            "iconIndex": i,
            "icon": "images/watch.svg",
            "brandCount": count
        })

    # Add one partial watch for the remainder
    if remainder > 0:
        icons.append({
            "foundingPeriod": row["foundingPeriod"],
            "periodOrder": int(row["periodOrder"]),
            "iconIndex": full_icons,
            "icon": f"images/watch-partial-{remainder}.svg",
            "brandCount": count
        })


# ============================================================
# 7. SAVE THE JSON FILE
# ============================================================

with OUTPUT_JSON.open("w", encoding="utf-8") as f:
    json.dump(
        icons,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"\nCreated: {OUTPUT_JSON.relative_to(ROOT)}")
print(f"Total icon records: {len(icons)}")


# ============================================================
# 8. PRINT A SUMMARY FOR VERIFICATION
# ============================================================

print("\nWatch representation summary:")

for _, row in counts.iterrows():

    count = int(row["brandCount"])
    full_icons = count // 5
    remainder = count % 5

    print(
        f"{row['foundingPeriod']}: {count} brands = "
        f"{full_icons} full watches + "
        f"{remainder}/5 watch"
        if remainder > 0
        else
        f"{row['foundingPeriod']}: {count} brands = "
        f"{full_icons} full watches"
    )

print("\nAll processing completed.")
