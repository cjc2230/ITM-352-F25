# create a scatter plot of fares and tips
import matplotlib.pyplot as plt
import pandas as pd

trips_df = pd.read_json("../Trips from area 8.json")

fare_series = trips_df.fare
trip_series = trips_df.trip_miles

fig = plt.figure() # not strictly necessary

plt.plot(fare_series, trip_series, linestyle='none', marker='v', color = 'cyan', alpha = 0.2 )
plt.title("trip miles by fare")
plt.xlabel("fare in $")
plt.ylabel("trip miles")
plt.show()