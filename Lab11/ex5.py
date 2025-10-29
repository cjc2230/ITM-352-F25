import pandas as pd

df_homes = pd.read_csv("homes_data.csv")

# print the shape of the data frame
shape = df_homes.shape
print(f"the homes data has {shape[0]} rows and {shape[1]} columns")

# select only the homes with more than 500 sqft living area
df_big_homes = df_homes[df_homes.units >= 500]

# drop unnecessary columns and print first 10 rows
df_big_homes = df_big_homes.drop(columns=["id", "easement"])
print(df_big_homes.head(10))

# look at data types
print(df_big_homes.info())

#convert columns to appropriate data types
df_big_homes['sale_price'] = pd.to_numeric(df_big_homes['sale_price'], errors='coerce')
df_big_homes['land_sqft'] = pd.to_numeric(df_big_homes['land_sqft'], errors='coerce')
df_big_homes['gross_sqft'] = pd.to_numeric(df_big_homes['gross_sqft'], errors='coerce')

# drop rows with missing values
df_big_homes = df_big_homes.dropna()
# drop duplicate rows
df_big_homes = df_big_homes.drop_duplicates()

# print out first 10 rows after cleaning
print(" after dropping nulls and duplicates\n", df_big_homes.head(10))

df_big_homes = df_big_homes[df_big_homes['sale_price'] > 0]
print(f" after dropping zero sale price\n", df_big_homes.head(10))

# calculate average sale price
average_price = df_big_homes['sale_price'].mean()
print(f" average sale price of homes with more than 500 sqft living area: ${average_price:,.2f}")