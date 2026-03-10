# IPL Mock Auction

Flask-based mock auction application using Google Sheets as backend with beautiful UI and PDF player list import.

## Deployment to Render

1. **Prepare your code**
   - Ensure all files are committed to your Git repository
   - Make sure `credentials.json` is NOT committed (add to `.gitignore`)

2. **Create Render account and service**
   - Go to [render.com](https://render.com) and create an account
   - Click "New +" and select "Web Service"
   - Connect your Git repository

3. **Configure the service**
   - **Name**: Choose a name for your app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py` or `./start.sh`

4. **Set Environment Variables**
   In Render dashboard, go to your service settings and add these environment variables:
   ```
   GSHEET_CREDENTIALS=app/credentials.json
   GSHEET_SPREADSHEET_NAME=ipl-mock-auction-the-ultimate
   FLASK_ENV=production
   SECRET_KEY=your-very-secure-random-secret-key-here
   ```

5. **Upload Google Credentials**
   - Since `credentials.json` shouldn't be in your repo, you'll need to upload it to Render
   - In your service settings, go to "Secret Files" and upload your `credentials.json` to `app/credentials.json`
   - Or you can paste the JSON content directly as an environment variable named `GOOGLE_CREDENTIALS_JSON`

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Once deployed, you'll get a URL like `https://your-app-name.onrender.com`

7. **Post-deployment setup**
   - Access your admin panel at `https://your-app-name.onrender.com/admin`
   - Upload your player list PDF or use manual entry
   - Share the landing page URL with participants

## Local Development

1. **Python environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows
   pip install -r requirements.txt
   ```

2. **Google Sheets API**
   - Create a project in Google Cloud and enable the Sheets API.
   - Create a service account, download JSON credentials file, and place it inside the `app` folder (default) or anywhere you like.
     If you put it elsewhere, either move it to `app/credentials.json` or set the `GSHEET_CREDENTIALS`
     environment variable to the full path.
   - Share your spreadsheet with the service account email (e.g. `...@model-union-473204-r6.iam.gserviceaccount.com`).
   - Ensure `GSHEET_SPREADSHEET_ID` is correct in `app/__init__.py` or override via `GSHEET_SPREADSHEET_ID` env var.
   
> ⚠️ The application will refuse to start if it cannot locate the credentials file.

3. **Spreadsheet structure**
   - Create worksheets named `participants` and `players`.
   - Column headers: for `participants` -> `name`, `college`, `team`, `password`, `wallet`
   - For `players` -> `name`, `team`, `price`
   - `auction_players` worksheet will be created automatically when first PDF is uploaded
   - Team-specific worksheets will be created automatically when players are added to teams.
   - Each team worksheet contains: `Player Name`, `Price`, and current `Wallet Balance`.

4. **Run**
   ```bash
   python main.py
   ```

5. **Access**
   - Landing Page: `http://localhost:5000/` - Browse available players organized by role
   - Admin login at `/admin`: username `admin`, password `admin_direct@69`
   - Participant registration at `/register` and login at `/login`

## Features

### 🏏 Landing Page
- **College Information Display**: Shows college name, tagline, and description
- **Player List by Role**: Automatically organized into Batsmen, Bowlers, and All-Rounders sections
- **Beautiful Cards**: Role-specific color schemes with smooth animations
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop

### 📋 PDF Player Upload (Admin)
- Upload player list from PDF with smart parsing
- Supports multiple formats:
  - `Player Name | Role` (pipe-delimited)
  - Space-separated or comma-separated
  - Table data extracted from Excel/CSV converted to PDF
- **Preview Page**: Review all parsed players before confirming upload
- **Smart Filtering**: Automatically removes headers, noise, and duplicates
- **Role Detection**: Intelligently identifies Batsman, Bowler, All-rounder roles

### 👥 Player Management
- Admin can add/edit/delete players
- Participants register per team, track wallet balance
- Each team has dedicated Google Sheet for admin monitoring
- Wallet currency formatting uses crore notation (₹ Cr)

### 🎨 Modern UI
- Smooth animations with anime.js
- Gradient backgrounds and modern design
- Dark mode support
- Role-based color coding for players

### 💰 Wallet System
- Automatic wallet tracking per team
- Player cost deduction on purchase
- Refund on player removal
- Real-time balance updates

## File Guide

- `main.py` - Application entry point
- `app/__init__.py` - Flask app factory and configuration
- `app/routes.py` - All route handlers and business logic
- `app/utils.py` - Utility functions (currency formatting, etc.)
- `app/templates/landing.html` - Home page with player list
- `app/templates/admin_dashboard.html` - Admin panel with PDF upload
- `app/templates/player_preview.html` - PDF upload preview page
- `requirements.txt` - Python dependencies
- `PDF_UPLOAD_GUIDE.md` - Detailed PDF upload documentation

## Dependencies

- **Flask** - Web framework
- **gspread** - Google Sheets API client
- **oauth2client** - Authentication for Google Sheets
- **PyPDF2** - PDF text extraction and parsing
- **anime.js** - Front-end animations (CDN)

## Notes

- Front-end animations use anime.js via CDN.
- All data persists in Google Sheets (no local database).
- Each team gets its own worksheet for admin monitoring.
- PDF parsing is intelligent and handles various formats automatically.
- This is intended as a proof-of-concept; proper security and validation would be needed for production.

## Quick Start for PDF Upload

1. Prepare a PDF with player names and roles
2. Go to Admin Panel
3. Click "Upload & Parse Players" button
4. Review players in preview table
5. Click "Confirm Upload" to save to Google Sheets
6. Players automatically appear on home page!

For more details, see `PDF_UPLOAD_GUIDE.md`.

