# Updates - Sniper Job Bot

## Recent Changes (Latest)

### 1. Enhanced Scraping Engine (`curl_cffi`)
- **Problem**: The previous scraper (`cloudscraper`) was getting blocked by some ATS boards (Greenhouse, Lever) and was unable to handle modern TLS fingerprinting requirements, leading to `SSLEOFError` or 403 Forbidden responses.
- **Solution**: Integrated `curl_cffi`, a library that wraps `curl-impersonate`. This allows the bot to mimic the exact TLS fingerprint of a real Chrome browser.
- **Implementation**:
    - Installed `curl_cffi` via pip.
    - Updated `aggregator.py` to use `curl_cffi`'s `requests` drop-in replacement for `fetch_greenhouse` and `fetch_lever`.
    - This resolves the SSL handshake errors and improves the bot's stealth.

### 2. Indeed Integration (Disabled)
- **Status**: Attempted but currently disabled.
- **Details**: Added logic to scrape Indeed using `curl_cffi`. However, Indeed's anti-bot protections are extremely aggressive (Cloudflare Turnstile + behavioral analysis), resulting in persistent 403 Forbidden errors even with TLS impersonation.
- **Action**: The `fetch_indeed` method exists in `aggregator.py` but is commented out in the main execution loop to prevent crashes/errors during the run.

### 3. Dependency Updates
- Added `curl_cffi` to the project.
- If you move this bot to another machine, remember to run:
  ```bash
  pip install curl_cffi
  ```

## How to Run
The bot continues to function as before:
```bash
python main.py
```
