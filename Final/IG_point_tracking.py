# final ig point tracking app
# import necessary libraries
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
from difflib import SequenceMatcher
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import csv
import re

try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None  # will skip date extraction if not installed

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here-change-this-in-production' # for session management lol

# set tesseract path for Mac - update if your path is different
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # for M1/M2 Macs
# if you have an Intel Mac, uncomment this line instead:
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# point calculation stuff - matches the og project plan
FUZZY_MATCH_THRESHOLD = 0.8
MAX_POINTS_PER_COMMENT = 4
POINTS = { "likers": 1, "commenters": 1, "tagged_users": 5 }

# where all my files live :)
CREDENTIALS_FILE = 'credentials.json'
ROSTER_FILE = 'F25IGPointTracking - Sheet1.csv'
INTERACTIONS_FILE = 'interactions.json'
ACTIVITY_FILE = 'last_activity.json'

# stores all the data in memory while app is running
roster = []
interactions = []
credentials = {}
undo_stack = []  # stores recent actions for undo functionality
last_activity = {}  # tracks last upload info

# loads everything from files when app starts up
def load_data():
    global roster, interactions, credentials, last_activity
    
    # load login credentials if they exist
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
    
    # load the member roster from CSV
    if os.path.exists(ROSTER_FILE):
        with open(ROSTER_FILE, 'r') as f:
            csv_reader = csv.DictReader(f)
            roster = []
            for row in csv_reader:
                # handles different column name formats bc consistency is hard lol
                member = {
                    'first_name': row.get('First Name', row.get('first_name', '')),
                    'last_name': row.get('Last Name', row.get('last_name', '')),
                    'username': row.get('Username', row.get('username', '')).lower().strip().replace('@', ''),
                    'likes': int(row.get('likes', 0)),
                    'comments': int(row.get('comments', 0)),
                    'tags': int(row.get('tags', 0)),
                    'total_points': int(row.get('total_points', 0))
                }
                roster.append(member)

    # load all the interaction history
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as f:
            interactions = json.load(f)
    
    # load last activity
    if os.path.exists(ACTIVITY_FILE):
        with open(ACTIVITY_FILE, 'r') as f:
            last_activity.update(json.load(f))

# saves login info
def save_credentials():
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=2)
    
# saves roster back to CSV file
def save_roster():
    if not roster:
        return
    
    with open(ROSTER_FILE, 'w', newline='') as f:
        fieldnames = ['First Name', 'Last Name', 'Username', 'likes', 'comments', 'tags', 'total_points']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for member in roster:
            writer.writerow({
                'First Name': member['first_name'],
                'Last Name': member['last_name'],
                'Username': member['username'],
                'likes': member['likes'],
                'comments': member['comments'],
                'tags': member['tags'],
                'total_points': member['total_points']
            })

# saves all the interactions we've processed
def save_interactions():
    with open(INTERACTIONS_FILE, 'w') as f:
        json.dump(interactions, f, indent=2)

# saves last activity info
def save_activity():
    with open(ACTIVITY_FILE, 'w') as f:
        json.dump(last_activity, f, indent=2)

# actually load everything when app starts
load_data()

# makes sure you're logged in before accessing stuff
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({"error": "Unauthorized access:(, redirecting to '/login'"}), 401
        return f(*args, **kwargs)
    return decorated_function

# fuzzy matching bc instagram usernames are messy
def fuzzy_match(text, roster_usernames):
    text_lower = text.lower().strip().replace('@', '')
    matches = []

    for username in roster_usernames:
        similarity = SequenceMatcher(None, text_lower, username.lower()).ratio()
        if similarity >= FUZZY_MATCH_THRESHOLD:
            matches.append(username)
    return matches

# main page - redirects to login if you're not logged in
@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# login page
@app.route('/login')
def login():
    return render_template('login.html')

# simple test endpoint to verify server is working
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'success': True, 'message': 'Server is working!'})

