import json
from collections import defaultdict
import glob
import pip
install_requires = [
    "instaloader"
]

like_counts = defaultdict(int)
comment_counts = defaultdict(int)

# Loop through all post JSON files
for file in glob.glob("instagram_data/media/*.json"):
    with open(file, "r") as f:
        data = json.load(f)

    for item in data.get("media_map_data", {}).values():
        for like in item.get("likes", []):
            like_counts[like["username"]] += 1
        for comment in item.get("comments", []):
            comment_counts[comment["username"]] += 1

# Print engagement totals
print("=== Top Engagers ===")
for user in sorted(set(like_counts.keys()) | set(comment_counts.keys())):
    print(f"{user}: {like_counts[user]} likes, {comment_counts[user]} comments")
print("\n=== Likes Given ===")