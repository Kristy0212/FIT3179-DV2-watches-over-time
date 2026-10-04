import pandas as pd

# Load dataset 
df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Remove records without case material
df = df.dropna(subset=["casem"])

# Find the top 10 manufacturers
top_manufacturers = (
    df["brand"]
    .value_counts()
    .head(10)
    .index
)

df = df[df["brand"].isin(top_manufacturers)]

# Group case materials
def group_material(material):
    material = material.lower()

    if "steel" in material:
        if "gold" in material:
            return "Gold / Gold combination"
        return "Steel"

    elif "gold" in material:
        return "Gold / Gold combination"

    elif "titanium" in material:
        return "Titanium"

    elif "ceramic" in material:
        return "Ceramic"

    elif "platinum" in material:
        return "Platinum"

    else:
        return "Other"
    
# Count watches by manufacturer and case material
material_counts = (
    df.groupby(["brand", "casem"])
    .size()
    .reset_index(name="watchCount")
)

# Apply material grouping
material_counts["materialGroup"] = (
    material_counts["casem"].apply(group_material)
)

# Combine the grouped materials
material_counts = (
    material_counts
    .groupby(["brand", "materialGroup"])["watchCount"]
    .sum()
    .reset_index()
)

# Calculate the total number of watches for each manufacturer
manufacturer_totals = (
    material_counts
    .groupby("brand")["watchCount"]
    .transform("sum")
)

# Calculate percentage
material_counts["percentage"] = (
    material_counts["watchCount"]/
    manufacturer_totals * 100
)

# Store processed data 
material_counts.to_json(
    "data/manufacturerCaseMaterial.json",
    orient="records",
    indent=2,
    force_ascii=False
)

print("Processed data saved to data/manufacturerCaseMaterial.json")
print("Number of records:", len(material_counts))