# handles login attempts
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': "Username and password pretty please."}), 400

    # first time using the app? create an account
    if not credentials:
        credentials['username'] = username
        credentials['password_hash'] = generate_password_hash(password)
        save_credentials()
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': "Account created and logged in!"})
    
    # verify login for existing account
    if credentials['username'] == username and check_password_hash(credentials['password_hash'], password):
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': "Invalid username or password:("}), 401

# log out
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# change password if needed
@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not check_password_hash(credentials['password_hash'], old_password):
        return jsonify({'success': False, 'error': 'Incorrect current password'}), 401

    credentials['password_hash'] = generate_password_hash(new_password)
    save_credentials()
    return jsonify({'success': True, 'message': 'Password updated successfully'})

# get the full roster
@app.route('/api/roster', methods=['GET'])
@login_required
def get_roster():
    return jsonify(roster)

# add a single member manually
@app.route('/api/roster/add', methods=['POST'])
@login_required
def add_member():
    data = request.json
    member = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'username': data['username'].lower().strip().replace('@', ''),
        'likes': 0,
        'comments': 0,
        'tags': 0,
        'total_points': 0
    }
    roster.append(member)
    save_roster()
    return jsonify({'success': True})

# delete a member
@app.route('/api/roster/delete/<int:index>', methods=['DELETE'])
@login_required
def delete_member(index):
    if 0 <= index < len(roster):
        roster.pop(index)
        save_roster()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

# upload entire roster from CSV file - way easier than adding one by one
@app.route('/api/roster/upload', methods=['POST'])
@login_required
def upload_roster():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # read the CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        new_roster = []
        for row in csv_reader:
            # handles both "First Name" and "first_name" style headers
            username = row.get('Username', row.get('username', '')).lower().strip().replace('@', '')
            first_name = row.get('First Name', row.get('first_name', ''))
            last_name = row.get('Last Name', row.get('last_name', ''))
            
            # skip rows with empty username
            if not username:
                continue
                
            member = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'likes': int(row.get('likes', 0)),
                'comments': int(row.get('comments', 0)),
                'tags': int(row.get('tags', 0)),
                'total_points': int(row.get('total_points', 0))
            }
            new_roster.append(member)
        
        # replace old roster with new one
        roster.clear()
        roster.extend(new_roster)
        save_roster()
        
        return jsonify({'success': True, 'count': len(roster)})
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {error_details}")  # Log to console for debugging
        return jsonify({'success': False, 'error': str(e)}), 500

