import pandas as pd

# ============================================
# 1. Load dataset
# ============================================

df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Convert year of production to numeric
df["yop"] = pd.to_numeric(
    df["yop"],
    errors="coerce"
)

# Remove rows with missing bracelet material or production year
df = df.dropna(
    subset=["bracem", "yop"]
)


# ============================================
# 2. Select top 10 manufacturers
# ============================================

top_manufacturers = (
    df["brand"]
    .value_counts()
    .head(10)
    .index
)

df = df[
    df["brand"].isin(top_manufacturers)
]


# ============================================
# 3. Group bracelet / strap materials
# ============================================

def group_material(material):

    material = str(material).lower()

    if "gold" in material:
        return "Gold / Gold combination"

    elif "steel" in material:
        return "Steel"

    elif "leather" in material or "skin" in material:
        return "Leather / Animal skin"

    elif "rubber" in material:
        return "Rubber"

    elif "titanium" in material:
        return "Titanium"

    elif "ceramic" in material:
        return "Ceramic"

    elif "textile" in material or "satin" in material:
        return "Textile"

    else:
        return "Other"


df["materialGroup"] = (
    df["bracem"].apply(group_material)
)


# ============================================
# 4. Create production periods
# ============================================

def get_period(year):

    if year < 1950:
        return "Before 1950"

    elif year < 1970:
        return "1950-1969"

    elif year < 1990:
        return "1970-1989"

    elif year < 2010:
        return "1990-2009"

    else:
        return "2010+"


df["productionPeriod"] = (
    df["yop"].apply(get_period)
)


# ============================================
# 5. Count watches by period and material
# ============================================

material_counts = (
    df.groupby(
        ["productionPeriod", "materialGroup"]
    )
    .size()
    .reset_index(name="watchCount")
)


# ============================================
# 6. Calculate percentage within each period
# ============================================

period_totals = (
    material_counts
    .groupby("productionPeriod")["watchCount"]
    .transform("sum")
)

material_counts["percentage"] = (
    material_counts["watchCount"]
    / period_totals
    * 100
)


# ============================================
# 7. Calculate material ranking within period
# ============================================

material_counts["rank"] = (
    material_counts
    .groupby("productionPeriod")["percentage"]
    .rank(
        method="min",
        ascending=False
    )
)

material_counts["rank"] = (
    material_counts["rank"].astype(int)
)


# ============================================
# 8. Set correct production period order
# ============================================

period_order = [
    "Before 1950",
    "1950-1969",
    "1970-1989",
    "1990-2009",
    "2010+"
]

material_counts["productionPeriod"] = pd.Categorical(
    material_counts["productionPeriod"],
    categories=period_order,
    ordered=True
)


# ============================================
# 9. Sort data
# ============================================

material_counts = material_counts.sort_values(
    ["productionPeriod", "rank"]
)


# ============================================
# 10. Save processed data
# ============================================

material_counts.to_json(
    "data/braceletMaterialEvolution.json",
    orient="records",
    indent=2,
    force_ascii=False
)


# ============================================
# 11. Print results
# ============================================

print(
    "Processed data saved to "
    "data/braceletMaterialEvolution.json"
)

print(
    "Number of records:",
    len(material_counts)
)

print()
print(material_counts)