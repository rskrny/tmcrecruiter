import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import config
import re

# Setup
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)
ua = UserAgent()
headers = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def score_job_debug(title):
    """Simplified scoring for debug purposes"""
    score = 0
    text = title.lower()
    
    # Check Negative
    for kw in config.NEGATIVE_KEYWORDS:
        # Use regex for word boundaries to avoid "Intern" matching "International"
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text):
            return -1, f"Negative Keyword: {kw}"

    # Tier 1
    for kw in config.TIER_1_KEYWORDS:
        if kw.lower() in text:
            score += 50
            return score, f"Tier 1 Match: {kw}"

    # Tier 2
    for kw in config.TIER_2_KEYWORDS:
        if kw.lower() in text:
            score += 15
            return score, f"Tier 2 Match: {kw}"
            
    return score, "No Keyword Match"

def verify_site(name, url):
    print(f"\n--- VERIFYING: {name} ({url}) ---")
    try:
        r = scraper.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Failed: {r.status_code}")
            return

        soup = BeautifulSoup(r.content, 'html.parser')
        
        found_any = False
        for link in soup.find_all('a', href=True):
            href = link['href']
            if "/jobs/" in href:
                title = link.get_text(" ").strip()
                if not title: continue
                
                found_any = True
                score, reason = score_job_debug(title)
                
                # Print everything so the user SEES the data
                print(f"Job: {title[:50]}...")
                print(f"  - Score: {score} ({reason})")
                print(f"  - URL: {href}")
                print("-" * 20)
        
        if not found_any:
            print("No links with '/jobs/' found. Dumping all links to debug:")
            for link in soup.find_all('a', href=True):
                print(f"  - {link.get_text().strip()} -> {link['href']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_site("A24", "https://boards.greenhouse.io/a24")
    verify_site("Vox Media", "https://boards.greenhouse.io/voxmedia")
    verify_site("Axios", "https://boards.greenhouse.io/axios")
