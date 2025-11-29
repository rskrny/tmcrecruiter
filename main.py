from aggregator import JobAggregator
import data_manager
import telegram_poster
from gemini_filter import GeminiJobFilter
import os
import sys

def main():
    print("=" * 60)
    print(" SNIPER JOB BOT - AI-Powered Job Hunting")
    print("=" * 60)
    
    # Check for Gemini API key
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    use_gemini = bool(gemini_api_key)
    
    if use_gemini:
        print("[OK] Gemini API key found - AI filtering enabled")
    else:
        print("[WARNING] No GEMINI_API_KEY - falling back to keyword-only filtering")
    
    # =========================================================================
    # STAGE 1: Wide-Net Job Collection (Python keyword filtering)
    # =========================================================================
    print("\n" + "-" * 60)
    print("STAGE 1: Aggregating Jobs (Keyword-Based Wide Net)")
    print("-" * 60)
    
    aggregator = JobAggregator()
    all_jobs = aggregator.get_jobs()
    print(f"\n[OK] Stage 1 complete: {len(all_jobs)} potential matches from all sources")

    # =========================================================================
    # DEDUPE - Filter out jobs we've already seen/sent
    # =========================================================================
    new_jobs = data_manager.filter_new_jobs(all_jobs)
    print(f"\n[OK] After deduplication: {len(new_jobs)} NEW jobs to evaluate")
    
    if not new_jobs:
        print("\n[INFO] No new jobs found. Exiting.")
        data_manager.save_seen_jobs([])  # Touch the file
        return

    # =========================================================================
    # STAGE 2: Gemini AI Filtering (Smart Relevance Scoring)
    # =========================================================================
    if use_gemini and new_jobs:
        print("\n" + "-" * 60)
        print("STAGE 2: Gemini AI Relevance Filtering")
        print("-" * 60)
        
        gemini_filter = GeminiJobFilter(gemini_api_key)
        filtered_jobs = gemini_filter.filter_jobs(new_jobs, min_score=7)
        
        print(f"\n[OK] Stage 2 complete: {len(filtered_jobs)} jobs scored 7+ by Gemini")
        
        # Sort by Gemini score (highest first)
        filtered_jobs.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        jobs_to_post = filtered_jobs
    else:
        # Fallback: No Gemini, just use original scoring
        print("\n[WARNING] Skipping Stage 2 (no API key). Using keyword scores only.")
        jobs_to_post = sorted(new_jobs, key=lambda x: x.get('score', 0), reverse=True)[:10]

    # =========================================================================
    # POST TO TELEGRAM - TOP 5 ONLY
    # =========================================================================
    if jobs_to_post:
        print("\n" + "-" * 60)
        print(f"[INFO] Selecting TOP 5 jobs from {len(jobs_to_post)} candidates")
        print("-" * 60)
        
        # Only send TOP 5 most relevant jobs
        top_jobs = jobs_to_post[:5]
        
        print(f"\nTop 5 Jobs to Post:")
        for i, job in enumerate(top_jobs):
            score = job.get('ai_score', job.get('score', 0))
            print(f"  {i+1}. [{score}/10] {job['title']} @ {job['company']}")
        
        telegram_poster.post_to_telegram(top_jobs)
    else:
        print("\n[INFO] No jobs passed the AI relevance filter. Nothing to post.")

    # =========================================================================
    # SAVE SEEN JOBS
    # =========================================================================
    # Save ALL new job URLs (both posted and not posted) to avoid reprocessing
    new_urls = [job['url'] for job in new_jobs]
    data_manager.save_seen_jobs(new_urls)
    
    print("\n" + "=" * 60)
    print("[OK] Sniper Job Bot Finished")
    print("=" * 60)

if __name__ == "__main__":
    main()
