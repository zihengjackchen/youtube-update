import os
import json
import requests
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_latest_video(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    entry = feed.entries[0]
    return entry.id.split(":")[-1], entry.title

def get_transcript_or_whisper(video_id, api_key):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return transcribe_audio_with_openai(video_id, api_key)

def transcribe_audio_with_openai(video_id, api_key):
    import yt_dlp
    import tempfile

    print(f"[WHISPER] Transcribing {video_id} using OpenAI Whisper API...")
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "audio.mp3")
        yt_dlp.YoutubeDL({
            "format": "bestaudio",
            "outtmpl": filepath,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }).download([url])

        with open(filepath, "rb") as f:
            res = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )
        res.raise_for_status()
        return res.json()["text"]

def summarize_with_gpt4o(text, prompt, api_key):
    print("[GPT-4o] Summarizing transcript...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful summarizer."},
            {"role": "user", "content": f"{prompt}\n\n{text}"}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def send_to_discord(webhook_url, message, video_url):
    print(f"[DISCORD] Sending summary for {video_url}")
    content = f"📺 {video_url}\n\n{message}"
    res = requests.post(webhook_url, json={"content": content})
    res.raise_for_status()

def load_state(path="seen.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_state(state, path="seen.json"):
    with open(path, "w") as f:
        json.dump(state, f)
