import requests
import cloudscraper

scraper = cloudscraper.create_scraper()

candidates = [
    ("Spotify", "https://jobs.lever.co/spotify"),
    ("Netflix", "https://jobs.lever.co/netflix"),
    ("Hulu", "https://jobs.lever.co/hulu"),
    ("Riot Games", "https://jobs.lever.co/riotgames"), # Gaming/Entertainment
    ("Figma", "https://jobs.lever.co/figma"), # Tech/Design
    ("Canva", "https://jobs.lever.co/canva"), # Tech/Design
    ("Skillshare", "https://jobs.lever.co/skillshare"),
    ("MasterClass", "https://jobs.lever.co/masterclass"), # Edutainment - Good for PR
    ("Cameo", "https://jobs.lever.co/cameo"),
]

print("Checking potential Lever boards...")
for name, url in candidates:
    try:
        r = scraper.get(url)
        if r.status_code == 200:
            print(f"[VALID] {name}: {url}")
        else:
            print(f"[FAILED {r.status_code}] {name}")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
