# create a bar chart from the trip miles data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

trips_df = pd.read_json("../Trips from area 8.json")

# grab the tips and payment type colums from data frame
trips_df = trips_df.dropna()
trips_df = trips_df[["tips", 'payment_type']]
trips_df = trips_df.astype({'tips': float})
trip_df = trips_df.set_index('payment_type')

trips_by_payment = trip_df.groupby('payment_type').sum()

x_labels = pd.Series(trips_by_payment.index.values)
y_labels = pd.Series(trips_by_payment['tips'].values)

bars = np.array(range(len(x_labels)))
plt.xticks(bars, x_labels, colors='red', fortweight='bold')

plt.bar(bars, y_labels)

plt.title("Total Tips by Payment Type")
plt.xlabel("Payment Type")
plt.ylabel("tips in $")
plt.show()