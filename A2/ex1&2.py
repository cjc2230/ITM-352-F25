# read in the csv file and create a data frame print info
# pivot the data frame to show total sales by order type
# calculate total sales per order 
# show average sales by state
# sales type
import pandas as pd
import numpy as np
import pyarrow
import ssl
import time

# temporary fix don't do this in production code
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

def load_csv(file_path):
    print(f"Reading CSV file from {url}...")
    start_time = time.time()

    try: 
        df = pd.read_csv(file_path, engine = "pyarrow")
        end_time = time.time()
        loading_time = end_time - start_time
        print(f"CSV file loaded successfully in {loading_time:.2f} seconds.")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {df.columns.to_list()}")

        df["order_date"] = pd.to_datetime(df["order_date"], format='%m/%d/%y', errors='coerce')
        df.fillna(0, inplace=True)

        df["sales"] = df["quantity"] * df["unit_price"]
        required_columns = ['quantity', 'unit_price', 'order_date', 'sales']
        # check that the required columns are in df
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"WARNING: Missing columns in data frame: {missing_columns}")
        else:
            print("All required columns are present.")
        return df

    except FileNotFoundError as e:
        print(f"Error: The file {file_path} was not found. {e}")

    except pd.errors.EmptyDataError as e:
        print(f"Error: The file {file_path} is empty. {e}")
        return None

    except pd.errors.ParserError as e:
        print(f"Error: The file {file_path} could not be parsed. {e}")
        return None

    except Exception as e:
        print(f"Error: An unexpected error occurred while reading {file_path}. {e}")
        return None
    
url = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"
sales_data = load_csv(url)

#check if the data frame is loaded successfully
if sales_data is not None:
    print("\nThe first 5 rows of the data frame:")
    print(sales_data.head())

    #print("\nData frame info:")
    #print(sales_data.info())
else:
    print("Failed to load data frame.")