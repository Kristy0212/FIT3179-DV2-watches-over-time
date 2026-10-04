import pandas as pd 

# Load dataset 
df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Extract the production year
df["year"] = (
    df["yop"].astype(str).str.extract(r"(\d{4})")[0]
)

df["year"] = pd.to_numeric(
    df["year"],errors="coerce"
)

# Extract the first numeric measurement from size
df["size_mm"] = (
    df["size"]
    .astype(str)
    .str.extract(r"(\d+(?:\.\d+)?)")[0]
)

df["size_mm"] = pd.to_numeric(
    df["size_mm"],
    errors="coerce"
)

df = df.dropna(subset=["year", "size_mm"])
df["year"] = df["year"].astype(int)

# Keep reasonable watch sizes
df = df[
    (df["size_mm"] >= 15) &
    (df["size_mm"] <= 60)
]

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

# Select the columns needed for the chart 
size_data = df[
    ["brand", "model", "year", "productionPeriod", "size_mm"]
]

# Store processed data 
size_data.to_json(
    "data/watchSizeDistribution.json",
    orient="records",
    indent=2,
    force_ascii=False
)

print("Processed data saved to data/watchSizeDistribution.json")
print("Number of records:", len(size_data))