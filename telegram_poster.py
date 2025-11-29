import requests
import os
import sys

def post_to_telegram(jobs):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Error: Telegram credentials not found in environment variables.")
        return

    print(f"Posting {len(jobs)} jobs to Telegram...")

    for i, job in enumerate(jobs):
        # New format with AI analysis
        ai_score = job.get('ai_score', job.get('score', 0))
        ai_reasoning = job.get('ai_reasoning', 'No AI analysis available')
        ai_highlights = job.get('ai_highlights', [])
        requirements = job.get('ai_requirements', [])
        
        # Build requirements section
        if requirements:
            req_text = "\n".join([f"  • {req}" for req in requirements[:4]])
        elif ai_highlights:
            req_text = "\n".join([f"  • {h}" for h in ai_highlights[:4]])
        else:
            req_text = "  • See full listing for details"
        
        # Match rating display (stars)
        stars = "⭐" * min(ai_score, 10) if ai_score else "N/A"
        
        message = (
            f"💼 *{job['title']}*\n"
            f"🏢 {job['company']}\n\n"
            f"🤖 *AI Analysis:*\n_{ai_reasoning}_\n\n"
            f"📍 *Location:* {job.get('location', 'Remote')}\n\n"
            f"📋 *Key Points:*\n{req_text}\n\n"
            f"🎯 *Match Rating:* {ai_score}/10 {stars}\n\n"
            f"🔗 [Apply Here]({job['url']})"
        )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"  [{i+1}/{len(jobs)}] Posted: {job['title']} @ {job['company']}")
        except requests.exceptions.RequestException as e:
            print(f"  [{i+1}/{len(jobs)}] Failed to send: {e}")
