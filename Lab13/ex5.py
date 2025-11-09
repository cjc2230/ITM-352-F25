# get a json file from the city of chicagos data portal and analyze driver types
#  make use of the sequel like query capabilities of portal
import requests
import pandas as pd

# create a rest query that returns the count of driver licenses by driver type
search_results = requests.get("https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type")
results_json = search_results.json()

# convert the json results to a data frame
results_df = pd.DataFrame.from_records(results_json)
results_df.columns = ['count', 'driver_type']
results_df = results_df.set_index('driver_type')

# print the results
print (results_df)