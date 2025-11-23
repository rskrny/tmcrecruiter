import json
import os

DATA_FILE = "seen_jobs.json"

def load_seen_jobs():
    """Loads the list of previously processed job URLs."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_seen_jobs(job_urls):
    """Saves the list of processed job URLs to avoid duplicates."""
    # We only keep the last 1000 to prevent the file from growing infinitely, 
    # though for this use case, infinite is probably fine for a long time.
    # Let's keep it simple.
    
    # Load existing to merge (in case we want to append, but usually we pass the full updated list)
    # Actually, better strategy: Read current, add new, save back.
    
    current_seen = set(load_seen_jobs())
    current_seen.update(job_urls)
    
    with open(DATA_FILE, 'w') as f:
        json.dump(list(current_seen), f)

def filter_new_jobs(jobs):
    """Accepts a list of job dictionaries and returns only the ones not seen before."""
    seen_urls = set(load_seen_jobs())
    new_jobs = []
    
    for job in jobs:
        if job['url'] not in seen_urls:
            new_jobs.append(job)
            
    return new_jobs
