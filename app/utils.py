import os
import json
import requests
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime
import hashlib
import subprocess

TRANSCRIPT_CACHE_DIR = "cache/transcript"
SUMMARY_CACHE_DIR = "cache/summary"
os.makedirs(TRANSCRIPT_CACHE_DIR, exist_ok=True)
os.makedirs(SUMMARY_CACHE_DIR, exist_ok=True)

def get_latest_video(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    entry = feed.entries[0]
    video_id = entry.id.split(":")[-1]
    return {
        "video_id": video_id,
        "title": entry.title,
        "published": entry.published,
        "uploader": entry.author,
        "link": entry.link
    }

def video_is_too_long(video_id):
    from yt_dlp import YoutubeDL
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        duration_sec = info.get("duration", 0)
        is_live = info.get("is_live", False)
        if is_live:
            print(f"[SKIP] {video_id} is a live stream.")
        return is_live or duration_sec > 45 * 60

def transcript_cache_path(video_id):
    return os.path.join(TRANSCRIPT_CACHE_DIR, f"{video_id}.json")

def summary_cache_path(video_id):
    return os.path.join(SUMMARY_CACHE_DIR, f"{video_id}.json")

def get_transcript(video_id, api_key):
    # Check cache
    if os.path.exists(transcript_cache_path(video_id)):
        with open(transcript_cache_path(video_id), "r") as f:
            return json.load(f)["text"]

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'zh-Hans', 'zh-Hant', 'en'])
        text = " ".join([entry["text"] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        text = transcribe_with_gpt4o(video_id, api_key)

    with open(transcript_cache_path(video_id), "w") as f:
        json.dump({"text": text}, f)

    return text

def transcribe_with_gpt4o(video_id, api_key):
    import yt_dlp
    import tempfile
    import glob

    print(f"[TRANSCRIBE] Using GPT-4o-mini for video {video_id}")
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        outtmpl = os.path.join(tmpdir, "%(title)s.%(ext)s")
        audio_path = os.path.join(tmpdir, "trimmed.mp3")

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": outtmpl,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_files = glob.glob(os.path.join(tmpdir, "*.mp3"))
        if not mp3_files:
            raise FileNotFoundError("Audio file not found after yt-dlp processing.")

        full_audio_path = mp3_files[0]

        print(f"[INFO] Trimming audio to 24.5 minutes max")
        subprocess.run([
            "ffmpeg", "-y", "-i", full_audio_path, "-t", "1470",  # 24.5 * 60
            "-c", "copy", audio_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        print(f"[INFO] Uploading audio file of size: {file_size_mb:.2f} MB")

        if file_size_mb > 25:
            raise ValueError("Trimmed audio still exceeds 25MB limit.")

        with open(audio_path, "rb") as f:
            res = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": f},
                data={"model": "gpt-4o-mini-transcribe"}
            )

        res.raise_for_status()
        return res.json()["text"]

def summarize_with_gpt4o(text, prompt, api_key, video_id):
    if os.path.exists(summary_cache_path(video_id)):
        with open(summary_cache_path(video_id), "r") as f:
            return json.load(f)["summary"]

    print("[GPT-4o] Summarizing transcript...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful summarizer for financial information."},
            {"role": "user", "content": f"{prompt}\n\n{text}"}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    summary = response.json()["choices"][0]["message"]["content"]

    with open(summary_cache_path(video_id), "w") as f:
        json.dump({"summary": summary}, f)

    return summary

def send_to_discord(webhook_url, summary, video_data):
    title_link = f"[{video_data['title']}](<{video_data['link']}>)"
    published_time = datetime.strptime(video_data['published'], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")

    content = (
        f"**📺 {title_link}**\n"
        f"👤 Uploader: `{video_data['uploader']}`\n"
        f"🕒 Published: `{published_time}`\n\n"
        f"{summary}"
    )
    print(f"[DISCORD] Sending summary for {video_data['video_id']}")
    res = requests.post(webhook_url, json={"content": content, "allowed_mentions": {"parse": []}})
    res.raise_for_status()

def load_state(path="seen.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_state(state, path="seen.json"):
    with open(path, "w") as f:
        json.dump(state, f)
