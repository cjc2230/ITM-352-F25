# read csv file of employee data
import csv

csv_filename = "my_custom_spreadsheet.csv"
salaries = []

with open(csv_filename, newline="") as csv_file: 
    reader = csv.reader(csv_file)
    headers = next(reader)  # Skip the header row
    print(f"Headers: {headers}")

    salary_index = headers.index("Annual_Salary")
    for row_data in reader:
        salaries.append((float(row_data[salary_index])))

if salaries:
    average_salary = sum(salaries) / len(salaries)
    max_salary = max(salaries)
    min_salary = min(salaries)

    print(f"Average Salary: ${average_salary:,.2f}")
    print(f"Maximum Salary: ${max_salary:,.2f}")
    print(f"Minimum Salary: ${min_salary:,.2f}")

else:
    print("No salary data found.")