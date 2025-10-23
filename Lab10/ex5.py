# save the dictionary of quiz questions as a json file
import json

QUESTIONS = {
    "What is the airspeed of an unladen swallow in miles per hour?": ["12", "13", "24", "36", "48"],
    "What is the capital of Texas?": ["Austin", "Dallas", "Houston", "Waco"],
    "The last supper was a famous painting by which artist?": ["Da Vinci", "Michelangelo", "Raphael"],
    "Which classic novel opens with the line 'Call me Ishmael'?": ["Moby Dick", "Pride and Prejudice", "1984", "To Kill a Mockingbird"]
}

JSON_file = "quiz.json"

with open(JSON_file, "w") as f:
    json.dump(QUESTIONS, f, indent=4)

print(f"Saved quiz questions to {JSON_file}")
