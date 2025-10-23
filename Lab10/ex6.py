# read a file of questions from a json file and save them in a dictionary, then print the dictionary
import json

# specify the json file name
JSON_file = "quiz.json"

# open the json file and load the questions into a dictionary
with open(JSON_file, "r") as json_file:
    data = json.load(json_file)

print(data)