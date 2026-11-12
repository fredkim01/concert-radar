# Concert Radar

Pulls your top artists from Spotify, cross-references live Ticketmaster listings near you, and sends a phone notification when someone you actually listen to announces a show or has an upcoming presale. Built so I stop missing Ticketmaster presales.

**Stack:** Python, Spotify Web API (OAuth), Ticketmaster Discovery API, SQLite, ntfy push notifications, Windows Task Scheduler (cron on Mac/Linux)

## How it works

1. `spotify_top_artists.py` authenticates with Spotify and saves my top artists across short, medium and long term to `artists.json`.
2. `concert_radar.py` searches Ticketmaster for each artist within a set radius of home, and filters out tribute acts and name look-alikes by checking the event's listed performers.
3. A SQLite database (`radar.db`) remembers every show and presale already seen, so only new shows and upcoming presales trigger an alert.
4. `notify.py` sends the alert to my phone through ntfy.sh, with a tappable ticket link and the presale time converted to local time.
5. Task Scheduler runs `run_radar.bat` every 4 hours and logs to `radar.log`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your keys
python spotify_top_artists.py   # one-time Spotify login, creates artists.json
python concert_radar.py --baseline   # record current shows without alerting
python concert_radar.py              # normal run
```

Keys needed in `.env`: Spotify client ID/secret, a Ticketmaster Discovery API key, an ntfy topic name, and your home lat/long and search radius.

## Scheduling

Windows:
```
schtasks /create /tn "Concert Radar" /tr "C:\path\to\run_radar.bat" /sc hourly /mo 4 /f
```
Mac/Linux cron: `0 */4 * * * cd /path/to/concert-radar && .venv/bin/python concert_radar.py >> radar.log 2>&1`

## Notes

- `send_text.py` contains a working Twilio SMS sender. Twilio trial accounts only allow predefined templates, so alerts use ntfy until the account is upgraded. Switching back is a one-line change to `notify.py`.
- Ticketmaster's free API tier allows about 5 requests per second, so the script pauses briefly between artists.

## Ideas for later

- Reminder notification an hour before a presale starts
- Weight alerts toward artists I've played most recently
- Filters by venue or weekday
