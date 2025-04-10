import os

# Load from environment
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_WEBHOOK or not OPENAI_API_KEY:
    raise ValueError("DISCORD_WEBHOOK and OPENAI_API_KEY must be set as environment variables.")

# Channel IDs (from YouTube channel URLs)
CHANNELS = [
    "UCYO_jab_esuFRV4b17AJtAw",  # 3Blue1Brown
    "UClvG3xB6xLPNbvCkzZn2p0A"   # Computerphile
]

# Custom GPT prompt
CUSTOM_PROMPT = (
    "Summarize this video in clear bullet points. "
    "Include key insights or interesting facts. Avoid unnecessary filler."
)

# Interval to check for new videos
POLL_INTERVAL_MINUTES = 60
