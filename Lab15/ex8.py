import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

trips_df = pd.read_json("../Trips from area 8.json")

# Create a cross-tabulation (contingency table)
heatmap_data = pd.crosstab(
    trips_df['pickup_community_area'],
    trips_df['dropoff_community_area'],
    dropna=False
)

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(
    heatmap_data,
    cmap='Blues',
    cbar_kws={'label': 'Number of Trips'}
)

plt.title("Heatmap of Pickup vs Dropoff Community Areas")
plt.xlabel("Dropoff Community Area")
plt.ylabel("Pickup Community Area")
plt.xticks(rotation=90)
plt.yticks(rotation=0)

plt.tight_layout()
plt.show()