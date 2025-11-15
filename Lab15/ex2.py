# create a histogram from the trip miles data
import matplotlib.pyplot as plt
import pandas as pd

# read the data file and create a dataframe
trips_df = pd.read_json("../Trips from area 8.json")
trips_miles_series = trips_df.trip_miles

fig = plt.figure() # not strictly necessary

# create the histogram
plt.hist(trips_miles_series)
plt.title("Distribution of Trip Miles")
plt.xlabel("Trip Miles")
plt.ylabel("Frequency")

plt.show()