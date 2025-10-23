# read 1000 lines of taxi data from the taxi_1000.csv file
# calculate total of all fares and average fare amount and the maximum trip distance

import csv

with open("taxi_1000.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # Skip header row
    

    total_fare = 0.0
    max_distance = 0.0
    average_fare = 0.0
    num_rows = 0

    for line in csv_reader:
        if len(line) > 10:  
            trip_fare = float(line[10])
            distance = float(line[5])
            if trip_fare > 10:
                total_fare += trip_fare
                num_rows += 1
                if (distance > max_distance):
                    max_distance = distance

    if num_rows > 0:
        print(f"We read {num_rows} rows")
        print(f"Total fare amount: ${total_fare:.2f}")
        print(f"Average fare amount: ${total_fare / num_rows:.2f}")
        print(f"Maximum trip distance: {max_distance:.2f} miles")
    else:
        print("No trips with fare over $10 were found.")