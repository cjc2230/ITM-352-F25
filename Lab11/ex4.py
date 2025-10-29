# read json file of taxi trip data 
# create a data frame
# calculate the median fare
import pandas as pd

taxi_df = pd.read_json("Taxi_Trips.json")

# print a summary of the data frame
print(taxi_df.describe())
print(taxi_df.head())

# print the median fare
print(f"Median fare amount: ${taxi_df['fare'].median():.2f}")
