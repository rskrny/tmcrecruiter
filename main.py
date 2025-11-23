from aggregator import JobAggregator
import data_manager
import telegram_poster
import sys

def main():
    print("--- Sniper Job Bot Started ---")
    
    # 1. Aggregate Jobs
    aggregator = JobAggregator()
    all_jobs = aggregator.get_jobs()
    print(f"Found {len(all_jobs)} potential matches based on keywords.")

    # 2. Filter Duplicates
    new_jobs = data_manager.filter_new_jobs(all_jobs)
    print(f"Found {len(new_jobs)} NEW matches after deduplication.")

    if new_jobs:
        # 3. Post to Telegram
        # Only post the top 10 to avoid spamming if there's a backlog
        jobs_to_post = new_jobs[:10]
        telegram_poster.post_to_telegram(jobs_to_post)
    else:
        print("No new jobs found to post.")

    # 4. Save Seen Jobs
    # We save ALL new jobs found, even if we didn't post them all (to avoid reposting later)
    # Or we can just save the ones we posted. 
    # Better strategy: Save all 'new_jobs' URLs so we don't process them again.
    # ALWAYS call this to ensure the file is created/touched
    new_urls = [job['url'] for job in new_jobs]
    data_manager.save_seen_jobs(new_urls)
    
    print("--- Sniper Job Bot Finished ---")

if __name__ == "__main__":
    main()
