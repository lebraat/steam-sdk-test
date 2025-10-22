#!/usr/bin/env python3
"""
Steam Qualification Checker Web App

A Flask web application that allows users to login with Steam
and verify if they meet gaming qualification criteria.
"""

import os
import re
from flask import Flask, render_template, redirect, url_for, session, request
from dotenv import load_dotenv
from steam_checker import SteamChecker

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

STEAM_API_KEY = os.getenv('STEAM_API_KEY')


def validate_steam_openid(claimed_id):
    """
    Validate and extract Steam ID from OpenID response.

    Args:
        claimed_id: The claimed_id from Steam OpenID response

    Returns:
        Steam ID if valid, None otherwise
    """
    pattern = r'https://steamcommunity.com/openid/id/(\d+)'
    match = re.match(pattern, claimed_id)
    if match:
        return match.group(1)
    return None


@app.route('/')
def index():
    """Home page - shows login or qualification status."""
    return render_template('index.html', user=session.get('user'))


@app.route('/login')
def login():
    """Redirect to Steam OpenID login."""
    return render_template('login.html',
                         return_url=request.url_root + 'authenticate')


@app.route('/authenticate')
def authenticate():
    """
    Handle Steam OpenID authentication response.

    In production, this would validate the OpenID response properly.
    For this demo, we'll use a simpler approach.
    """
    # Get the claimed_id from the OpenID response
    claimed_id = request.args.get('openid.claimed_id')

    if claimed_id:
        steam_id = validate_steam_openid(claimed_id)
        if steam_id:
            session['steam_id'] = steam_id
            return redirect(url_for('check'))

    # If no claimed_id or invalid, show manual input form
    return render_template('manual_auth.html')


@app.route('/manual-auth', methods=['POST'])
def manual_auth():
    """Allow manual Steam ID input for testing."""
    steam_id = request.form.get('steam_id')
    if steam_id and steam_id.isdigit() and len(steam_id) == 17:
        session['steam_id'] = steam_id
        return redirect(url_for('check'))
    return redirect(url_for('index'))


@app.route('/check')
def check():
    """Check qualification status for the logged-in user."""
    steam_id = session.get('steam_id')

    if not steam_id:
        return redirect(url_for('index'))

    if not STEAM_API_KEY:
        return render_template('error.html',
                             error='Steam API key not configured')

    # Run the qualification check
    checker = SteamChecker(STEAM_API_KEY, steam_id)
    results = checker.check_qualifications()

    if 'error' in results:
        return render_template('error.html', error=results['error'])

    return render_template('results.html',
                         steam_id=steam_id,
                         results=results)


@app.route('/logout')
def logout():
    """Clear session and logout."""
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    app.run(debug=True, port=5000)
