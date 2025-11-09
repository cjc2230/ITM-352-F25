# open a url from the us treasury and extract its information as a data frame 
# print the one month treasury rate information

import pandas as pd 
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202410"

print ("Opening URL:", url)
try: 
    tables = pd.read_html(url)
    int_rate_table = tables[0] # assuming the first table is the one we want
    #print (int_rate_table.columns)
    #print (int_rate_table.head())

    # print the one month treasury rates
    print ("\nOne Month Treasury Rates:")
    for index, row in int_rate_table.iterrows():
        print (f"Index:{index}, Date: {row['Date']}, 1 Month Rate: {row['1 Mo']}%")

except Exception as e:
    print (f"Error reading The URL or parsing HTML:", e)
    exit()