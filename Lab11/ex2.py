# create a data frame from individual lists
# do some simple statistics on data mine
import pandas as pd

# List of individuals' ages
ages = [25, 30, 22, 35, 28, 40, 50, 18, 60, 45]


#Lists of individuals' names and genders
names = ["Joe", "Jaden", "Max", "Sidney", "Evgeni", "Taylor", "Pia", "Luis", "Blanca", "Cyndi"]
gender = ["M", "M", "M", "F", "M", "F", "F", "M", "F", "F"]

# create a dictionary from the lists
dict = zip(ages, gender)

# convert the dictionary to a data frame with names as the keys
df = pd.DataFrame(dict, index=names, columns= ["Age", "Gender"])
print(df)
summary = df.describe()
print(summary)

# calculate average age by gender
average_age_by_gender = df.groupby("Gender")["Age"].mean()
print(average_age_by_gender)