import csv
import difflib
import pandas as pd
from typing import List, Dict, Any, Tuple

# --- Configuration ---
MEMBER_CSV_FILE = 'F25IGPointTracking.xlsx - Sheet1.csv'
# The required minimum similarity score (0.0 to 1.0)
# A value of 0.8 is usually a good starting point for finding typos.
FUZZY_MATCH_THRESHOLD = 0.8 
# ---------------------


def match_usernames(raw_usernames: List[str], official_list: List[str]) -> List[str]:
    """
    Utility function to clean a list of scraped usernames by:
    1. Removing non-member accounts.
    2. Correcting typos using fuzzy matching against the official list.
    
    Returns a list of cleaned, officially matched member usernames (allowing duplicates).
    Duplicates are important for correctly counting multiple comments.
    """
    matched_members = []
    
    # Pre-calculate matcher for efficiency if the lists are large
    
    for raw_user in raw_usernames:
        raw_user_lower = raw_user.lower().replace('@', '').strip()
        
        # 1. Direct Match Check
        if raw_user_lower in official_list:
            matched_members.append(raw_user_lower)
            continue
            
        # 2. Fuzzy Match Check (for typos)
        # difflib.get_close_matches is efficient for finding the single best match
        close_matches = difflib.get_close_matches(
            raw_user_lower, 
            official_list, 
            n=1, 
            cutoff=FUZZY_MATCH_THRESHOLD
        )
        
        if close_matches:
            # It's a member with a typo, use the official, corrected username
            official_match = close_matches[0]
            matched_members.append(official_match)
        # Else: It's not a member or the typo is too severe, so discard it.
            
    return matched_members


def fuzzy_match_members(post_data_interaction_lists: Dict[str, List[str]], roster_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    The main matching function called by main_tracker.py.
    It processes raw interaction lists against the member roster using fuzzy matching.

    Args:
        post_data_interaction_lists: A dictionary with keys 'likers', 'commenters', 'tagged_users' 
                           and lists of raw usernames as values. (From scraper)
        roster_df: The DataFrame containing the official member roster, including a 
                   'Username' column. (From initialization)

    Returns:
        A dictionary with the same keys, but containing only the officially matched 
        usernames (duplicates preserved). This is passed to the point calculator.
    """
    # Create the authoritative list of official usernames from the DataFrame
    if 'Username' not in roster_df.columns:
        print("🚨 ERROR: Roster DataFrame is missing the 'Username' column for matching.")
        return {key: [] for key in post_data_interaction_lists.keys()}

    official_usernames = roster_df['Username'].str.lower().tolist()
    
    # Store the results, preserving duplicates (important for comments)
    matched_interactions = {key: [] for key in post_data_interaction_lists.keys()}
    
    print(f"  -> Starting member matching against {len(official_usernames)} official usernames...")
    
    for interaction_type, raw_usernames in post_data_interaction_lists.items():
        if not raw_usernames:
            continue
            
        # Call the utility function to perform the matching
        matched_list = match_usernames(raw_usernames, official_usernames)
        matched_interactions[interaction_type] = matched_list
        
        unique_matches = len(set(matched_list))
        total_matches = len(matched_list)
        print(f"    - {interaction_type}: Found {total_matches} total interactions ({unique_matches} unique members).")
        
    print("  -> Matching complete.")
    return matched_interactions