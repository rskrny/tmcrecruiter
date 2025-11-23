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
        
        # Penalty for "Marketing" if no Tier 1 match found (to filter out generic marketing)
        if "marketing" in title.lower() and not tier1_match:
            score -= 30

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

    def fetch_weworkremotely(self):
        print("Fetching WeWorkRemotely...")
        urls = [config.URLS["WeWorkRemotely_Marketing"], config.URLS["WeWorkRemotely_Management"]]
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    score, loc_status = self.score_job(entry.title, entry.description)
                    if score >= config.MIN_SCORE_THRESHOLD:
                        self.jobs.append({
                            "title": entry.title,
                            "company": entry.get("author", "Unknown"),
                            "url": entry.link,
                            "score": score,
                            "salary": self.extract_salary(entry.description),
                            "location": loc_status,
                            "source": "WeWorkRemotely"
                        })
            except Exception as e:
                print(f"Error fetching WWR: {e}")

    def fetch_remotive(self):
        print("Fetching Remotive...")
        try:
            response = requests.get(config.URLS["Remotive"])
            data = response.json()
            for job in data.get("jobs", []):
                score, loc_status = self.score_job(job["title"], job["description"])
                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": job["title"],
                        "company": job["company_name"],
                        "url": job["url"],
                        "score": score,
                        "salary": job.get("salary") or self.extract_salary(job["description"]),
                        "location": loc_status,
                        "source": "Remotive"
                    })
        except Exception as e:
            print(f"Error fetching Remotive: {e}")

    def fetch_working_nomads(self):
        print("Fetching Working Nomads...")
        try:
            feed = feedparser.parse(config.URLS["WorkingNomads"])
            for entry in feed.entries:
                score, loc_status = self.score_job(entry.title, entry.description)
                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": entry.title,
                        "company": "Unknown (See Link)", # RSS often hides company in title
                        "url": entry.link,
                        "score": score,
                        "salary": self.extract_salary(entry.description),
                        "location": loc_status,
                        "source": "Working Nomads"
                    })
        except Exception as e:
            print(f"Error fetching Working Nomads: {e}")

    def fetch_remoteok(self):
        # RemoteOK is tricky with bot protection. We'll try a simple RSS parse with headers.
        print("Fetching RemoteOK...")
        try:
            # Sometimes feedparser fails on RemoteOK due to cloudflare, 
            # but let's try standard approach first.
            feed = feedparser.parse(config.URLS["RemoteOK"])
            for entry in feed.entries:
                score, loc_status = self.score_job(entry.title, entry.description)
                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": entry.title,
                        "company": entry.get("author", "Unknown"),
                        "url": entry.link,
                        "score": score,
                        "salary": self.extract_salary(entry.description),
                        "location": loc_status,
                        "source": "RemoteOK"
                    })
        except Exception as e:
            print(f"Error fetching RemoteOK: {e}")

    def get_jobs(self):
        self.fetch_weworkremotely()
        self.fetch_remotive()
        self.fetch_working_nomads()
        self.fetch_remoteok()
        
        # Sort by score descending
        self.jobs.sort(key=lambda x: x['score'], reverse=True)
        return self.jobs
