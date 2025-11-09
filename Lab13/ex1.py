# scrape data from the city of chicago data portal
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
url = "https://data.cityofchicago.org/Historic-Preservation/Landmark-Districts/zidz-sdfj/about_data"

# open the web page 
print ("Opening URL: ", url)
web_page = urllib.request.urlopen(url)  

# iterate through each line and search for title tags 
for line in web_page: 
    line = line.decode("utf-8")  # decode the bytes to string
    if "<title>" in line:        # search string for title
        print (line)