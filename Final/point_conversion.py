import pandas as pd
from typing import Dict, List

# Define the point values for each interaction type
POINTS = {
    "likers": 1,
    "commenters": 1, 
    "tagged_users": 5, # Point value for a post tag, story tag, etc.
}
# Define the maximum points a member can earn for repeated actions on a single post
MAX_POINTS_PER_COMMENT = 4

def calculate_points(roster_df: pd.DataFrame, matched_interactions: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Calculates points based on matched interactions and updates the roster DataFrame.

    Args:
        roster_df: The DataFrame containing the current member roster and accumulated scores.
        matched_interactions: A dictionary containing lists of officially matched usernames 
                              for 'likers', 'commenters', and 'tagged_users'.

    Returns:
        The updated roster DataFrame with new points added for this post.
    """
    
    # 1. Process Likers (1 point each)
    print("  -> Calculating points for LIKES (1 pt each)...")
    for username in matched_interactions["likers"]:
        # Find the index of the member in the roster
        member_index = roster_df[roster_df['Username'] == username].index
        if not member_index.empty:
            roster_df.loc[member_index, 'Likes 1 pt'] += POINTS["likers"]

    # 2. Process Commenters (1 point each, max 4 per post)
    print(f"  -> Calculating points for COMMENTS (1 pt each, max {MAX_POINTS_PER_COMMENT} max)...")
    
    # Count unique comments per user for this post
    comment_counts = pd.Series(matched_interactions["commenters"]).value_counts()
    
    for username, count in comment_counts.items():
        # Find the index of the member in the roster
        member_index = roster_df[roster_df['Username'] == username].index
        if not member_index.empty:
            # Apply the cap: points awarded = min(count, MAX_POINTS_PER_COMMENT)
            points_awarded = min(count, MAX_POINTS_PER_COMMENT) * POINTS["commenters"]
            roster_df.loc[member_index, 'Comments 1pt (4 max)'] += points_awarded
            
    # 3. Process Tagged Users (5 points each, one per post tag)
    # Note: We assume only one 'Post Tag' point is awarded per user per post.
    print(f"  -> Calculating points for POST TAGS ({POINTS['tagged_users']} pts each)...")
    # Use set to only count unique users tagged in this post
    unique_tagged_users = set(matched_interactions["tagged_users"])
    
    for username in unique_tagged_users:
        member_index = roster_df[roster_df['Username'] == username].index
        if not member_index.empty:
            roster_df.loc[member_index, 'Post Tag 5 pt'] += POINTS["tagged_users"]


    # 4. Recalculate Total Points
    # Sum up all the interaction columns (excluding metadata) to get the new total
    point_columns = ['Likes 1 pt', 'Comments 1pt (4 max)', 'Story Repost 5 pt', 
                     'Story Tag 5 pt', 'Post Tag 5 pt', 'Linkedin 5 pt']
                     
    # Ensure all columns exist before summing (they should, due to initialize_roster)
    valid_cols = [col for col in point_columns if col in roster_df.columns]
    
    roster_df['Total'] = roster_df[valid_cols].sum(axis=1)

    print("  -> Points for this post successfully calculated and accumulated.")
    return roster_df

# Example of how this function is used (for testing/debugging)
if __name__ == "__main__":
    # Mock Roster Data with initial zeros
    mock_roster_data = {
        'First Name': ['Aiden', 'Jenna', 'Brady', 'NonMember'],
        'Last Name': ['Cheung', 'Weigelt', 'Johnson', 'User'],
        'Username': ['aiidencc', 'jennaamarii', 'bradyj_01', 'non_member_a'],
        'Likes 1 pt': [0, 0, 0, 0], 
        'Comments 1pt (4 max)': [0, 0, 0, 0], 
        'Story Repost 5 pt': [0, 0, 0, 0],
        'Story Tag 5 pt': [0, 0, 0, 0], 
        'Post Tag 5 pt': [0, 0, 0, 0], 
        'Linkedin 5 pt': [0, 0, 0, 0],
        'Total': [0, 0, 0, 0]
    }
    roster_df = pd.DataFrame(mock_roster_data)

    # Mock Matched Interactions (from member_matcher.py output)
    mock_matched_interactions = {
        "likers": ["aiidencc", "jennaamarii", "bradyj_01", "aiidencc", "jennaamarii"],
        "commenters": ["aiidencc", "aiidencc", "aiidencc", "aiidencc", "aiidencc", "jennaamarii"], # 5 comments by Aiden, 1 by Jenna
        "tagged_users": ["aiidencc", "jennaamarii"] 
    }
    
    updated_roster = calculate_points(roster_df, mock_matched_interactions)
    
    # Expected results:
    # Aiden: 2 Likes + 4 Comments (capped) + 5 Tag = 11 Total
    # Jenna: 2 Likes + 1 Comment + 5 Tag = 8 Total
    # Brady: 1 Like + 0 Comment + 0 Tag = 1 Total
    
    print("\n--- Point Calculation Results ---")
    print(updated_roster[['Username', 'Likes 1 pt', 'Comments 1pt (4 max)', 'Post Tag 5 pt', 'Total']])