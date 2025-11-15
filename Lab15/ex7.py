# create a scatter plot of fares and tips
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

trips_df = pd.read_json("../Trips from area 8.json")

fare_series = trips_df.fare
trip_series = trips_df.trip_miles

# filter out trips with zero miles
non_zero_trips = trips_df[trips_df.trip_miles > 0]

# filter out trips with less than two miles
valid_trips = non_zero_trips[non_zero_trips.trip_miles >= 2]

fig = plt.figure() # not strictly necessary

# create 3D scatter plot
ax = fig.add_subplot(111, projection='3d')

plt.plot(valid_trips.fare, valid_trips.trip_miles, linestyle='none', marker='.')
plt.title("trip miles by fare")
plt.xlabel("fare in $")
plt.ylabel("trip miles")
plt.show()