"""Concert Radar: find new shows and presales for your top artists.

Usage:
    python concert_radar.py --baseline   (first run: remember current shows, no show alerts)
    python concert_radar.py              (normal run: alert only on NEW shows and presales)
"""
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone

from find_shows import parse_time, upcoming_presales
from notify import send_alert
from ticketmaster_search import is_really_the_artist, search_events

DB_FILE = "radar.db"


def setup_db():
    db = sqlite3.connect(DB_FILE)
    db.execute("CREATE TABLE IF NOT EXISTS seen (key TEXT PRIMARY KEY, first_seen TEXT)")
    return db


def is_new(db, key):
    return db.execute("SELECT 1 FROM seen WHERE key = ?", (key,)).fetchone() is None


def mark_seen(db, key):
    now = datetime.now(timezone.utc).isoformat()
    db.execute("INSERT OR IGNORE INTO seen (key, first_seen) VALUES (?, ?)", (key, now))
    db.commit()


def main():
    baseline = "--baseline" in sys.argv

    with open("artists.json") as f:
        artists = json.load(f)

    db = setup_db()
    print(f"Checking {len(artists)} artists...\n")

    for artist in artists:
        name = artist["name"]
        try:
            raw = search_events(name)
        except Exception as error:
            print(f"!! {name}: {error}")
            continue

        for event in raw:
            if not is_really_the_artist(event, name):
                continue

            venue = event["_embedded"]["venues"][0]["name"]
            date = event["dates"]["start"].get("localDate", "date TBA")

            # New show?
            event_key = f"event:{event['id']}"
            if is_new(db, event_key):
                mark_seen(db, event_key)
                if not baseline:
                    send_alert(f"New show: {name} on {date} at {venue}. {event['url']}")

            # New upcoming presale? (always alerts, even on the baseline run)
            for presale in upcoming_presales(event):
                presale_key = f"presale:{event['id']}:{presale.get('name')}"
                if is_new(db, presale_key):
                    mark_seen(db, presale_key)
                    start = parse_time(presale["startDateTime"]).astimezone()
                    when = start.strftime("%a %b %d at %I:%M %p")
                    send_alert(
                        f"Presale: {name} at {venue} ({date}). "
                        f"{presale.get('name')} starts {when}. {event['url']}"
                    )

        time.sleep(0.3)

    db.close()
    print("Done.")


if __name__ == "__main__":
    main()
