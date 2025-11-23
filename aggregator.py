import requests
import feedparser
from bs4 import BeautifulSoup
import time
import random
import config
import re
import cloudscraper
from fake_useragent import UserAgent

class JobAggregator:
    def __init__(self):
        self.jobs = []
        # Browser-like configuration to avoid detection
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.ua = UserAgent()

    def random_sleep(self):
        """Sleeps for a random amount of time to mimic human behavior."""
        sleep_time = random.uniform(2.5, 5.5)
        time.sleep(sleep_time)

    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1', # Do Not Track
            'Upgrade-Insecure-Requests': '1'
        }

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
                print(f"  [SKIP] Negative Keyword '{kw}': {title}")
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
            print(f"  [SKIP] Marketing Trap: {title}")
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
        try:
            response = self.scraper.get(config.URLS["PRSA_Browse"], headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] PRSA returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            # Based on debug analysis, PRSA links are direct <a> tags in the browse list
            # We look for links that do NOT start with / (relative) but are job posts?
            # Actually, WebScribble usually puts job links in <h3> or similar.
            # Let's be broad: Any link with text > 10 chars that isn't a nav link.
            
            found_count = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text().strip()
                
                # Filter out navigation noise
                if len(title) < 10 or "Browse" in title or "Contact" in title or "About" in title:
                    continue
                    
                # PRSA job links usually end in .html or have /job/
                if "/job/" in href or href.endswith(".html"):
                        # Avoid category links "c-public-relations.html"
                    if "c-" in href and "jobs.html" in href:
                        continue

                    full_url = f"https://jobs.prsa.org{href}" if href.startswith("/") else href
                    
                    score, loc_status = self.score_job(title, title)
                    if score >= config.MIN_SCORE_THRESHOLD:
                        self.jobs.append({
                            "title": title,
                            "company": "See Listing",
                            "url": full_url,
                            "score": score,
                            "salary": "Check Listing",
                            "location": loc_status,
                            "source": "PRSA Jobcenter"
                        })
                        found_count += 1
            print(f"  - Found {found_count} matches from PRSA")
        except Exception as e:
            print(f"Error fetching PRSA: {e}")

    def fetch_themuse(self):
        print("Fetching The Muse...")
        try:
            # The Muse API returns JSON
            response = self.scraper.get(config.URLS["TheMuse"], headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] The Muse returned status code: {response.status_code}")
                return

            data = response.json()
            found_count = 0
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
                    found_count += 1
            print(f"  - Found {found_count} matches from The Muse")
        except Exception as e:
            print(f"Error fetching The Muse: {e}")

    def fetch_odwyers(self):
        if "ODwyers" not in config.URLS:
            return
            
        print("Fetching O'Dwyer's PR Jobs...")
        try:
            response = self.scraper.get(config.URLS["ODwyers"], headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] O'Dwyer's returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            # O'Dwyer's is a simple table or list. 
            # Looking for <tr> with job details.
            # This is a guess at their structure, usually they have <a> tags with job titles.
            found_count = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text().strip()
                
                # Filter for job-like links (usually contain 'job' or are in a specific list)
                # O'Dwyer's links often look like "job_view.php?job_id=..."
                if "job_view" in href or "job_id" in href:
                    score, loc_status = self.score_job(title, title)
                    if score >= config.MIN_SCORE_THRESHOLD:
                        full_url = f"https://www.odwyerpr.com/pr_jobs/{href}" if not href.startswith("http") else href
                        self.jobs.append({
                            "title": title,
                            "company": "See Listing",
                            "url": full_url,
                            "score": score,
                            "salary": "Check Listing",
                            "location": loc_status,
                            "source": "O'Dwyer's PR"
                        })
                        found_count += 1
            print(f"  - Found {found_count} matches from O'Dwyer's")
        except Exception as e:
            print(f"Error fetching O'Dwyer's: {e}")

    def fetch_entertainment_careers(self):
        print("Fetching EntertainmentCareers.net (Stealth Mode)...")
        try:
            # Use cloudscraper to bypass Cloudflare/403
            response = self.scraper.get(config.URLS["EntertainmentCareers"], headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] EntertainmentCareers returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            found_count = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text().strip()
                
                # Precise Logic based on Debug Analysis:
                # Valid Job URL: /company-name/job-title/job/123456/
                # We look for "/job/" in the path AND a numeric ID at the end (usually)
                
                if "/job/" in href and len(title) > 10:
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
                        found_count += 1
            print(f"  - Found {found_count} matches from EntertainmentCareers")
        except Exception as e:
            print(f"Skipping EntertainmentCareers: {e}")

    def fetch_weworkremotely(self):
        print("Fetching WeWorkRemotely...")
        # We only use the Management feed now as per config
        urls = [config.URLS["WeWorkRemotely_Management"]]
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

    def fetch_remoteok(self):
        print("Fetching RemoteOK...")
        try:
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

    def fetch_greenhouse(self, url, company_name):
        print(f"Fetching {company_name} (Greenhouse)...")
        self.random_sleep()
        try:
            response = self.scraper.get(url, headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] {company_name} returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            found_count = 0
            
            # Greenhouse Structure Analysis (Updated):
            # Some boards use div.opening, others use tr.job-post or similar.
            # A24 uses a table-like structure: div.job-posts--table
            # We need to be more generic to catch different themes.
            
            # Strategy 1: Look for ANY link that contains "/jobs/"
            # Greenhouse job links are usually /jobs/123456 or similar (relative)
            # or absolute https://boards.greenhouse.io/company/jobs/12345
            # NEW: A24 and Axios use 'https://job-boards.greenhouse.io/...' which is different!
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Check if it looks like a job link
                # We need to catch:
                # 1. /jobs/12345 (Relative)
                # 2. https://boards.greenhouse.io/.../jobs/12345
                # 3. https://job-boards.greenhouse.io/.../jobs/12345
                
                if "/jobs/" in href:
                    title = link.get_text().strip()
                    if not title: continue # Skip empty links
                    
                    # Try to find location in the same container (parent or sibling)
                    # This is tricky without specific structure, so we default to Unknown
                    # unless we find a clear location element nearby.
                    location_text = "Unknown"
                    
                    # Common pattern: Link is in a row, location is in a sibling cell/div
                    # Let's check the parent text
                    parent_text = link.parent.get_text().strip() if link.parent else ""
                    if len(parent_text) > len(title):
                        # The parent text likely contains the location too
                        full_text = parent_text
                    else:
                        full_text = title

                    score, loc_status = self.score_job(title, full_text)
                    
                    # Boost for direct agency match
                    score += 15
                    
                    if score >= config.MIN_SCORE_THRESHOLD:
                        # Handle full URLs correctly
                        if href.startswith("http"):
                            full_url = href
                        else:
                            full_url = f"https://boards.greenhouse.io{href}"
                            
                        self.jobs.append({
                            "title": title,
                            "company": company_name,
                            "url": full_url,
                            "score": score,
                            "salary": "Check Listing",
                            "location": loc_status,
                            "source": f"{company_name} (Direct)"
                        })
                        found_count += 1
            print(f"  - Found {found_count} matches from {company_name}")
            
        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    def fetch_lever(self, url, company_name):
        print(f"Fetching {company_name} (Lever)...")
        self.random_sleep()
        try:
            response = self.scraper.get(url, headers=self.get_headers())
            if response.status_code != 200:
                print(f"  [ERROR] {company_name} returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            found_count = 0
            
            # Lever usually lists jobs in a.posting-title
            for link in soup.find_all('a', class_='posting-title'):
                href = link['href']
                
                # Title is in h5 usually
                title_elem = link.find('h5')
                title = title_elem.get_text().strip() if title_elem else link.get_text().strip()
                
                # Location
                loc_elem = link.find('span', class_='sort-by-location')
                location_text = loc_elem.get_text().strip() if loc_elem else "Unknown"
                
                full_text = f"{title} {location_text}"
                
                score, loc_status = self.score_job(title, full_text)
                score += 15 # Boost
                
                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": title,
                        "company": company_name,
                        "url": href,
                        "score": score,
                        "salary": "Check Listing",
                        "location": loc_status,
                        "source": f"{company_name} (Direct)"
                    })
                    found_count += 1
            print(f"  - Found {found_count} matches from {company_name}")
            
        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    def fetch_ats_sources(self):
        """Iterates through configured ATS sources."""
        for source in config.ATS_SOURCES:
            if source["type"] == "greenhouse":
                self.fetch_greenhouse(source["url"], source["name"])
            elif source["type"] == "lever":
                self.fetch_lever(source["url"], source["name"])

    def get_jobs(self):
        self.fetch_prsa()
        self.fetch_themuse()
        self.fetch_entertainment_careers()
        self.fetch_odwyers()
        self.fetch_ats_sources() # NEW: Direct Agency Scraping
        self.fetch_weworkremotely()
        # self.fetch_remotive() # Disabled: Too much tech noise
        # self.fetch_working_nomads() # Disabled: Too much tech noise
        self.fetch_remoteok()
        
        # Sort by score descending
        self.jobs.sort(key=lambda x: x['score'], reverse=True)
        return self.jobs
