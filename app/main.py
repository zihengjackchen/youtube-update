import config
from utils import *

seen = load_state()

for channel_id, prompt in config.CHANNELS.items():
    video_data = get_latest_video(channel_id)
    video_id = video_data["video_id"]

    if seen.get(channel_id) == video_id:
        print(f"[SKIP] No new video for {channel_id}")
        continue

    if video_is_too_long(video_id):
        print(f"[SKIP] Video {video_id} is a stream or longer than 45 minutes")
        continue

    print(f"[NEW VIDEO] {video_data['title']} ({video_id})")

    try:
        transcript = get_transcript(video_id, config.OPENAI_API_KEY)
        summary = summarize_with_gpt4o(transcript, prompt, config.OPENAI_API_KEY, video_id)
        send_to_discord(config.DISCORD_WEBHOOK, summary, video_data)
        seen[channel_id] = video_id
        save_state(seen)
    except Exception as e:
        print(f"[ERROR] Failed to process {video_id}: {e}")
