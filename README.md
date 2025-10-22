# Steam Account Qualification Checker

Verifies if a Steam account meets specific gaming criteria using the Steam Web API.

## Qualification Criteria

- 100+ hours total playtime
- 10+ achievements earned
- 3+ games with >1 hour each
- No more than 50% playtime in single game

## Prerequisites

Before using this tool, you need:

### 1. Steam Account
- Create a free account at https://store.steampowered.com/
- Play some games to meet the qualification criteria

### 2. Steam Mobile App & Authenticator (Required for API Key)
- Download the **Steam Mobile App** ([iOS](https://apps.apple.com/us/app/steam-mobile/id495369748) | [Android](https://play.google.com/store/apps/details?id=com.valvesoftware.android.steam.community))
- Enable **Steam Guard Mobile Authenticator** in the app
- **Important:** You MUST have the mobile authenticator enabled for at least 7 days to register for a Steam API key

### 3. Steam API Key
- After 7+ days with mobile authenticator enabled, visit: https://steamcommunity.com/dev/apikey
- Enter a domain name (can be `localhost` for testing)
- Copy your API key (a 32-character hex string)

### 4. Steam ID (64-bit)
- Go to https://steamid.io/
- Enter your Steam profile URL or username
- Copy your **steamID64** (17-digit number starting with 7656119...)

### 5. Privacy Settings
- Go to your Steam Profile → Edit Profile → Privacy Settings
- Set **Game details** to **Public**
- This is required for the API to access your gaming data

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
   Replace with your actual Steam API key from step 3 in Prerequisites

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
   Replace with your Steam API key (step 3) and Steam ID (step 4) from Prerequisites

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
