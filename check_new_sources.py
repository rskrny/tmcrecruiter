import requests
import cloudscraper

scraper = cloudscraper.create_scraper()

candidates = [
    ("Roku", "https://boards.greenhouse.io/roku"),
    ("BuzzFeed", "https://boards.greenhouse.io/buzzfeed"),
    ("Conde Nast", "https://boards.greenhouse.io/condenast"),
    ("Spotify", "https://boards.greenhouse.io/spotify"),
    ("Vimeo", "https://boards.greenhouse.io/vimeo"),
    ("Discord", "https://boards.greenhouse.io/discord"),
    ("Twitch", "https://boards.greenhouse.io/twitch"),
    ("Fremantle", "https://boards.greenhouse.io/fremantle"),
    ("Wasserman", "https://boards.greenhouse.io/wasserman"),
    ("Substack", "https://boards.greenhouse.io/substack"), # Re-checking
    ("Patreon", "https://boards.greenhouse.io/patreon"),   # Re-checking
    ("Lionsgate", "https://boards.greenhouse.io/lionsgate"),
    ("Sony Music", "https://boards.greenhouse.io/sonymusic"),
    ("Warner Music", "https://boards.greenhouse.io/warnermusic"),
    ("Universal Music", "https://boards.greenhouse.io/universalmusicgroup"),
    ("Live Nation", "https://boards.greenhouse.io/livenation"),
    ("Ticketmaster", "https://boards.greenhouse.io/ticketmaster"),
    ("CAA", "https://boards.greenhouse.io/caa"),
    ("UTA", "https://boards.greenhouse.io/uta"),
    ("WME", "https://boards.greenhouse.io/wme"),
    ("Endeavor", "https://boards.greenhouse.io/endeavor"),
    ("Hello Sunshine", "https://boards.greenhouse.io/hellosunshine"),
    ("SpringHill", "https://boards.greenhouse.io/springhillcompany"),
    ("A24", "https://boards.greenhouse.io/a24"), # Control
]

print("Checking potential Greenhouse boards...")
for name, url in candidates:
    try:
        r = scraper.get(url)
        if r.status_code == 200:
            if "Current Job Openings" in r.text or "jobs" in r.text:
                print(f"[VALID] {name}: {url}")
            else:
                print(f"[200 but WEIRD] {name}: {url}")
        else:
            print(f"[FAILED {r.status_code}] {name}")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
