# read csv file of employee data
import csv
import os

csv_filename = "my_custom_spreadsheet.csv"

def analyze_salaries(filename):
    print(f"Analyzing salary data from {filename}...")
   
    salaries = []
    with open(csv_filename, newline="") as csv_file: 
        reader = csv.reader(csv_file)
        headers = next(reader)  # Skip the header row
        print(f"Headers: {headers}")

        salary_index = headers.index("Annual_Salary")
        for row_data in reader:
            salaries.append((float(row_data[salary_index])))

        average_salary = sum(salaries) / len(salaries)
        max_salary = max(salaries)
        min_salary = min(salaries)

        print(f"Average Salary: ${average_salary:,.2f}")
        print(f"Maximum Salary: ${max_salary:,.2f}")
        print(f"Minimum Salary: ${min_salary:,.2f}")

if os.path.exists(csv_filename) and os.access(csv_filename, os.R_OK):
        analyze_salaries(csv_filename)
else:
        print(f"File {csv_filename} does not exist or is not readable.")
