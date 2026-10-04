import pandas as pd 

# Load dataset 
df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Extract the numeric year from yop 
df["year"] = (
    df["yop"].astype(str).str.extract(r"(\d{4})")[0]
)

df["year"] = pd.to_numeric(
    df["year"],errors="coerce"
)

# Remove records without a valid production year
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# Create production periods
def create_period(year):
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

df["productionPeriod"] = df["year"].apply(create_period)

period_order = [
    "Before 1950",
    "1950-1969",
    "1970-1989",
    "1990-2009",
    "2010+"
]

df["productionPeriod"] = pd.Categorical(
    df["productionPeriod"],
    categories=period_order,
    ordered=True
)

# Count watches by manufacturer and production period
counts = (
    df.groupby(["brand", "productionPeriod"], observed=False)
    .size()
    .reset_index(name="watchCount")
)

# Create an order for the production periods
counts["periodOrder"] = counts["productionPeriod"].cat.codes

# Find the manufacturers with the most watches 
manufacturer_totals = (
    counts.groupby("brand")["watchCount"]
    .sum()
    .sort_values(ascending=False)
)

# Select the top 5 manufacturers
top_manufacturers = manufacturer_totals.head(10).index
counts = counts[
    counts["brand"].isin(top_manufacturers)
]

# Store the processed data 
counts.to_json(
    "data/manufacturerProductionPeriod.json",
    orient="records",
    indent=2,
    force_ascii=False
)

# Check the selected manufacturers
print("Top 5 manufacturers:")
print(top_manufacturers)

print("\nManufacturers in final data:")
print(counts["brand"].unique())

print("\nProduction periods:")
print(counts["productionPeriod"].unique())

print("Processed data saved to data/manufacturerProductionPeriod.json")
