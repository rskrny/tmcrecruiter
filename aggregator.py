import requests
import feedparser
from bs4 import BeautifulSoup
import time
import config

import re

class JobAggregator:
    def __init__(self):
        self.jobs = []

    def extract_salary(self, text):
        """Attempts to extract salary information from text."""
        # Look for patterns like $50k, $100,000, 80-120k, etc.
        # This is a basic regex, can be improved.
        salary_pattern = r'(\$\d+(?:,\d+)?(?:k|K)?(?:\s*-\s*\$\d+(?:,\d+)?(?:k|K)?)?)'
        match = re.search(salary_pattern, text)
        if match:
            return match.group(1)
        return "Not listed"

    def score_job(self, title, description):
        """Calculates a score (0-100+) based on keyword matches."""
        score = 0
        text = (title + " " + description).lower()
        
        # Return a tuple: (score, location_status)
        location_status = "Remote"

        # Check Negative Keywords first (Immediate Disqualification)
        for kw in config.NEGATIVE_KEYWORDS:
            if kw.lower() in title.lower(): # Stricter on title for negatives
                return -1, "N/A"

        # Tier 1 Scoring
        tier1_match = False
        for kw in config.TIER_1_KEYWORDS:
            if kw.lower() in text:
                score += 50 # High value match
                tier1_match = True
                # If it's in the title, bonus points
                if kw.lower() in title.lower():
                    score += 30

        # Tier 2 Scoring
        for kw in config.TIER_2_KEYWORDS:
            if kw.lower() in text:
                score += 15
        
        # CRITICAL FILTER: The "Marketing Trap"
        # If the job is in a "Marketing" feed but the TITLE doesn't explicitly mention 
        # PR/Comms keywords, it is likely a Product/Growth marketing role.
        # We kill the score to prevent false positives.
        is_marketing_title = "marketing" in title.lower()
        has_pr_title = any(kw.lower() in title.lower() for kw in config.TIER_1_KEYWORDS + config.TIER_2_KEYWORDS)
        
        if is_marketing_title and not has_pr_title:
            return -1, "N/A" # Immediate discard. A "Marketing Manager" is not a "PR Manager".

        # Location Scoring (Los Angeles / Hybrid)
        la_match = False
        for loc in config.LOCATIONS:
            if loc.lower() in text:
                score += 40 # Big boost for LA based
                la_match = True
                location_status = f"📍 {loc} (Likely Hybrid)"
                break
        
        if "hybrid" in text:
            if la_match:
                score += 20 # Perfect combo
                location_status += " - Hybrid"
            else:
                # Hybrid but NOT in LA?
                # We need to be careful. If it says "Hybrid in New York", we don't want it.
                # But simple text search might miss "Remote (Hybrid optional)".
                # For now, we won't penalize, but we won't boost.
                if "remote" not in title.lower():
                     # If it's Hybrid and NOT LA, and NOT explicitly Remote in title, it might be bad.
                     pass

        return score, location_status

    def fetch_prsa(self):
        print("Fetching PRSA (Public Relations Society of America)...")
        urls = [config.URLS["PRSA_Remote"], config.URLS["PRSA_LA"]]
        for url in urls:
            try:
                # PRSA RSS feeds are standard
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    score, loc_status = self.score_job(entry.title, entry.description)
                    if score >= config.MIN_SCORE_THRESHOLD:
                        self.jobs.append({
                            "title": entry.title,
                            "company": entry.get("author", "Unknown"), # PRSA often puts company in author or title
                            "url": entry.link,
                            "score": score,
                            "salary": self.extract_salary(entry.description),
                            "location": loc_status,
                            "source": "PRSA Jobcenter"
                        })
            except Exception as e:
                print(f"Error fetching PRSA: {e}")

    def fetch_themuse(self):
        print("Fetching The Muse...")
        try:
            # The Muse API returns JSON
            response = requests.get(config.URLS["TheMuse"])
            data = response.json()
            for job in data.get("results", []):
                title = job.get("name", "")
                description = job.get("contents", "")
                company = job.get("company", {}).get("name", "Unknown")
                url = job.get("refs", {}).get("landing_page", "")
                
                # The Muse locations are a list
                locations = [loc.get("name") for loc in job.get("locations", [])]
                loc_str = ", ".join(locations)
                
                score, loc_status = self.score_job(title, description)
                
                # Boost score if it's explicitly in LA from the API data
                if "Los Angeles" in loc_str:
                    score += 20
                    loc_status = "📍 Los Angeles"

                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": title,
                        "company": company,
                        "url": url,
                        "score": score,
                        "salary": self.extract_salary(description),
                        "location": loc_status,
                        "source": "The Muse"
                    })
        except Exception as e:
            print(f"Error fetching The Muse: {e}")

    def fetch_entertainment_careers(self):
        # This is a placeholder. Real scraping of EC.net requires Selenium/Playwright 
        # which is heavy for this environment. We will try a basic request, 
        # but if it fails (403), we skip it to avoid crashing.
        print("Fetching EntertainmentCareers.net (Experimental)...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(config.URLS["EntertainmentCareers"], headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # This selector is a guess based on common table structures. 
                # EC.net structure changes often.
                # We look for links that contain "job" in the href
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    title = link.get_text().strip()
                    
                    if "job" in href and len(title) > 10:
                        # We don't have the description here, so we score based on Title only
                        # We give it a slight boost because the SOURCE is high quality
                        score, loc_status = self.score_job(title, title) 
                        
                        # Boost for being on EC.net
                        score += 10 
                        
                        if score >= config.MIN_SCORE_THRESHOLD:
                            full_url = f"https://www.entertainmentcareers.net{href}" if href.startswith("/") else href
                            self.jobs.append({
                                "title": title,
                                "company": "See Listing",
                                "url": full_url,
                                "score": score,
                                "salary": "Check Listing",
                                "location": loc_status,
                                "source": "EntertainmentCareers.net"
                            })
        except Exception as e:
            print(f"Skipping EntertainmentCareers (Anti-bot likely active): {e}")

    def get_jobs(self):
        self.fetch_prsa()
        self.fetch_themuse()
        self.fetch_entertainment_careers()
        self.fetch_weworkremotely()
        # self.fetch_remotive() # Disabled: Too much tech noise
        # self.fetch_working_nomads() # Disabled: Too much tech noise
        self.fetch_remoteok()
        
        # Sort by score descending
        self.jobs.sort(key=lambda x: x['score'], reverse=True)
        return self.jobs
