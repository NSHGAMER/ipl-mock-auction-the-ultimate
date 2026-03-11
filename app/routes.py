from flask import Blueprint, current_app, render_template, redirect, url_for, request, session, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Show landing page with college info and auction player list
    try:
        sheet = get_sheet().worksheet('auction_players')
        players = sheet.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        players = []
    
    # Get college info from a settings sheet if available
    college_info = {
        'name': 'Your College Name',
        'description': 'Welcome to the IPL Mock Auction - Build your dream team!',
        'tagline': 'Experience the thrill of IPL player auction'
    }
    
    return render_template('landing.html', players=players, college=college_info)


def init_app(app_instance):
    app_instance.register_blueprint(bp)


# Utility functions

import os
from flask import abort

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Try to load credentials from environment variable first (for production/Render)
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except (json.JSONDecodeError, ValueError) as e:
            abort(500, description=f"Invalid GOOGLE_CREDENTIALS_JSON environment variable: {str(e)}")
    else:
        # Fallback to file-based credentials for local development
        cfg = current_app.config
        creds_path = cfg.get("GSHEET_CREDENTIALS")
        
        # if the path is relative, treat it as relative to the app package
        if creds_path and not os.path.isabs(creds_path):
            creds_path = os.path.join(current_app.root_path, creds_path)
            
        if not creds_path or not os.path.isfile(creds_path):
            abort(500, description=f"Google Sheets credentials file not found: {creds_path}.\n" \
                                      "Set GOOGLE_CREDENTIALS_JSON env var or place credentials.json in the app folder.")
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    
    client = gspread.authorize(creds)
    spreadsheet = client.open("ipl-mock-auction-the-ultimate")
    return spreadsheet

def get_or_create_team_sheet(team_name):
    """Get or create a worksheet for the team"""
    spreadsheet = get_sheet()
    try:
        worksheet = spreadsheet.worksheet(team_name)
    except gspread.exceptions.WorksheetNotFound:
        # Create new worksheet for the team
        worksheet = spreadsheet.add_worksheet(title=team_name, rows=100, cols=10)
        # Add headers
        worksheet.update('A1:C1', [['Player Name', 'Price', 'Wallet Balance']])
    return worksheet

def update_team_wallet(team_name, wallet_balance):
    """Update the wallet balance in the team's sheet"""
    worksheet = get_or_create_team_sheet(team_name)
    # Find the wallet row (assume it's in A2:C2 or something, but for simplicity, update a specific cell)
    # For now, let's put wallet in cell B2 (below headers)
    worksheet.update('B2', [[f'Wallet: {format_currency(wallet_balance)}']])
    # Actually, better to have a dedicated wallet row
    # Let's assume row 2 is for wallet info
    worksheet.update('A2:C2', [['', '', f'Current Wallet: {format_currency(wallet_balance)}']])

def add_player_to_team_sheet(team_name, player_name, price, wallet_balance):
    """Add player to team's sheet and update wallet"""
    worksheet = get_or_create_team_sheet(team_name)
    # Find next empty row
    records = worksheet.get_all_records()
    next_row = len(records) + 2  # +2 because header is row 1, wallet is row 2
    worksheet.update(f'A{next_row}:C{next_row}', [[player_name, format_currency(price), '']])
    # Update wallet
    update_team_wallet(team_name, wallet_balance)

def remove_player_from_team_sheet(team_name, player_name, wallet_balance):
    """Remove player from team's sheet and update wallet"""
    worksheet = get_or_create_team_sheet(team_name)
    records = worksheet.get_all_records()
    for idx, record in enumerate(records, start=3):  # start from row 3 (after header and wallet)
        if record.get('Player Name') == player_name:
            worksheet.delete_rows(idx)
            break
    # Update wallet
    update_team_wallet(team_name, wallet_balance)

# price parser is moved to utils
from .utils import parse_price, format_currency

# Admin login
@bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin_direct@69':
            session['role'] = 'admin'
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    # load team/player data
    sheet = get_sheet().worksheet('players')
    players = sheet.get_all_records()
    return render_template('admin_dashboard.html', players=players)

