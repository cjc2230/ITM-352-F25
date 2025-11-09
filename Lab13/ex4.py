# extract vehicle license data from the city of chicagos data portal
import pandas as pd
from sodapy import Socrata

# create socrata client
client = Socrata("data.cityofchicago.org", None)

# specify the JSON file for vehicle license data
json_file = "rr23-ymwb"
results = client.get(json_file, limit=500)

# convert to data frame
df = pd.DataFrame.from_records(results)
print(df.head())

vehicles_and_fuel_sources = df[['public_vehicle_number', 'vehicle_fuel_source']]
print(f"Vehicles and Fuel Sources:\n{vehicles_and_fuel_sources}")

vehicles_by_fuel_type = vehicles_and_fuel_sources.groupby('vehicle_fuel_source').count()
print(f"\nNumber of Vehicles by Fuel Type:\n")
print(vehicles_by_fuel_type)