import requests
import sys

def get_chat_id(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    print(f"Checking: {url}")
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")
        return

    if not data.get('ok'):
        print(f"Error from Telegram: {data}")
        return

    results = data.get('result', [])
    
    if not results:
        print("\n❌ No updates found.")
        print("1. Make sure you added the bot to the channel as an Admin.")
        print("2. Send a new message (e.g., 'Hello') to the channel.")
        print("3. Run this script again.")
        return

    print("\n✅ Found the following Chat IDs:\n")
    for update in results:
        # Check for channel posts
        if 'channel_post' in update:
            chat = update['channel_post']['chat']
            print(f"📢 Channel: {chat.get('title')}")
            print(f"🆔 ID: {chat['id']}")
            print("-" * 30)
        
        # Check for direct messages or group messages
        elif 'message' in update:
            chat = update['message']['chat']
            print(f"💬 Chat Type: {chat['type']}")
            print(f"👤 Name: {chat.get('title') or chat.get('username') or chat.get('first_name')}")
            print(f"🆔 ID: {chat['id']}")
            print("-" * 30)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_id.py <YOUR_BOT_TOKEN>")
    else:
        get_chat_id(sys.argv[1])
