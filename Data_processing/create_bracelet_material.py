import pandas as pd

df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Remove missing bracelet materials
df = df.dropna(
    subset=["bracem"]
)

# Select the top 10 manufacturers
top_manufacturers = (
    df["brand"]
    .value_counts()
    .head(10)
    .index
)

df = df[
    df["brand"].isin(top_manufacturers)
]

# Group bracelet materials
def group_material(material):
    material = material.lower()

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

# Count watches by manufacturer and material
material_counts = (
    df.groupby(
        ["brand", "materialGroup"]
    )
    .size()
    .reset_index(name="watchCount")
)

# Calculate percentage within each manufacturer
manufacturer_totals = (
    material_counts
    .groupby("brand")["watchCount"]
    .transform("sum")
)

material_counts["percentage"] = (
    material_counts["watchCount"]
    / manufacturer_totals
    * 100
)

# Save processed data
material_counts.to_json(
    "data/manufacturerBraceletMaterial.json",
    orient="records",
    indent=2,
    force_ascii=False
)

print(
    "Processed data saved to "
    "data/manufacturerBraceletMaterial.json"
)

print(
    "Number of records:",
    len(material_counts)
)

print(material_counts)