import json
import os
import requests
import yt_dlp

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = "seen.json"
PROFILES_FILE = "profiles.txt"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_seen(data):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False})
    print("Telegram response:", r.status_code, r.text)

def get_latest_video(profile_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": 1,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile_url, download=False)
            entries = info.get("entries", [])
            if entries:
                vid = entries[0]
                vid_id = str(vid.get("id"))
                title = vid.get("title", "Video jdida")
                link = vid.get("url") or f"https://vimeo.com/{vid_id}"
                return vid_id, title, link
    except Exception as e:
        print(f"Error checking {profile_url}: {e}")
    return None, None, None

def main():
    seen = load_seen()
    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        profiles = [line.strip() for line in f if line.strip()]

    updated = False
    for profile in profiles:
        vid_id, title, link = get_latest_video(profile)
        if not vid_id:
            continue

        if seen.get(profile) != vid_id:
            seen[profile] = vid_id
            updated = True
            msg = f"🎬 Video jdida f Vimeo!\n\n📌 {title}\n🔗 {link}"
            send_telegram(msg)

    if updated:
        save_seen(seen)

if __name__ == "__main__":
    main()
