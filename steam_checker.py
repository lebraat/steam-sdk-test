#!/usr/bin/env python3
"""
Steam Account Qualification Checker

Checks if a Steam account meets the following criteria:
- 100+ hours total playtime
- 10+ achievements earned
- 3+ games with >1 hour each
- No more than 50% playtime in single game
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM_ID = os.getenv('STEAM_ID')

class SteamChecker:
    def __init__(self, api_key: str, steam_id: str):
        self.api_key = api_key
        self.steam_id = steam_id
        self.base_url = "http://api.steampowered.com"

    def get_owned_games(self) -> Optional[Dict]:
        """Fetch all owned games with playtime information."""
        url = f"{self.base_url}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': self.api_key,
            'steamid': self.steam_id,
            'format': 'json',
            'include_appinfo': True,
            'include_played_free_games': True
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching owned games: {e}")
            return None

    def get_user_stats(self, app_id: int, game_name: str = "") -> Optional[Dict]:
        """Fetch user stats for a specific game."""
        url = f"{self.base_url}/ISteamUserStats/GetUserStatsForGame/v0002/"
        params = {
            'appid': app_id,
            'key': self.api_key,
            'steamid': self.steam_id
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data and 'playerstats' in data:
                achievements = data['playerstats'].get('achievements', [])
                unlocked = sum(1 for ach in achievements if ach.get('achieved') == 1)
                if unlocked > 0:
                    print(f"  ✓ {game_name} ({app_id}): {unlocked} achievements")
                return data
        except requests.exceptions.RequestException as e:
            print(f"  ✗ {game_name} ({app_id}): {str(e)}")
            return None

    def check_qualifications(self) -> Dict:
        """Check if the account meets all qualification criteria."""
        print("Fetching Steam account data...")

        games_data = self.get_owned_games()
        if not games_data or 'response' not in games_data:
            return {'error': 'Failed to fetch games data'}

        games = games_data['response'].get('games', [])
        if not games:
            return {'error': 'No games found'}

        # Calculate stats
        total_playtime_minutes = sum(game.get('playtime_forever', 0) for game in games)
        total_playtime_hours = total_playtime_minutes / 60
        games_over_1hr = [game for game in games if game.get('playtime_forever', 0) > 60]
        most_played_game = max(games, key=lambda x: x.get('playtime_forever', 0))
        most_played_percentage = (most_played_game.get('playtime_forever', 0) / total_playtime_minutes * 100) if total_playtime_minutes > 0 else 0

        # Count achievements
        print("\nCounting achievements across all games...")
        print("(This may take a while...)\n")
        total_achievements = 0

        for game in games:
            if game.get('playtime_forever', 0) > 0:
                game_name = game.get('name', 'Unknown')
                stats_data = self.get_user_stats(game['appid'], game_name)
                if stats_data and 'playerstats' in stats_data:
                    achievements = stats_data['playerstats'].get('achievements', [])
                    unlocked = sum(1 for ach in achievements if ach.get('achieved') == 1)
                    total_achievements += unlocked

        # Check criteria
        criteria = {
            'total_playtime_hours': round(total_playtime_hours, 2),
            'playtime_100hrs': total_playtime_hours >= 100,
            'total_achievements': total_achievements,
            'achievements_10plus': total_achievements >= 10,
            'games_over_1hr': len(games_over_1hr),
            'games_3plus_over_1hr': len(games_over_1hr) >= 3,
            'most_played_game': most_played_game.get('name', 'Unknown'),
            'most_played_percentage': round(most_played_percentage, 2),
            'no_more_than_50pct_single_game': most_played_percentage <= 50,
            'qualifies': (
                total_playtime_hours >= 100 and
                total_achievements >= 10 and
                len(games_over_1hr) >= 3 and
                most_played_percentage <= 50
            )
        }

        return criteria


def print_results(results: Dict):
    """Print the qualification check results in a readable format."""
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
        return

    print("\n" + "="*60)
    print("STEAM ACCOUNT QUALIFICATION CHECK")
    print("="*60)

    print(f"\n📊 Total Playtime: {results['total_playtime_hours']} hours")
    print(f"   ✓ Requirement: 100+ hours" if results['playtime_100hrs'] else f"   ✗ Requirement: 100+ hours (Need {100 - results['total_playtime_hours']:.2f} more)")

    print(f"\n🏆 Total Achievements: {results['total_achievements']}")
    print(f"   ✓ Requirement: 10+ achievements" if results['achievements_10plus'] else f"   ✗ Requirement: 10+ achievements (Need {10 - results['total_achievements']} more)")

    print(f"\n🎮 Games with >1 hour: {results['games_over_1hr']}")
    print(f"   ✓ Requirement: 3+ games" if results['games_3plus_over_1hr'] else f"   ✗ Requirement: 3+ games (Need {3 - results['games_over_1hr']} more)")

    print(f"\n⭐ Most Played Game: {results['most_played_game']} ({results['most_played_percentage']}% of total)")
    print(f"   ✓ Requirement: ≤50% in single game" if results['no_more_than_50pct_single_game'] else f"   ✗ Requirement: ≤50% in single game (Over by {results['most_played_percentage'] - 50:.2f}%)")

    print("\n" + "="*60)
    if results['qualifies']:
        print("✅ QUALIFIED: Account meets all criteria!")
    else:
        print("❌ NOT QUALIFIED: Account does not meet all criteria")
    print("="*60 + "\n")


if __name__ == "__main__":
    if not STEAM_API_KEY or STEAM_API_KEY == 'your_api_key_here':
        print("Error: Please set STEAM_API_KEY in the .env file")
        exit(1)

    if not STEAM_ID or STEAM_ID == 'your_steam_id_here':
        print("Error: Please set STEAM_ID in the .env file")
        exit(1)

    checker = SteamChecker(STEAM_API_KEY, STEAM_ID)
    results = checker.check_qualifications()
    print_results(results)
