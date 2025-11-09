import pandas as pd
import numpy as np
import pyarrow 
import ssl
import time
import os

# Temporary fix.  Don't do this in production code. 
# I could not get pyarrow to work without this fix.
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

# load csv file into a data frame (done in class)
def load_csv(file_path):
    print(f"Reading CSV file from {file_path}...")
    start_time = time.time()
    
    try:
        df = pd.read_csv(file_path, engine="pyarrow")
        end_time = time.time()
        load_time = end_time - start_time
        print(f"CSV file loaded successfully in {load_time:.2f} seconds.")
        print(f"Number of rows: {len(df)}")
        print(f"Columns: {df.columns.tolist()}")

        df['order_date'] = pd.to_datetime(df['order_date'], format='%m/%d/%y', errors='coerce')
        df.fillna(0, inplace=True)
        df['sales'] = df['quantity'] * df['unit_price']

        required_columns = ['quantity', 'unit_price', 'order_date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing required columns: {missing_columns}")
        else:
            print("All required columns are present.")
        return df

    except FileNotFoundError as e:
        print(f"Error: The file {file_path} was not found. {e}")

    except pd.errors.EmptyDataError as e:
        print(f"Error: The file {file_path} is empty. {e}")
        return None
    
    except pd.errors.ParserError as e:
        print(f"Error: There was a parsing error while reading {file_path}. {e}")
        return None
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    

def display_rows(dataframe):
    while True:
        filtered_data = filter_by_date_range(dataframe) # filter data by date range first
        print("\nEnter the number of rows to display")
        print(f" - Enter a number 1 to {len(filtered_data)}")
        print(" - To see all rows, enter 'all'")
        print(" - To skip preview, press Enter")
        user_input = input("Your choice: ").strip().lower()

        if user_input == '':
            print("Skipping preview.")
            break
        elif user_input == 'all':
            print("Displaying all rows:")
            result = dataframe
            print(result)
            break
        elif user_input.isdigit() and 1 <= int(user_input) < len(dataframe):
            num_rows = int(user_input)
            print(f"Displaying the first {num_rows} rows:")
            result = dataframe.head(num_rows)
            print(result)
            break
        else:
            print("Invalid input. Please try again.")

    # requirement 1: ask to export
    if 'result' in locals():
        ask_to_export(result)


def exit_program(sales_data):
    print("Exiting the program. Goodbye!")
    exit(0)


def show_employees_by_region(sales_data):
    filtered_data = filter_by_date_range(sales_data) # filter data by date range first
    pivot_table = pd.pivot_table(
        filtered_data, 
        index='sales_region',
        values='employee_id',
        aggfunc=pd.Series.nunique
    )
    pivot_table.columns = ['Number of Employees']
    print("\nNumber of Employees by Region:")
    print(pivot_table)

    # requirement 1: ask to export
    ask_to_export(pivot_table)

    return pivot_table
#end of portion done in class

# requirement 7: function to filter by date range
def filter_by_date_range(pivot_table):
    # Make sure order_date is datetime
    pivot_table['order_date'] = pd.to_datetime(pivot_table['order_date'], errors='coerce')

    print("\nPlease select a date range to filter the data. Use proper date format (MM/DD/YYYY)")

    while True:
        try:
            start_date = input("Start date: ").strip() #ask user for start date
            end_date = input("End date: ").strip() #ask user for end date

            # Convert to datetime with exact date format
            start = pd.to_datetime(start_date, format='%m/%d/%Y')
            end = pd.to_datetime(end_date, format='%m/%d/%Y')

            if start > end:
                print("Start date cannot be after end date. Try again.")
                continue

            filtered_df = pivot_table[(pivot_table['order_date'] >= start) & # filter data frame
                                      (pivot_table['order_date'] <= end)]

            if filtered_df.empty: # check if filtered data frame is empty
                print("⚠️ No data found in that date range. Try again.")
                continue

            print(f"Data filtered to {len(filtered_df)} rows between {start_date} and {end_date}.") # inform user of result
            return filtered_df

        except ValueError: # catch invalid date format
            print("Invalid date format. Please use MM/DD/YYYY.")

# requirement 1: function to handle Excel export
def ask_to_export(pivot_table):
    while True:
        export_choice = input("\nWould you like to export these results to an Excel file? (y/n): ").strip().lower()
        if export_choice == 'y':
            filename = input("Enter a filename (without extension): ").strip() #asks user to input filename
            if not filename: # check for empty filename
                print("Invalid filename. Export cancelled.")
                return
            try:
                filename = f"{filename}.xlsx" # add .xlsx extension
                pivot_table.to_excel(filename, index=True) # export to excel
                print(f"Results successfully exported to '{filename}':)") # tell user export was successful
            except Exception as e: # catch any errors during export
                print(f"Error exporting to Excel: {e} :(")
            break
        elif export_choice == 'n': # user chose not to export
            print("Okay, not exporting.") # tell user not exporting
            break
        else:
            print("Please enter 'y' or 'n'.") # invalid input, ask again

# done in class
def display_menu(sales_data):
    menu_options = (
        ("Show the first n rows of sales data", display_rows),
        ("Show the number of employees by region", show_employees_by_region),
        ("Exit the program", exit_program)
    )

    print("\nAvailable Options:")
    for i, (description, _) in enumerate(menu_options, start=1):
        print(f"{i}. {description}")

    try:
        menu_len = len(menu_options)
        choice = int(input("Select an option (1 to {}): ".format(menu_len)))
        if 1 <= choice <= menu_len:
            action = menu_options[choice - 1][1]
            action(sales_data)
        else:
            print("Invalid choice. Please select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")    

# load the sales data
url = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"
sales_data = load_csv(url)

# main program loop
def main():
    while True:
        display_menu(sales_data)

if __name__ == "__main__":
    main()
