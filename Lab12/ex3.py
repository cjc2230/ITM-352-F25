# read in the csv file and create a data frame print info
# pivot the data frame to show total sales by order type
# calculate total sales per order 
# show average sales by state
# sales type
import pandas as pd
import numpy as np
import ssl

# temporary fix don't do this in production code
ssl._create_default_https_context = ssl._create_unverified_context
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

url = "https://drive.google.com/uc?id=1ujY0WCcePdotG2xdbLyeECFW9lCJ4t-K"

try: 
    df = pd.read_csv(url, engine = "pyarrow")
    df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')
    df["sales"] = df["quantity"] * df["unit_price"]

    # create a pivot table aggregating sales by region and order type
    pivot_table = pd.pivot_table(df, 
                                 values="sales",
                                 index="customer_state", 
                                 columns=["customer_type", "order_type"],
                                 aggfunc=np.mean, 
                                 margins=True, # add a total column and row
                                 margins_name ="Total sales",)
    print(pivot_table)

except Exception as e:
    print(f"Error reading with pyarrow: {e}")
