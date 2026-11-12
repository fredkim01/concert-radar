"""Step 2: search Ticketmaster for one artist near home and print what we find."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

ARTIST = "SZA"  # change this to any artist from your list

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
    response.raise_for_status()  # stops with a clear error if the key is wrong
    data = response.json()
    # If there are no events, Ticketmaster leaves out "_embedded" entirely
    return data.get("_embedded", {}).get("events", [])


def is_really_the_artist(event, artist):
    """Keyword search is loose (tribute acts, similar names), so double-check."""
    attractions = event.get("_embedded", {}).get("attractions", [])
    return any(a["name"].lower() == artist.lower() for a in attractions)


def main():
    events = search_events(ARTIST)
    events = [e for e in events if is_really_the_artist(e, ARTIST)]

    if not events:
        print(f"No upcoming shows found for {ARTIST} near you.")
        return

    print(f"Found {len(events)} show(s) for {ARTIST}:\n")
    for event in events:
        venue = event["_embedded"]["venues"][0]["name"]
        date = event["dates"]["start"].get("localDate", "date TBA")
        print(f"{event['name']}")
        print(f"  {date} at {venue}")
        print(f"  {event['url']}")

        presales = event.get("sales", {}).get("presales", [])
        for presale in presales:
            print(f"  PRESALE: {presale.get('name')} starts {presale.get('startDateTime')}")
        print()


if __name__ == "__main__":
    main()
