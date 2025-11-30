import requests
import feedparser
from bs4 import BeautifulSoup
import time
import random
import config
import re
import cloudscraper
from fake_useragent import UserAgent
from curl_cffi import requests as cffi_requests

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

    def fetch_job_details(self, url):
        """Fetches the job detail page to extract Salary and Location."""
        try:
            self.random_sleep()
            response = self.scraper.get(url, headers=self.get_headers())
            if response.status_code != 200:
                return "Check Listing", "Unknown"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(" ", strip=True)
            
            # Salary
            salary = self.extract_salary(text)
            
            # Location
            location = "Unknown"
            if "hybrid" in text.lower():
                location = "Hybrid"
            elif "remote" in text.lower():
                location = "Remote"
            elif "on-site" in text.lower() or "onsite" in text.lower():
                location = "On-site"
                
            # Try to find specific location metadata if possible (Greenhouse/Lever specific)
            # Greenhouse often has <div class="location">
            gh_loc = soup.find(class_="location")
            if gh_loc:
                location = f"{gh_loc.get_text().strip()} ({location})"
                
            return salary, location
            
        except Exception:
            return "Check Listing", "Unknown"

    def score_job(self, title, description):
        """Calculates a score (0-100+) based on keyword matches."""
        score = 0
        text = (title + " " + description).lower()
        
        # Return a tuple: (score, location_status)
        location_status = "Remote"

        # Check Negative Keywords first (Immediate Disqualification)
        for kw in config.NEGATIVE_KEYWORDS:
            # Use regex for word boundaries to avoid "Intern" matching "International" or "Internal"
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, title.lower()): 
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
        # REVISED: In Entertainment/Music, "Marketing" is often PR-adjacent (Artist Marketing).
        # We removed the hard block. Instead, we rely on NEGATIVE_KEYWORDS to catch "Growth/Performance" marketing.
        # We also give a score boost to "Marketing" titles to help them pass the strict threshold
        # if they are not explicitly "Growth" or "Digital".
        if "marketing" in title.lower():
            score += 30 # Treat as a valid keyword, similar to Tier 1, but rely on negatives to filter bad ones.

        # STRICTER FILTERING:
        # If no Tier 1 keyword is present, we require a very high score (meaning multiple Tier 2s + Location)
        # or we discard it. This prevents "Executive Assistant" from passing just because it's in LA.
        if not tier1_match and score < 60: # Lowered from 70 to 60 to allow Marketing (30) + Location (40) to pass
             # print(f"  [SKIP] Weak Match (No Tier 1): {title} ({score})")
             return -1, "N/A"

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

    def fetch_indeed(self):
        print("Fetching Indeed (Experimental with curl_cffi)...")
        try:
            # Use curl_cffi with chrome impersonation to bypass TLS fingerprinting
            response = cffi_requests.get(
                config.URLS["Indeed"], 
                impersonate="chrome",
                headers={
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.google.com/',
                }
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] Indeed returned status code: {response.status_code}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            found_count = 0
            
            # Indeed structure is complex and changes often.
            # We look for the main job card container.
            # Common classes: 'job_seen_beacon', 'resultContent', 'cardOutline'
            
            # Strategy: Find all <h2> with class 'jobTitle'
            job_titles = soup.find_all('h2', class_=lambda x: x and 'jobTitle' in x)
            
            for h2 in job_titles:
                link = h2.find('a')
                if not link: continue
                
                title = link.get_text().strip()
                href = link['href']
                full_url = f"https://www.indeed.com{href}" if href.startswith("/") else href
                
                # Try to find company and location relative to the title
                # Usually in the same 'resultContent' or parent div
                card = h2.find_parent('div', class_='job_seen_beacon') or h2.find_parent('td', class_='resultContent')
                
                company = "Indeed Listing"
                location = "Los Angeles, CA" # Default since we searched for it
                
                if card:
                    company_elem = card.find('span', class_='companyName') or card.find('span', attrs={'data-testid': 'company-name'})
                    if company_elem:
                        company = company_elem.get_text().strip()
                        
                    location_elem = card.find('div', class_='companyLocation') or card.find('div', attrs={'data-testid': 'text-location'})
                    if location_elem:
                        location = location_elem.get_text().strip()

                score, loc_status = self.score_job(title, title) # Description not available on list view
                
                # If location matches our target, boost score
                if "Los Angeles" in location or "CA" in location:
                    score += 10
                    
                if score >= config.MIN_SCORE_THRESHOLD:
                    self.jobs.append({
                        "title": title,
                        "company": company,
                        "url": full_url,
                        "score": score,
                        "salary": "Check Listing",
                        "location": location,
                        "source": "Indeed"
                    })
                    found_count += 1
            
            print(f"  - Found {found_count} matches from Indeed")
            
        except Exception as e:
            print(f"Error fetching Indeed: {e}")

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
            # Use curl_cffi to avoid SSL errors and detection
            response = cffi_requests.get(
                url, 
                impersonate="chrome",
                headers=self.get_headers()
            )
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
                    # Use separator=" " to avoid "TitleLocation" mashups
                    title = link.get_text(" ").strip()
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
                        
                        # DEEP SCRAPE: Fetch details for Salary & Better Location
                        salary, detailed_loc = self.fetch_job_details(full_url)
                        
                        # Prefer detailed location if found
                        final_loc = detailed_loc if detailed_loc != "Unknown" else loc_status

                        self.jobs.append({
                            "title": title,
                            "company": company_name,
                            "url": full_url,
                            "score": score,
                            "salary": salary,
                            "location": final_loc,
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
            # Use curl_cffi to avoid SSL errors and detection
            response = cffi_requests.get(
                url, 
                impersonate="chrome",
                headers=self.get_headers()
            )
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
                    # DEEP SCRAPE: Fetch details for Salary & Better Location
                    salary, detailed_loc = self.fetch_job_details(href)
                    
                    # Prefer detailed location if found
                    final_loc = detailed_loc if detailed_loc != "Unknown" else loc_status

                    self.jobs.append({
                        "title": title,
                        "company": company_name,
                        "url": href,
                        "score": score,
                        "salary": salary,
                        "location": final_loc,
                        "source": f"{company_name} (Direct)"
                    })
                    found_count += 1
            print(f"  - Found {found_count} matches from {company_name}")
            
        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    def fetch_workday(self, api_url, company_name, base_url):
        """Fetches jobs from Workday-based career sites (Disney, Condé Nast, etc.)."""
        print(f"Fetching {company_name} (Workday)...")
        self.random_sleep()
        try:
            import json as json_lib
            
            # Workday requires a session-based approach:
            # 1. Visit the main careers page first to get cookies
            # 2. Then make the API call with those cookies
            session = cffi_requests.Session(impersonate="chrome")
            
            # Step 1: Get cookies from main page
            session.get(base_url, timeout=15)
            
            # Step 2: Make API call
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
            }
            # Note: Some Workday sites have issues with limit > 20
            payload = json_lib.dumps({'limit': 20, 'offset': 0})
            
            response = session.post(
                api_url,
                headers=headers,
                data=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] {company_name} returned status code: {response.status_code}")
                return
            
            data = response.json()
            found_count = 0
            
            for job in data.get("jobPostings", []):
                title = job.get("title", "")
                location_text = job.get("locationsText", "Unknown")
                external_path = job.get("externalPath", "")
                
                full_text = f"{title} {location_text}"
                score, loc_status = self.score_job(title, full_text)
                score += 20  # Major entertainment company boost
                
                if score >= config.MIN_SCORE_THRESHOLD:
                    full_url = f"{base_url}{external_path}"
                    
                    self.jobs.append({
                        "title": title,
                        "company": company_name,
                        "url": full_url,
                        "score": score,
                        "salary": "Check Listing",
                        "location": location_text,
                        "source": f"{company_name} (Direct)"
                    })
                    found_count += 1
                    
            print(f"  - Found {found_count} matches from {company_name}")
            
        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    def fetch_netflix(self, api_url, company_name):
        """Fetches jobs from Netflix's custom career API."""
        print(f"Fetching {company_name} (Custom API)...")
        self.random_sleep()
        try:
            # Netflix uses a GET request with limit param
            response = cffi_requests.get(
                f"{api_url}?limit=100",
                impersonate="chrome",
                headers=self.get_headers(),
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] {company_name} returned status code: {response.status_code}")
                return
            
            data = response.json()
            found_count = 0
            
            for job in data.get("positions", []):
                title = job.get("name", "")
                location_text = job.get("location", "Unknown")
                job_id = job.get("id", "")
                
                # Netflix also provides department info
                department = job.get("department", "")
                full_text = f"{title} {location_text} {department}"
                
                score, loc_status = self.score_job(title, full_text)
                score += 25  # Netflix is a prime target - big boost
                
                if score >= config.MIN_SCORE_THRESHOLD:
                    # Netflix job URLs follow this pattern
                    full_url = f"https://jobs.netflix.com/jobs/{job_id}"
                    
                    self.jobs.append({
                        "title": title,
                        "company": company_name,
                        "url": full_url,
                        "score": score,
                        "salary": "Check Listing",
                        "location": location_text if location_text else loc_status,
                        "source": f"{company_name} (Direct)"
                    })
                    found_count += 1
                    
            print(f"  - Found {found_count} matches from {company_name}")
            
        except Exception as e:
            print(f"Error fetching {company_name}: {e}")

    def fetch_smartrecruiters(self, company_url, company_name):
        """Fetches jobs from SmartRecruiters (NBCUniversal, etc.)."""
        print(f"Fetching {company_name} (SmartRecruiters)...")
        self.random_sleep()
        try:
            # SmartRecruiters API endpoint
            company_id = company_url.split('/')[-1]
            api_url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
            
            response = cffi_requests.get(
                api_url,
                impersonate="chrome",
                headers=self.get_headers(),
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] {company_name} returned status code: {response.status_code}")
                return
            
            data = response.json()
            found_count = 0
            
            for job in data.get("content", []):
                title = job.get("name", "")
                location_data = job.get("location", {})
                location_text = location_data.get("city", "") or location_data.get("region", "") or "Unknown"
                job_id = job.get("id", "")
                
                full_text = f"{title} {location_text}"
                score, loc_status = self.score_job(title, full_text)
                score += 25  # Major entertainment company boost
                
                if score >= config.MIN_SCORE_THRESHOLD:
                    full_url = f"https://jobs.smartrecruiters.com/{company_id}/{job_id}"
                    
                    self.jobs.append({
                        "title": title,
                        "company": company_name,
                        "url": full_url,
                        "score": score,
                        "salary": "Check Listing",
                        "location": location_text,
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
            elif source["type"] == "workday":
                self.fetch_workday(source["url"], source["name"], source.get("base_url", ""))
            elif source["type"] == "netflix":
                self.fetch_netflix(source["url"], source["name"])
            elif source["type"] == "smartrecruiters":
                self.fetch_smartrecruiters(source["url"], source["name"])

    def get_jobs(self):
        self.fetch_prsa()
        self.fetch_themuse()
        # self.fetch_indeed() # Disabled: 403 Forbidden (Anti-bot)
        self.fetch_entertainment_careers()
        self.fetch_odwyers()
        self.fetch_ats_sources() # Direct Agency Scraping (Greenhouse, Lever, Workday, Netflix)
        self.fetch_weworkremotely()
        # self.fetch_remotive() # Disabled: Too much tech noise
        # self.fetch_working_nomads() # Disabled: Too much tech noise
        self.fetch_remoteok()
        
        # Sort by score descending
        self.jobs.sort(key=lambda x: x['score'], reverse=True)
        return self.jobs
