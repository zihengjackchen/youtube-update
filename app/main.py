import time
import config
from utils import get_latest_video, get_transcript_or_whisper, summarize_with_gpt4o, send_to_discord, load_state, save_state

seen = load_state()

while True:
    for channel_id in config.CHANNELS:
        video_id, title = get_latest_video(channel_id)
        if seen.get(channel_id) != video_id:
            print(f"[NEW VIDEO] {title} ({video_id})")
            try:
                text = get_transcript_or_whisper(video_id, config.OPENAI_API_KEY)
                summary = summarize_with_gpt4o(text, config.CUSTOM_PROMPT, config.OPENAI_API_KEY)
                send_to_discord(config.DISCORD_WEBHOOK, summary, f"https://youtu.be/{video_id}")
                seen[channel_id] = video_id
                save_state(seen)
            except Exception as e:
                print(f"[ERROR] Failed to process {video_id}: {e}")
        else:
            print(f"[SKIP] No new video for {channel_id}")
    print(f"Sleeping {config.POLL_INTERVAL_MINUTES} minutes...")
    time.sleep(config.POLL_INTERVAL_MINUTES * 60)
