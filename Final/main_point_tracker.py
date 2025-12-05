import pandas as pd
import os
import time
import difflib # Added for fuzzy matching
from tabulate import tabulate 
from typing import List, Dict, Any, Tuple

# --- Configuration ---
# Assuming the user has this file saved in the execution directory.
# NOTE: Ensure the actual CSV or XLSX file is in the same directory.
MEMBER_ROSTER_FILE = 'F25IGPointTracking - Sheet1.csv' 
LEADERBOARD_OUTPUT_FILE = 'leaderboard.csv'
FUZZY_MATCH_THRESHOLD = 0.8 # Minimum similarity score
MAX_POINTS_PER_COMMENT = 4
POINTS = { "likers": 1, "commenters": 1, "tagged_users": 5 }
# ---------------------

# --- MOCK INTERACTION DATA (Used for testing point calculation without web scraping) ---
# Each item in the list represents the interactions from a single Instagram post.
MOCK_POST_INTERACTIONS = [
    {
        "url": "https://www.instagram.com/p/Post-A/",
        "interaction_lists": {
            # aiidencc: 1 like (1 pt)
            # k4nunu: 1 like (1 pt), 3 comments (3 pts, max 4) -> 4 points total
            # _carleem: 1 tag (5 pts)
            "likers": ["aiidencc", "bradyj_01", "non_member_1", "k4nunu", "eileen.l"],
            "commenters": ["aiidencc", "k4nunu", "aiidencc", "typo_user", "k4nunu", "k4nunu"], 
            "tagged_users": ["_carleem", "club_member_y", "jennaamarii", "aiidencc"] 
        }
    },
    {
        "url": "https://www.instagram.com/p/Post-B/",
        "interaction_lists": {
            # aiidencc: 1 like (1 pt)
            # jennaamarii: 1 like (1 pt)
            "likers": ["aiidencc", "typo_for_jennaamarii", "another_non_member"], 
            "commenters": ["jennaamarii"], # 1 comment (1 pt)
            "tagged_users": [] 
        }
    },
]
# -----------------------------------------------------------------------------------


# --- CORE LOGIC FUNCTIONS ---

def initialize_roster(file_path: str) -> pd.DataFrame:
    """Loads the member roster file and ensures required columns exist."""
    print(f"Loading member roster from {file_path}...")
    roster_df = pd.DataFrame()

    # Define standard point columns for initialization
    point_columns = ['Likes 1 pt', 'Comments 1pt (4 max)', 'Story Repost 5 pt', 
                     'Story Tag 5 pt', 'Post Tag 5 pt', 'Linkedin 5 pt', 'Total']

    try:
        # ATTEMPT 1: Try reading as CSV
        if os.path.exists(file_path):
            roster_df = pd.read_csv(file_path)
            if roster_df.empty or roster_df.shape[0] == 0:
                 raise ValueError("CSV read resulted in empty DataFrame.")

            print("✅ Successfully read file as CSV.")

        # ATTEMPT 2: Try reading as Excel if CSV fails or file not found
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    except Exception as e:
        print(f"⚠️ Read failed ({e}). Attempting to read as Excel...")
        try:
            # Assume the actual Excel file is named without the '- Sheet1.csv' suffix
            excel_file_path = file_path.split(' - Sheet1.csv')[0] + '.xlsx'
            sheet_name = 'Sheet1' if 'Sheet1' in file_path else 0 

            roster_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            if roster_df.empty or roster_df.shape[0] == 0:
                 raise ValueError("Excel file read resulted in empty DataFrame.")

            print(f"✅ Successfully read file as Excel from '{excel_file_path}'.")
        except Exception as e_excel:
            print(f"🚨 FINAL FAILURE: Could not read roster file. Details: {e_excel}")
            return pd.DataFrame(columns=['First Name', 'Last Name', 'Username'] + point_columns)

    # Post-load cleanup and initialization (Runs only if roster_df is NOT empty)
    roster_df.columns = roster_df.columns.str.strip()

    if 'Username' not in roster_df.columns:
        print("🚨 ERROR: The essential 'Username' column is missing from the roster file.")
        return pd.DataFrame(columns=['First Name', 'Last Name', 'Username'] + point_columns)
    
    # CRUCIAL FIX: Ensure the Username column is treated as a string and missing values (NaN/float) 
    # are replaced with empty strings, preventing the 'object of type 'float' has no len()' error.
    roster_df['Username'] = roster_df['Username'].astype(str).str.strip().fillna('')
        
    for col in point_columns:
        if col not in roster_df.columns:
            roster_df[col] = 0
            
    # Ensure point columns are numeric
    for col in point_columns:
        roster_df[col] = pd.to_numeric(roster_df[col], errors='coerce').fillna(0).astype(int)

    return roster_df

def match_usernames(raw_usernames: List[str], official_list: List[str]) -> List[str]:
    """Utility function to clean a list of scraped usernames using fuzzy matching."""
    matched_members = []
    
    for raw_user in raw_usernames:
        # Since raw_user comes from the mock list (or the scraper), it should be a string.
        raw_user_lower = raw_user.lower().replace('@', '').strip()
        
        if raw_user_lower in official_list:
            matched_members.append(raw_user_lower)
            continue
            
        close_matches = difflib.get_close_matches(
            raw_user_lower, 
            official_list, 
            n=1, 
            cutoff=FUZZY_MATCH_THRESHOLD
        )
        
        if close_matches:
            # If fuzzy match is found, use the official username
            matched_members.append(close_matches[0])
            
    return matched_members


