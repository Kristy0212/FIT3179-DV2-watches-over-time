import pandas as pd 
df = pd.read_csv(
    "data/Watches.csv",
    low_memory=False
)

# Convert price to number 
df["price_numeric"] = (
    df["price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["price_numeric"] = pd.to_numeric(
    df["price_numeric"],
    errors="coerce"
)

# Extract production year
df["year"] = (
    df["yop"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)

# Remove missing / invalid values 
df = df.dropna(
    subset=["price_numeric", "year"]
)

df = df[
    (df["price_numeric"] > 0) &
    (df["year"] > 0)
]

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

# Keep only the fields needed for the chart
price_data = df[
    [
        "brand",
        "model",
        "year",
        "productionPeriod",
        "price_numeric"
    ]
]

price_data.to_json(
    "data/watchPriceEvolution.json",
    orient="records",
    indent=2,
    force_ascii = False
)

print("Processed data saved to data/watchPriceEvolution.json")
print("Number of records:", len(price_data))