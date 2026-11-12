"""Step 8: check every artist in artists.json for upcoming shows near home."""
import json
import time
from datetime import datetime, timezone

from ticketmaster_search import is_really_the_artist, search_events


def parse_time(text):
    """Turn '2026-08-19T17:00:00Z' into a real datetime we can compare."""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def upcoming_presales(event):
    now = datetime.now(timezone.utc)
    result = []
    for presale in event.get("sales", {}).get("presales", []):
        start = presale.get("startDateTime")
        if start and parse_time(start) > now:
            result.append(presale)
    return result


def main():
    with open("artists.json") as f:
        artists = json.load(f)

    print(f"Checking {len(artists)} artists...\n")
    total_shows = 0
    total_raw = 0
    filtered_out = []

    for artist in artists:
        name = artist["name"]
        try:
            raw = search_events(name)
        except Exception as error:
            print(f"!! {name}: {error}")
            continue

        events = [e for e in raw if is_really_the_artist(e, name)]
        total_raw += len(raw)
        for e in raw:
            if e not in events:
                filtered_out.append(f"{name} -> {e['name']}")
        for event in events:
            total_shows += 1
            venue = event["_embedded"]["venues"][0]["name"]
            date = event["dates"]["start"].get("localDate", "date TBA")
            print(f"{name}: {date} at {venue}")
            print(f"  {event['url']}")
            for presale in upcoming_presales(event):
                print(f"  UPCOMING PRESALE: {presale.get('name')} at {presale.get('startDateTime')}")

        time.sleep(0.3)  # stay under Ticketmaster's 5 requests per second limit

    print(f"\nDone. Found {total_shows} show(s) near you.")
    print(f"Ticketmaster returned {total_raw} raw result(s) in total.")
    if filtered_out:
        print("\nResults my filter threw out (searched artist -> event):")
        for line in filtered_out[:25]:
            print(f"  {line}")


if __name__ == "__main__":
    main()