def fuzzy_match_members(post_data_interaction_lists: Dict[str, List[str]], roster_df: pd.DataFrame) -> Dict[str, List[str]]:
    """Processes raw interaction lists against the roster using fuzzy matching."""
    # Filter out empty strings that result from cleaning NaN values in the roster, then convert to lowercase.
    official_usernames = [u.lower() for u in roster_df['Username'].tolist() if u]
    matched_interactions = {key: [] for key in post_data_interaction_lists.keys()}
    
    print(f"  -> Starting member matching against {len(official_usernames)} official usernames...")
    
    for interaction_type, raw_usernames in post_data_interaction_lists.items():
        if not raw_usernames:
            continue
            
        matched_list = match_usernames(raw_usernames, official_usernames)
        matched_interactions[interaction_type] = matched_list
        
        unique_matches = len(set(matched_list))
        total_matches = len(matched_list)
        print(f"    - {interaction_type}: Found {total_matches} total interactions ({unique_matches} unique members).")
        
    print("  -> Matching complete.")
    return matched_interactions


def calculate_points(roster_df: pd.DataFrame, matched_interactions: Dict[str, List[str]]) -> pd.DataFrame:
    """Calculates points based on matched interactions and updates the roster DataFrame."""
    
    # 1. Process Likers (1 point each)
    print("  -> Calculating points for LIKES (1 pt each)...")
    # Only count one like per user per post
    for username in set(matched_interactions.get("likers", [])): 
        member_index = roster_df[roster_df['Username'].str.lower() == username.lower()].index
        if not member_index.empty:
            roster_df.loc[member_index, 'Likes 1 pt'] += POINTS["likers"]

    # 2. Process Commenters (1 point each, max 4 per post)
    print(f"  -> Calculating points for COMMENTS (1 pt each, max {MAX_POINTS_PER_COMMENT} max)...")
    comment_counts = pd.Series(matched_interactions.get("commenters", [])).value_counts()
    
    for username, count in comment_counts.items():
        member_index = roster_df[roster_df['Username'].str.lower() == username.lower()].index
        if not member_index.empty:
            points_awarded = min(count, MAX_POINTS_PER_COMMENT) * POINTS["commenters"]
            roster_df.loc[member_index, 'Comments 1pt (4 max)'] += points_awarded
            
    # 3. Process Tagged Users (5 points each, one per post tag)
    print(f"  -> Calculating points for POST TAGS ({POINTS['tagged_users']} pts each)...")
    unique_tagged_users = set(matched_interactions.get("tagged_users", []))
    
    for username in unique_tagged_users:
        member_index = roster_df[roster_df['Username'].str.lower() == username.lower()].index
        if not member_index.empty:
            roster_df.loc[member_index, 'Post Tag 5 pt'] += POINTS["tagged_users"]


    # 4. Recalculate Total Points
    point_columns = ['Likes 1 pt', 'Comments 1pt (4 max)', 'Story Repost 5 pt', 
                     'Story Tag 5 pt', 'Post Tag 5 pt', 'Linkedin 5 pt']
                     
    valid_cols = [col for col in point_columns if col in roster_df.columns]
    
    roster_df['Total'] = roster_df[valid_cols].fillna(0).sum(axis=1)

    print("  -> Points for this post successfully calculated and accumulated.")
    return roster_df


# --- MAIN EXECUTION ---
def run_tracker():
    """Main function to run the Instagram point tracker using mock data."""
    
    # 1. Initialize Roster
    roster_df = initialize_roster(MEMBER_ROSTER_FILE)
    if roster_df.empty or roster_df.shape[0] == 0:
        print("\nTracker halted: Roster is empty or invalid. Cannot proceed.")
        return

    try:
        # Prepare a copy of the roster for point accumulation
        initial_roster_copy = roster_df.copy()
        
        # Reset all dynamic point columns to 0 for a fresh run
        point_columns_to_reset = [col for col in roster_df.columns if ' pt' in col or col == 'Total']
        for col in point_columns_to_reset:
            roster_df[col] = 0


        # 2. Process Each Mock Post Interaction
        for i, post_data in enumerate(MOCK_POST_INTERACTIONS):
            url = post_data["url"]
            print(f"\n--- Processing Mock Post {i+1}: {url} ---")
            
            # The 'post_data' here is the dictionary structure that the scraper used to return.
            
            # 3. Map Scraped Usernames to Official Roster Names
            matched_interactions = fuzzy_match_members(post_data['interaction_lists'], initial_roster_copy)
            
            # 4. Calculate Points and Update Roster
            roster_df = calculate_points(roster_df, matched_interactions)

        # 5. Generate Final Leaderboard
        roster_df = roster_df.sort_values(by='Total', ascending=False).reset_index(drop=True)
        roster_df['Rank'] = roster_df.index + 1 
        roster_df.to_csv(LEADERBOARD_OUTPUT_FILE, index=False)

        print("\n=============================================")
        print(f"✨ SUCCESS! Leaderboard generated: {LEADERBOARD_OUTPUT_FILE}")
        print("=============================================")
        
        # Prepare data for beautiful console table
        display_cols = ['Rank', 'First Name', 'Last Name', 'Total', 'Likes 1 pt', 'Comments 1pt (4 max)', 'Post Tag 5 pt']
        final_display_df = roster_df[[col for col in display_cols if col in roster_df.columns]]
        
        # Print the table using tabulate
        print("\n--- Current Leaderboard (Top 10) ---")
        print(tabulate(final_display_df.head(10), headers='keys', tablefmt='fancy_grid', showindex=False))

    except Exception as e:
        print(f"\nFATAL ERROR during tracker execution: {e}")

if __name__ == "__main__":
    run_tracker()