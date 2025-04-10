FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg cron curl && rm -rf /var/lib/apt/lists/*

# Copy app source code
COPY app/ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy and apply the cron job
COPY youtube-summarizer-cron /etc/cron.d/youtube-summarizer-cron
RUN chmod 0644 /etc/cron.d/youtube-summarizer-cron
RUN crontab /etc/cron.d/youtube-summarizer-cron

# Create cron log file
RUN touch /var/log/cron.log

# Start cron and stream logs
CMD ["/bin/bash", "-c", "printenv > /etc/environment && cron && tail -f /var/log/cron.log"]
