# Read in a CSV file and create a dataframe.  Print some info.
# Pivot the dataframe to show total sales by order type.
# Calculate total sales per order.  Show average sales by state
# and sales type.
import pandas as pd
import numpy as np
import pyarrow 
import ssl
import time

# Temporary fix.  Don't do this in production code.
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)


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
        # Check that the required columns are in df
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
        print("\nEnter the number of rows to display")
        print(f" - Enter a number 1 to {len(dataframe)}")  
        print(" - To see all rows, enter 'all'")
        print(" - To skip preview, press Enter")
        user_input = input("Your choice: ").strip().lower()

        if user_input == '':
            print("Skipping preview.")
            break
        elif user_input == 'all':
            print("Displaying all rows:")
            print(dataframe)
            break
        elif user_input.isdigit() and 1 <= int(user_input) < len(dataframe):
            num_rows = int(user_input)
            print(f"Displaying the first {num_rows} rows:")
            print(dataframe.head(num_rows))
            break
        else:
            print("Invalid input. Please try again.")

def exit_program(sales_data):
    print("Exiting the program. Goodbye!")
    exit(0)

def show_employees_by_region(sales_data):
    pivot_table = pd.pivot_table(sales_data, index='sales_region', values='employee_id', aggfunc=pd.Series.nunique)
    pivot_table.columns = ['Number of Employees']  # Rename the colummn for readability
    print("\nNumber of Employees by Region:")
    print(pivot_table)
    return pivot_table


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

url = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"
sales_data = load_csv(url)


def main():
    # Main program loop
    while True:
        display_menu(sales_data)


if __name__ == "__main__":
    main()
         