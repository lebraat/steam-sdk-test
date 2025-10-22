# Steam Account Qualification Checker

Verifies if a Steam account meets specific gaming criteria using the Steam Web API.

## Qualification Criteria

- 100+ hours total playtime
- 10+ achievements earned
- 3+ games with >1 hour each
- No more than 50% playtime in single game

## Two Usage Options

### Option 1: Web App (Recommended)

A user-friendly web interface with Steam login.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`:**
   ```
   STEAM_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your_random_secret_key
   ```
   Get your Steam API Key at https://steamcommunity.com/dev/apikey

3. **Run the web app:**
   ```bash
   python3 app.py
   ```

4. **Open your browser:**
   Navigate to http://localhost:5000

5. **Login with Steam:**
   - Click "Sign in through Steam" for OpenID authentication
   - Or manually enter your Steam ID for testing

### Option 2: Command Line

Direct Python script for quick checks.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`:**
   ```
   STEAM_API_KEY=your_api_key_here
   STEAM_ID=your_steam_id_here
   ```
   - Get Steam API Key: https://steamcommunity.com/dev/apikey
   - Find Steam ID: https://steamid.io/

3. **Run the checker:**
   ```bash
   python3 steam_checker.py
   ```

## Example Output (CLI)

```
============================================================
STEAM ACCOUNT QUALIFICATION CHECK
============================================================

📊 Total Playtime: 2078.53 hours
   ✓ Requirement: 100+ hours

🏆 Total Achievements: 90
   ✓ Requirement: 10+ achievements

🎮 Games with >1 hour: 5
   ✓ Requirement: 3+ games

⭐ Most Played Game: Stellaris (49.32% of total)
   ✓ Requirement: ≤50% in single game

============================================================
✅ QUALIFIED: Account meets all criteria!
============================================================
```

## Project Structure

```
steam-sdk-test/
├── app.py                 # Flask web application
├── steam_checker.py       # Core verification logic
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── results.html
│   └── error.html
├── static/
│   └── style.css          # Styling
├── .env                   # Configuration (gitignored)
├── requirements.txt       # Python dependencies
└── README.md
```
