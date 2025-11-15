# create a scatter plot of fares and tips
import matplotlib.pyplot as plt
import pandas as pd

trips_df = pd.read_json("../Trips_Fri07072017T4 trip_miles gt1.json")

fare_series = trips_df.fare
trip_series = trips_df.tips

fig = plt.figure() # not strictly necessary

plt.plot(fare_series, trip_series, linestyle='none', marker='.')
plt.title("tips by fare")
plt.xlabel("fare in $")
plt.ylabel("tips in $")
plt.show()