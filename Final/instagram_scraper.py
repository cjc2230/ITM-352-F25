import difflib
from typing import Dict, List, Optional, Tuple

# The club's official list of usernames (keys) and full names (values).
# This data is derived from the 'IG_point_tracker.xlsx - Sheet1.csv' you provided.
MEMBER_DIRECTORY: Dict[str, str] = {
    "aiidencc": "Aiden Cheung",
    "aileee.m": "Ailee Watanabe",
    "alyssa.caballero": "Alyssa Grace Caballero",
    "bradyj_01": "Brady Johnson",
    "calistafujitani": "Calista Fujitani",
    "_carleem": "Carlee Marcello",
    "cj.cornforth": "Chloe Cornforth",
    "christian.erice": "Christian Erice",
    "christinaadoan": "Christina Doan",
    "dacksvic": "Daxton Vickers",
    "daytonn.b": "Dayton Barsatan",
    "destinyyasuhara": "Destiny Yasuhara",
    "di21on.t": "Dillon Tom",
    "e1leen.l": "Eileen Liu",
    "emersondives": "Emerson Heaton",
    "ethanshekk": "Ethan Shek",
    "hyunnycha": "Hyunny Cha",
    "jamie.hirano": "Jamie Hirano",
    "jennaamarii": "Jenna Weigelt",
    "kaigardiner_": "Kai Gardiner",
    "k4nunu": "Kanunu Potts",
    "kellie.rother": "Kellie Rother",
    "kou.nishiyama": "Kou Nishiyama",
    "kxchun": "Kristen Chun",
    "lara_ho1": "Lara Miyakawa Ho",
    "lorissa.mach": "Lori Mach",
    "mxwll.lee": "Maxwell Lee",
    "_michelletlu": "Michelle Lu",
    "nahtaleh": "Natalie Hope Pagdilao",
    "natereitzell": "Nathan Reitzell",
    "noah.dasani": "Noah Sasaki",
    "oceankishimoto": "Ocean Kishimoto",
    "reeceorsmthn": "Reece Ichinose",
    "riochoppa": "Rio Chopot",
    "rvxane_": "Roxane Ruan",
    "russqln": "Russell Quelnan",
    "s.am.lee3": "Samuel Lee"
    # Note: Users without usernames like "David Wetter" and "Katie Huynh" are excluded from the directory
}


def find_member_match(input_username: str, members: Dict[str, str], threshold: float = 0.8) -> Tuple[Optional[str], Optional[str], float]:
    """
    Attempts to match an input username (from a post interaction) to an official
    member username using fuzzy string matching. This function handles both exact
    and near-match (typo) lookups.

    Args:
        input_username (str): The username found on an Instagram post (e.g., from a comment).
        members (Dict[str, str]): The official member directory {username: full_name}.
        threshold (float): The minimum similarity score (0.0 to 1.0) required for a match.

    Returns:
        Tuple[str | None, str | None, float]: 
            (matched_username, matched_full_name, similarity_score)
            Returns (None, None, 0.0) if no match is found above the threshold.
    """
    
    # 1. Exact Match Check (Highest priority, fastest lookup)
    if input_username in members:
        return input_username, members[input_username], 1.0

    # 2. Fuzzy Match Check
    best_match = None
    highest_score = 0.0

    member_usernames = list(members.keys())
    
    # Use difflib's SequenceMatcher for comparison
    matcher = difflib.SequenceMatcher()
    
    for official_username in member_usernames:
        # Use lowercase for case-insensitive comparison
        matcher.set_seqs(input_username.lower(), official_username.lower()) 
        score = matcher.ratio()

        if score > highest_score:
            highest_score = score
            best_match = official_username

    # 3. Return the result if it meets the threshold
    if best_match and highest_score >= threshold:
        return best_match, members[best_match], highest_score
    else:
        return None, None, 0.0


def get_full_name_from_username(username: str, members: Dict[str, str]) -> str:
    """
    Converts a recognized club member's username to their full name using
    exact matching and a fuzzy fallback.
    
    Handles blank/empty usernames by returning a designated non-member tag.

    Args:
        username (str): The username to look up.
        members (Dict[str, str]): The official member directory {username: full_name}.

    Returns:
        str: The member's full name, or a formatted string indicating a non-member.
    """
    # 1. CRITICAL: Filter out blank/empty usernames immediately
    if not username or username.strip() == "":
        return "[NON_MEMBER] (BLANK/MISSING USERNAME)"

    # 2. Perform Match (Exact or Fuzzy)
    # find_member_match handles the exact match first for efficiency and covers all lookups.
    matched_username, full_name, score = find_member_match(username, members)

    if full_name:
        # If a non-exact, fuzzy match occurred, print a helpful INFO message.
        if score < 1.0:
            print(f"INFO: Fuzzy match found for '{username}'. Used official name: '{full_name}' (Score: {score:.2f})")
        
        # Return the official full name
        return full_name
    else:
        # If no match (exact or fuzzy) was found
        return f"[NON_MEMBER] {username}"


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Testing Member Matching Module ---")
    
    # Test cases for matching
    test_users = [
        "aiidencc",      # Perfect match
        "aiiden c",      # Close match (typo/extra space)
        "natereitzel",   # Possible typo (missing 'l')
        "john_doe_123"   # Non-member
    ]

    for user in test_users:
        match_username, full_name, score = find_member_match(user, MEMBER_DIRECTORY)
        
        print(f"\nInput User (Fuzzy Test): '{user}'")
        if match_username:
            print(f"  -> MATCHED: {match_username} ({full_name})")
            print(f"  -> Confidence Score: {score:.2f} (Threshold: 0.80)")
        else:
            print(f"  -> NO FUZZY MATCH found above threshold 0.80.")

    print("\n--- Testing Full Name Conversion Module ---")
    
    # Test cases for conversion
    conversion_users = [
        "alyssa.caballero", # Exact match (should not print INFO)
        "k4nunu",           # Exact match (should not print INFO)
        "k4nunuu",          # Fuzzy match should resolve this (should print INFO)
        "",                 # Blank username check (NEW)
        "  ",               # Whitespace username check (NEW)
        "BEST_alumni_fan"   # Non-member
    ]
    
    for user in conversion_users:
        official_name = get_full_name_from_username(user, MEMBER_DIRECTORY)
        print(f"Input: '{user}' -> Output: '{official_name}'")