# the main feature!! processes screenshots to extract usernames
@app.route('/api/process-screenshot', methods=['POST'])
@login_required
def process_screenshot():
    try:
        image_file = request.files['image']
        interaction_type = request.form['type']
        post_url = request.form.get('post_url', '')
        manual_username = request.form.get('manual_username', '').lower().strip().replace('@', '')

        # initialize variables at the start
        total_tag_occurrences = 0
        extracted_date = None

        # save current state for undo
        roster_backup = json.loads(json.dumps(roster))  # deep copy

        # run OCR on the screenshot
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        
        print(f"\n\\\ ===== PROCESSING NEW SCREENSHOT =====")
        print(f"Interaction type: {interaction_type}")
        print(f"Full OCR text:\n{text}\n")

        # try to extract date from screenshot text (Instagram format: "Dec 17" or "December 17")
        date_patterns = [
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if date_parser:
                        extracted_date = date_parser.parse(match.group() + f" {datetime.now().year}").date().isoformat()
                except:
                    pass
                break

        # count story mentions and post tags (these are worth 5 points each)
        story_mention_count = len(re.findall(r'mentioned\s+you\s+in\s+(their|a)\s+story', text, re.IGNORECASE))
        post_tag_count = len(re.findall(r'tagged\s+you\s+in\s+(a|their)\s+post', text, re.IGNORECASE))
        
        # define total BEFORE using it
        total_tag_occurrences = story_mention_count + post_tag_count
        
        print(f"Story mentions detected: {story_mention_count}")
        print(f"Post tags detected: {post_tag_count}")
        print(f"Total tag occurrences: {total_tag_occurrences}")
        
        # extract username from the TOP of the DM/notification
        # instagram puts the username in the first few lines, usually alone on a line
        potential_usernames = []
        
        # if manual username provided, use that instead of OCR
        if manual_username and interaction_type == 'tags':
            print(f"Using manual username: {manual_username}")
            potential_usernames = [manual_username]
        elif interaction_type == 'tags' and total_tag_occurrences > 0:
            # for tags, focus on the first 10 lines to find the username at the top
            # Instagram shows: Display Name, then @handle below it
            first_lines = text.split('\n')[:10]
            print(f"First 10 lines of screenshot:")
            for idx, line in enumerate(first_lines):
                print(f"  Line {idx}: '{line}'")

            # look specifically for the @handle (is after @)
            for line in first_lines:
                line = line.strip()
                if not line or len(line) < 2:
                    continue
                
                # skip common UI text
                if any(skip in line.lower() for skip in ['mentioned', 'tagged', 'story', 'post', 'notification', 'at ', 'pm', 'am', 'sep', 'oct', 'nov', 'dec']):
                    continue

                # look for handles that start with _ or contain @
                if line.startswith('_') or '@' in line:
                    clean_word = line.strip('@.,!?(){}[]"\'').strip()
                    if clean_word and 2 <= len(clean_word) <= 30:
                        potential_usernames.append(clean_word)
                        print(f"Found Instagram handle: '{clean_word}'")
                        break
                
                if potential_usernames:
                    break
            
            # if still no username found, try any alphanumeric word that looks like a handle
            if not potential_usernames:
                print("No handle with _ found, trying fallback method...")
                for line in first_lines[:5]:
                    line = line.strip()
                    if not line:
                        continue
                    if any(skip in line.lower() for skip in ['mentioned', 'tagged', 'story', 'post', 'sep', 'oct', 'nov', 'dec', 'at ', 'pm', 'am']):
                        continue
                    
                    words = line.split()
                    for word in words:
                        clean_word = word.strip('@.,!?(){}[]"\'')
                        if clean_word and 2 <= len(clean_word) <= 30:
                            alphanumeric_count = sum(c.isalnum() or c in '._' for c in clean_word)
                            if alphanumeric_count >= len(clean_word) * 0.8:
                                potential_usernames.append(clean_word)
                                print(f"Found potential username: '{clean_word}'")
                                break
                    
                    if potential_usernames:
                        break
        else:
            # for likes/comments, extract usernames normally from the whole text
            print("Non-tag interaction, extracting usernames from full text")
            lines = text.split('\n')
            for line in lines: 
                line = line.strip()
                if '@' in line or any(c.isalnum() for c in line):
                    words = line.split()
                    for word in words:
                        clean_word = word.strip("@.,!?(){}[]")
                        if clean_word and len(clean_word) > 2:
                            potential_usernames.append(clean_word)
        
        print(f"All potential usernames extracted: {potential_usernames}")
        
        # match against our actual roster using fuzzy matching
        roster_usernames = [m['username'] for m in roster]
        matched_usernames = []
        
        for potential in potential_usernames:
            matches = fuzzy_match(potential, roster_usernames)
            matched_usernames.extend(matches)

        # remove duplicates but keep order
        matched_usernames = list(dict.fromkeys(matched_usernames))
        
        print(f"Final matched usernames: {matched_usernames}")
        
        # If this is a tags interaction type, we award based on occurrence count
        if interaction_type == 'tags' and total_tag_occurrences > 0:
            print(f"Tags mode: Found {total_tag_occurrences} tag occurrences")
            if matched_usernames:
                points_per_person = total_tag_occurrences
                print(f"Will award {points_per_person} tag occurrences (×5 pts each) to each matched user")
            else:
                print(f"WARNING: Found {total_tag_occurrences} tags but no matched usernames!")
        
        # use extracted date or current date
        timestamp = extracted_date + 'T12:00:00' if extracted_date else datetime.now().isoformat()

        # log this interaction for records
        interaction = {
            'timestamp': timestamp,
            'postUrl': post_url,
            'type': interaction_type,
            'usernames': matched_usernames
        }
        interactions.append(interaction)
        save_interactions()

        # update everyone's points based on what type of interaction this was
        for username in matched_usernames:
            for member in roster:
                if member['username'] == username:
                    if interaction_type == 'likes':
                        member['likes'] += 1
                        member['total_points'] += POINTS['likers']
                        print(f"Added 1 like to {username}")
                    elif interaction_type == 'comments':
                        # count how many times they commented (max 4 points per post)
                        count = matched_usernames.count(username)
                        points_to_add = min(count, MAX_POINTS_PER_COMMENT) * POINTS['commenters']
                        member['comments'] += count
                        member['total_points'] += points_to_add
                        print(f"Added {count} comments ({points_to_add} pts) to {username}")
                    elif interaction_type == 'tags':
                        # For tags, give 5 points per occurrence detected
                        if total_tag_occurrences > 0:
                            member['tags'] += total_tag_occurrences
                            member['total_points'] += total_tag_occurrences * POINTS['tagged_users']
                            print(f"Added {total_tag_occurrences} tags ({total_tag_occurrences * 5} pts) to {username}")
                        else:
                            # Fallback: if no occurrences detected but it's a tag type, give 1
                            member['tags'] += 1
                            member['total_points'] += POINTS['tagged_users']
                            print(f"Added 1 tag (5 pts) to {username} (fallback)")
                    break

        save_roster()
        
        # update last activity
        last_activity['timestamp'] = datetime.now().isoformat()
        last_activity['post_url'] = post_url or 'No URL provided'
        last_activity['type'] = interaction_type
        last_activity['matched_count'] = len(matched_usernames)
        last_activity['extracted_date'] = extracted_date
        save_activity()
        
        # save undo state
        undo_stack.append({
            'action': 'process_screenshot',
            'roster_before': roster_backup,
            'interaction': interaction
        })
        print(f"[DEBUG] Undo state saved. Total undo stack size: {len(undo_stack)}")
        
        # keep only last 20 actions for better undo history
        if len(undo_stack) > 20:
            undo_stack.pop(0)
            
        return jsonify({
            'success': True,
            'matched_count': len(matched_usernames),
            'matched_usernames': matched_usernames,
            'all_text': potential_usernames,
            'extracted_date': extracted_date,
            'ocr_text_preview': text[:300],  # first 300 chars for debugging
            'tag_occurrences': total_tag_occurrences if interaction_type == 'tags' else 0
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[DEBUG] Screenshot processing error:\n{error_trace}")
        return jsonify({'success': False, 'error': str(e), 'traceback': error_trace}), 500

# generate the leaderboard sorted by points
@app.route('/api/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    # get date filters if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # if dates provided, recalculate points from interactions
    if start_date or end_date:
        # reset points
        for member in roster:
            member['likes'] = 0
            member['comments'] = 0
            member['tags'] = 0
            member['total_points'] = 0
        
        # filter interactions by date
        filtered_interactions = interactions
        if start_date or end_date:
            filtered_interactions = []
            for interaction in interactions:
                interaction_date = interaction['timestamp'][:10]  # YYYY-MM-DD
                
                include = True
                if start_date and interaction_date < start_date:
                    include = False
                if end_date and interaction_date > end_date:
                    include = False
                    
                if include:
                    filtered_interactions.append(interaction)
        
        # recalculate points from filtered interactions
        for interaction in filtered_interactions:
            interaction_type = interaction['type']
            matched_usernames = interaction['usernames']
            
            for username in matched_usernames:
                for member in roster:
                    if member['username'] == username:
                        if interaction_type == 'likes':
                            member['likes'] += 1
                            member['total_points'] += POINTS['likers']
                        elif interaction_type == 'comments':
                            count = matched_usernames.count(username)
                            points_to_add = min(count, MAX_POINTS_PER_COMMENT) * POINTS['commenters']
                            member['comments'] += count
                            member['total_points'] += points_to_add
                        elif interaction_type == 'tags':
                            member['tags'] += 1
                            member['total_points'] += POINTS['tagged_users']
                        break
    
    # use the total_points we've been tracking
    for member in roster:
        member['total'] = member['total_points']
    
    # sort highest to lowest
    sorted_roster = sorted(roster, key=lambda x: x['total'], reverse=True)
    return jsonify(sorted_roster)

@app.route('/api/undo', methods=['POST'])
@login_required
def undo_action():
    """Undo the last screenshot processing action"""
    global roster, interactions
    
    print(f"[DEBUG] Undo requested. Stack size: {len(undo_stack)}")
    
    if not undo_stack:
        print("[DEBUG] Undo stack is empty!")
        return jsonify({'success': False, 'error': 'Nothing to undo - upload history is empty'}), 400
    
    try:
        last_action = undo_stack.pop()
        print(f"[DEBUG] Undoing action: {last_action['action']}")
        
        if last_action['action'] == 'process_screenshot':
            # restore roster state
            print(f"[DEBUG] Restoring roster from backup (size: {len(last_action['roster_before'])})")
            roster.clear()
            roster.extend(last_action['roster_before'])
            
            # remove the interaction from log
            interaction_to_remove = last_action['interaction']
            original_size = len(interactions)
            interactions[:] = [i for i in interactions if i != interaction_to_remove]
            print(f"[DEBUG] Removed interaction. Interactions: {original_size} -> {len(interactions)}")
            
            save_roster()
            save_interactions()
            
            print(f"[DEBUG] Undo successful. Remaining undos: {len(undo_stack)}")
            return jsonify({'success': True, 'message': 'Last action undone', 'remaining_undos': len(undo_stack)})
        
        return jsonify({'success': False, 'error': 'Unknown action type'}), 400
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[DEBUG] Undo error: {error_trace}")
        return jsonify({'success': False, 'error': f'Undo failed: {str(e)}'}), 500

@app.route('/api/export', methods=['GET'])
@login_required
def export_leaderboard():
    """Export leaderboard as CSV"""
    # get current leaderboard
    for member in roster:
        member['total'] = member['total_points']
    sorted_roster = sorted(roster, key=lambda x: x['total'], reverse=True)
    
    # create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # headers
    writer.writerow(['Rank', 'First Name', 'Last Name', 'Username', 'Likes', 'Comments', 'Tags', 'Total Points'])
    
    # data
    for idx, member in enumerate(sorted_roster, 1):
        writer.writerow([
            idx,
            member['first_name'],
            member['last_name'],
            member['username'],
            member['likes'],
            member['comments'],
            member['tags'],
            member['total']
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=leaderboard_export.csv'}
    )

@app.route('/api/last-activity', methods=['GET'])
@login_required
def get_last_activity():
    """Get info about last upload"""
    return jsonify(last_activity if last_activity else {'timestamp': None})

@app.route('/api/interactions', methods=['GET'])
@login_required
def get_interactions():
    """Get all interactions for analytics"""
    return jsonify(interactions)

@app.route('/api/undo-status', methods=['GET'])
@login_required
def get_undo_status():
    """Check how many undo actions are available"""
    return jsonify({
        'available_undos': len(undo_stack),
        'last_action': undo_stack[-1]['action'] if undo_stack else None
    })

# reset everything for next semester
@app.route('/api/reset', methods=['POST'])
@login_required
def reset_points():
    for member in roster:
        member['likes'] = 0
        member['comments'] = 0
        member['tags'] = 0
        member['total_points'] = 0
    interactions.clear()
    save_roster()
    save_interactions()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed to port 5001 to avoid macOS AirPlay conflict
