"""Search Ticketmaster for any artist near home.

Usage:
    python ticketmaster_search.py "Chris Brown"
    python ticketmaster_search.py              (defaults to Chris Brown)
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def search_events(artist):
    params = {
        "apikey": os.getenv("TICKETMASTER_API_KEY"),
        "keyword": artist,
        "latlong": os.getenv("HOME_LATLONG"),
        "radius": os.getenv("SEARCH_RADIUS_MILES", "50"),
        "unit": "miles",
        "classificationName": "music",
        "sort": "date,asc",
        "size": 20,
    }
    response = requests.get(API_URL, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data.get("_embedded", {}).get("events", [])


def is_really_the_artist(event, artist):
    attractions = event.get("_embedded", {}).get("attractions", [])
    return any(a["name"].lower() == artist.lower() for a in attractions)


def main():
    artist = sys.argv[1] if len(sys.argv) > 1 else "Chris Brown"

    raw = search_events(artist)
    events = [e for e in raw if is_really_the_artist(e, artist)]

    print(f"Ticketmaster returned {len(raw)} result(s) near you for '{artist}'.")
    print(f"{len(events)} of them are actually {artist}.\n")

    if not events:
        for e in raw:
            print(f"  (filtered out) {e['name']}")
        return

    for event in events:
        venue = event["_embedded"]["venues"][0]["name"]
        date = event["dates"]["start"].get("localDate", "date TBA")
        print(f"{event['name']}")
        print(f"  {date} at {venue}")
        print(f"  {event['url']}")

        for presale in event.get("sales", {}).get("presales", []):
            print(f"  PRESALE: {presale.get('name')} starts {presale.get('startDateTime')}")
        print()


if __name__ == "__main__":
    main()