# Participant registration & login
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        college = request.form['college']
        team = request.form['team']
        password = request.form['password']
        # check uniqueness team+name?
        sheet = get_sheet().worksheet('participants')
        records = sheet.get_all_records()
        for r in records:
            if r['team'].lower() == team.lower() and r['name'].lower() == name.lower():
                flash('You are already registered for this team', 'error')
                return redirect(url_for('main.register'))
        # add to sheet
        sheet.append_row([name, college, team, password, 10000000000])
        flash('Registration successful. Please login.', 'success')
        # Initialize team sheet with wallet
        update_team_wallet(team, 10000000000)
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team = request.form['team']
        password = request.form['password']
        sheet = get_sheet().worksheet('participants')
        records = sheet.get_all_records()
        for r in records:
            if r['team'].lower() == team.lower() and r['password'] == password:
                session['role'] = 'participant'
                session['team'] = team
                return redirect(url_for('main.participant_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@bp.route('/dashboard')
def participant_dashboard():
    if session.get('role') != 'participant':
        return redirect(url_for('main.login'))
    team = session.get('team')
    # fetch participant details
    sheet = get_sheet().worksheet('participants')
    records = sheet.get_all_records()
    user = None
    for r in records:
        if r['team'].lower() == team.lower():
            user = r
            break
    # fetch players bought by team
    sheetp = get_sheet().worksheet('players')
    players = [p for p in sheetp.get_all_records() if p['team'].lower() == team.lower()]
    bought_count = len(players)
    wallet = user['wallet'] if user else 0
    return render_template('dashboard.html', team=team, bought_count=bought_count, wallet=wallet, players=players)

# endpoints for admin actions to add/edit/delete players
@bp.route('/admin/player/add', methods=['POST'])
def admin_add_player():
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    name = request.form['name']
    team = request.form['team']
    price_str = request.form['price']
    # parse price allowing "100cr" etc
    price = parse_price(price_str)
    sheet = get_sheet().worksheet('players')
    sheet.append_row([name, team, price])
    # adjust participant wallet
    part_sheet = get_sheet().worksheet('participants')
    records = part_sheet.get_all_records()
    for idx, r in enumerate(records, start=2):
        if r['team'].lower() == team.lower():
            new_wallet = int(r.get('wallet', 0)) - price
            part_sheet.update_cell(idx, 5, new_wallet)  # wallet is 5th column
            # Also update team sheet
            add_player_to_team_sheet(team, name, price, new_wallet)
            break
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/player/delete/<int:row>')
def admin_delete_player(row):
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    sheet = get_sheet().worksheet('players')
    # fetch price and team before deletion
    record = sheet.row_values(row)
    if len(record) >= 3:
        team = record[1]
        try:
            price = int(record[2])
        except ValueError:
            price = 0
        # refund wallet
        part_sheet = get_sheet().worksheet('participants')
        records = part_sheet.get_all_records()
        for idx, r in enumerate(records, start=2):
            if r['team'].lower() == team.lower():
                new_wallet = int(r.get('wallet', 0)) + price
                part_sheet.update_cell(idx, 5, new_wallet)
                # Also update team sheet
                player_name = record[0]
                remove_player_from_team_sheet(team, player_name, new_wallet)
                break
    sheet.delete_rows(row)
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/player/edit/<int:row>', methods=['GET', 'POST'])
def admin_edit_player(row):
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    sheet = get_sheet().worksheet('players')
    
    if request.method == 'GET':
        # Get current player data
        record = sheet.row_values(row)
        if len(record) < 3:
            flash('Player not found', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        player_data = {
            'row': row,
            'name': record[0],
            'team': record[1],
            'price': record[2]
        }
        return render_template('edit_player.html', player=player_data)
    
    elif request.method == 'POST':
        # Update player data
        new_name = request.form['name']
        new_team = request.form['team']
        new_price_str = request.form['price']
        new_price = parse_price(new_price_str)
        
        # Get old data
        record = sheet.row_values(row)
        old_team = record[1]
        old_price = int(record[2]) if record[2].isdigit() or (isinstance(record[2], int)) else parse_price(str(record[2]))
        
        # Update player in sheet
        sheet.update_cell(row, 1, new_name)
        sheet.update_cell(row, 2, new_team)
        sheet.update_cell(row, 3, new_price)
        
        # Adjust wallet if team or price changed
        if old_team != new_team or old_price != new_price:
            part_sheet = get_sheet().worksheet('participants')
            records = part_sheet.get_all_records()
            
            # Refund old team if team changed
            if old_team != new_team:
                for idx, r in enumerate(records, start=2):
                    if r['team'].lower() == old_team.lower():
                        refund_wallet = int(r.get('wallet', 0)) + old_price
                        part_sheet.update_cell(idx, 5, refund_wallet)
                        remove_player_from_team_sheet(old_team, record[0], refund_wallet)
                        break
                
                # Deduct from new team
                for idx, r in enumerate(records, start=2):
                    if r['team'].lower() == new_team.lower():
                        new_wallet = int(r.get('wallet', 0)) - new_price
                        part_sheet.update_cell(idx, 5, new_wallet)
                        add_player_to_team_sheet(new_team, new_name, new_price, new_wallet)
                        break
            else:
                # Same team, adjust wallet by price difference
                price_diff = new_price - old_price
                for idx, r in enumerate(records, start=2):
                    if r['team'].lower() == old_team.lower():
                        current_wallet = int(r.get('wallet', 0))
                        new_wallet = current_wallet - price_diff
                        part_sheet.update_cell(idx, 5, new_wallet)
                        remove_player_from_team_sheet(old_team, record[0], new_wallet)
                        add_player_to_team_sheet(new_team, new_name, new_price, new_wallet)
                        break
        
        flash(f'Player "{new_name}" updated successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))

# helper to parse price strings
def parse_price(txt):
    txt = txt.strip().lower()
    if txt.endswith('cr'):
        num = float(txt[:-2])
        return int(num * 1e7)
    else:
        # assume rupees
        return int(float(txt))

# PDF handling and auction player management
import io
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return None

def clean_text(text):
    """
    Clean extracted text by removing excess whitespace
    but preserving structure
    """
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:  # Keep non-empty lines
            cleaned.append(line)
    return cleaned

def parse_players_from_text(text):
    """
    Parse player information from extracted PDF text.
    Handles multiple formats:
    1. "Player Name | Role" (structured format)
    2. "Player Name  Role" (space-separated)
    3. "Player Name" (just name, defaults to Batsman)
    4. Table-like data (multi-column CSV)
    """
    players = []
    lines = clean_text(text)
    
    # Common role keywords to identify
    role_keywords = {
        'batsman': 'Batsman',
        'batter': 'Batsman',
        'bowler': 'Bowler',
        'all-rounder': 'All-rounder',
        'allrounder': 'All-rounder',
        'pacer': 'Bowler',
        'spinner': 'Bowler',
        'keeper': 'Batsman',
        'wk': 'Batsman',
    }
    
    seen = set()  # To avoid duplicates
    
    for line in lines:
        if not line or len(line) < 2:
            continue
        
        # Skip header lines and common noise
        if any(header in line.lower() for header in 
               ['name', 'player', 'role', 'list sr.', 'set no.', 'firstname', 'surname', 
                'country', 'dob', 'age', 'caps', 'reserve', 'price', 'team', 'specialismtest']):
            continue
        
        name = None
        role = 'Batsman'
        
        # Try pipe delimiter first (structured format)
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            name = parts[0]
            if len(parts) > 1:
                # Try to match role keyword
                role_str = parts[1].lower()
                for keyword, role_val in role_keywords.items():
                    if keyword in role_str:
                        role = role_val
                        break
        else:
            # Try to extract player name and role from mixed text
            # Split by common separators or multiple spaces
            words = line.split()
            
            if len(words) >= 1:
                # Look for role keywords in the line
                line_lower = line.lower()
                detected_role = 'Batsman'
                
                for keyword, role_val in role_keywords.items():
                    if keyword in line_lower:
                        detected_role = role_val
                        # Remove the role word from line to get just the name
                        name = line_lower.replace(keyword, '').strip()
                        break
                
                # If no role found, take the whole line as name
                if detected_role == 'Batsman' and name is None:
                    name = line
                    role = detected_role
                else:
                    role = detected_role
        
        # Clean up name
        if name:
            name = name.strip()
            # Remove extra numbers and special chars at end (like row numbers)
            name = ' '.join(word for word in name.split() if not word.isdigit())
            name = name.strip()
            
            # Filter out noise - too short or all numbers or common headers
            if name and len(name) > 1 and not name.replace(' ', '').isdigit():
                # Avoid duplicates
                if name.lower() not in seen:
                    seen.add(name.lower())
                    players.append({
                        'name': name,
                        'role': role
                    })
    
    return players

def get_or_create_auction_sheet():
    """Get or create the auction_players worksheet"""
    spreadsheet = get_sheet()
    try:
        worksheet = spreadsheet.worksheet('auction_players')
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title='auction_players', rows=1000, cols=10)
        worksheet.update('A1:B1', [['Player Name', 'Role']])
    return worksheet

@bp.route('/admin/players/upload', methods=['POST'])
def admin_upload_player_list():
    """Upload and parse player list PDF with preview"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    if 'pdf_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    file = request.files['pdf_file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    if not (file and allowed_file(file.filename)):
        flash('Only PDF files are allowed', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file)
        if not text:
            flash('Could not extract text from PDF. It may be a scanned image. Try converting to searchable PDF.', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Parse players from text
        players = parse_players_from_text(text)
        if not players:
            flash('No players found in PDF. Try a different format or use Manual Entry.', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        # Store in session for preview
        session['pending_players'] = players
        session['pending_players_count'] = len(players)
        
        # Show preview
        return render_template('player_preview.html', players=players, file_name=file.filename)
    
    except Exception as e:
        flash(f'Error processing PDF: {str(e)}', 'error')
        return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/players/confirm', methods=['POST'])
def confirm_player_upload():
    """Confirm and save the previewed players to Google Sheets"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    if 'pending_players' not in session:
        flash('No pending players to upload', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    players = session['pending_players']
    
    try:
        # Clear existing auction players
        worksheet = get_or_create_auction_sheet()
        # Delete all rows except header
        if worksheet.row_count > 1:
            worksheet.delete_rows(2, worksheet.row_count)
        
        # Add new players
        for player in players:
            worksheet.append_row([player['name'], player['role']])
        
        # Clear session
        session.pop('pending_players', None)
        session.pop('pending_players_count', None)
        
        flash(f'Successfully uploaded {len(players)} players!', 'success')
    except Exception as e:
        flash(f'Error saving players: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/players/cancel', methods=['POST'])
def cancel_player_upload():
    """Cancel the player upload preview"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    session.pop('pending_players', None)
    session.pop('pending_players_count', None)
    
    flash('Upload cancelled', 'info')
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/players/manual-form', methods=['GET'])
def manual_players_form():
    """Show manual player entry form"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    return render_template('manual_players.html')

@bp.route('/admin/players/manual-upload', methods=['POST'])
def manual_upload_players():
    """Handle manual bulk player entry"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    players_text = request.form.get('players_text', '').strip()
    
    if not players_text:
        flash('Please enter player data', 'error')
        return redirect(url_for('manual_players_form'))
    
    try:
        # Parse manually entered players
        players = parse_players_from_text(players_text)
        
        if not players:
            flash('No players found. Use format: Player Name | Role (or just names)', 'error')
            return redirect(url_for('manual_players_form'))
        
        # Store in session for preview
        session['pending_players'] = players
        session['pending_players_count'] = len(players)
        
        # Show preview
        return render_template('player_preview.html', players=players, file_name='Manual Entry')
    
    except Exception as e:
        flash(f'Error processing data: {str(e)}', 'error')
        return redirect(url_for('manual_players_form'))

@bp.route('/admin/players/clear', methods=['POST'])
def admin_clear_player_list():
    """Clear auction player list"""
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_login'))
    
    try:
        worksheet = get_or_create_auction_sheet()
        if worksheet.row_count > 1:
            worksheet.delete_rows(2, worksheet.row_count)
        flash('Auction player list cleared', 'success')
    except Exception as e:
        flash(f'Error clearing list: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_dashboard'))
