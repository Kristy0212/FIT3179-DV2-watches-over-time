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

# Remove missing / invalid prices
df = df.dropna(
    subset=["brand", "price_numeric"]
)

df = df[
    df["price_numeric"] > 0
]

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

#Calculate median and avergae price
price_comparison = (
    df.groupby("brand")["price_numeric"]
    .agg(
        medianPrice="median",
        averagePrice="mean",
        watchCount="count"
    )
    .reset_index()
)

# Sort by median price
price_comparison = price_comparison.sort_values(
    "medianPrice",
    ascending=False
)

price_comparison.to_json(
    "data/manufacturerPriceComparison.json",
    orient="records",
    indent=2,
    force_ascii=False
)

print(
    "Number of manufacturers:",
    len(price_comparison)
)

print(price_comparison)