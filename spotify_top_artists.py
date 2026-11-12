"""Step 1: pull your top Spotify artists and save them to artists.json."""
import json

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

SCOPE = "user-top-read"
TIME_RANGES = ["short_term", "medium_term", "long_term"]  # ~4 weeks, ~6 months, all time


def get_top_artists(sp, limit=50):
    """Return a de-duplicated list of top artists across all time ranges."""
    seen = {}
    for time_range in TIME_RANGES:
        results = sp.current_user_top_artists(limit=limit, time_range=time_range)
        for item in results["items"]:
            entry = seen.setdefault(
                item["id"],
                {"id": item["id"], "name": item["name"], "ranges": []},
            )
            entry["ranges"].append(time_range)
    return list(seen.values())


def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
    artists = get_top_artists(sp)
    with open("artists.json", "w") as f:
        json.dump(artists, f, indent=2)
    print(f"Saved {len(artists)} artists to artists.json")
    for a in artists[:10]:
        print(f"  {a['name']}  ({', '.join(a['ranges'])})")


if __name__ == "__main__":
    main()
