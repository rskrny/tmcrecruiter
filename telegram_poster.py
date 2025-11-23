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

    for job in jobs:
        # Format the message
        # 🎯 SCORE: 85
        # 💼 Role: Public Relations Manager
        # 🏢 Company: Acme Corp
        # 📍 Location: Los Angeles (Likely Hybrid)
        # 💰 Salary: $80k-120k
        # 🔗 Apply: [Link]
        
        message = (
            f"🎯 *SNIPER SCORE: {job['score']}*\n"
            f"💼 *Role:* {job['title']}\n"
            f"🏢 *Company:* {job['company']}\n"
            f"📍 *Location:* {job.get('location', 'Remote')}\n"
            f"💰 *Salary:* {job.get('salary', 'Not listed')}\n"
            f"🌐 *Source:* {job['source']}\n\n"
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
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message: {e}")
