# parse the UHM SHIDLER department of ITM department page and extract names of faculty members
import urllib.request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

itm_url = "https://shidler.hawaii.edu/itm/people"

itm_html = urllib.request.urlopen(itm_url)
html_to_parse = BeautifulSoup(itm_html, 'html.parser')

pretty_html = html_to_parse.prettify()
lines = pretty_html.splitlines()
num_to_print = 10

# print the first few lines of the prettified HTML
for line in lines[:num_to_print]:
    print(line)

#find and print all faculty names
list_of_faculty = html_to_parse.find_all('h2', class_='title')

# create a list with just the names 
itm_faculty = []
for element in list_of_faculty:
    itm_faculty.append(element.text)
    print (element.text)

print("Number in the initial list:", len(itm_faculty))
unique_itm_faculty = list(set(itm_faculty))
print("Number of unique faculty names:", len(unique_itm_faculty))