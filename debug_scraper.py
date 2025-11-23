import config
from aggregator import JobAggregator

def debug_source(source_name, fetch_method):
    print(f"\n--- DEBUGGING: {source_name} ---")
    agg = JobAggregator()
    
    # Monkey patch the score_job method to print details
    original_score_job = agg.score_job
    
    def debug_score_job(title, description):
        score, loc = original_score_job(title, description)
        print(f"  [ANALYSIS] Title: '{title}' | Score: {score} | Loc: {loc}")
        return score, loc
    
    agg.score_job = debug_score_job
    
    # Run the fetch
    try:
        # We need to hook into the internal scraper/requests to see the raw body
        # But since we can't easily do that without modifying aggregator, 
        # let's just run the method.
        # Wait, I can verify the URLs in config first.
        pass
        
    except Exception as e:
        print(f"  [ERROR] {e}")

    # Manually fetch to see raw response
    if source_name == "The Muse":
        try:
            r = agg.scraper.get(config.URLS["TheMuse"], headers=agg.get_headers())
            print(f"  [RAW RESPONSE STATUS] {r.status_code}")
            print(f"  [RAW RESPONSE START] {r.text[:500]}...")
        except Exception as e:
            print(f"  [RAW ERROR] {e}")

    if source_name == "EntertainmentCareers":
        try:
            r = agg.scraper.get(config.URLS["EntertainmentCareers"], headers=agg.get_headers())
            print(f"  [RAW RESPONSE STATUS] {r.status_code}")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.content, 'html.parser')
            print("  [LINK ANALYSIS - EntertainmentCareers]")
            # Print ALL links that look like job postings to find the pattern
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()
                # Filter out obvious nav links to reduce noise
                if len(text) > 5 and "Login" not in text and "Sign" not in text:
                    print(f"    Href: {href} | Text: {text[:40]}")
        except Exception as e:
            print(f"  [RAW ERROR] {e}")

    if source_name == "PRSA":
        try:
            r = agg.scraper.get(config.URLS["PRSA_Search"], headers=agg.get_headers())
            print(f"  [RAW RESPONSE STATUS] {r.status_code}")
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.content, 'html.parser')
            print("  [LINK ANALYSIS - PRSA]")
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()
                if len(text) > 5:
                    print(f"    Href: {href} | Text: {text[:40]}")
        except Exception as e:
            print(f"  [RAW ERROR] {e}")

    fetch_method()
        
    print(f"  [RESULT] Found {len(agg.jobs)} passing jobs.")

if __name__ == "__main__":
    agg = JobAggregator()
    
    # Test specific sources
    debug_source("The Muse", agg.fetch_themuse)
    debug_source("EntertainmentCareers", agg.fetch_entertainment_careers)
    debug_source("PRSA", agg.fetch_prsa)
