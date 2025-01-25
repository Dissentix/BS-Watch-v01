#!/usr/bin/env python3

import os
import pytz
import re
import time
import sqlite3
from datetime import datetime
from discord_webhook import DiscordWebhook

# Set the webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1331952876146266215/NbGxlE1fRYFCI8st1vWOfoKC1PKw3rmAxFaFuyNXPVJIEEqqvE3Ug18PlldH_QDabgGs'

# Directories
DOMAINS_DIR = '/root/BS-Watch/program-domains'
HTTPX_DIR = '/root/BS-Watch/sub-discovery'
DATABASE_DIR = '/root/BS-Watch/database'  # Create the 'database' directory here

def find_domains_file():
    """Find the .domains file in the specified directory."""
    for file in os.listdir(DOMAINS_DIR): 
        if file.endswith('.domains'):
            return os.path.join(DOMAINS_DIR, file)
    return None

def get_current_time_in_iran():
    """Get current time in Iran timezone."""
    iran_tz = pytz.timezone('Asia/Tehran')
    return datetime.now(iran_tz).strftime('%Y-%m-%d %H:%M:%S')

def remove_ansi_codes(text):
    """Remove ANSI color codes from text."""
    return re.sub(r'\x1b\[([0-9]{1,2})(;[0-9]{1,2}){0,2}m', '', text)

# Find the target name from the .domains file
filename = find_domains_file()
if not filename:
    print("Error: No .domains file found in the specified directory.")
    exit(1)

# Extract the program name from the file name
program_name = os.path.basename(filename).replace('.domains', '')

# Create the 'database' directory if it doesn't exist
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

# Set the database file path
db_file_path = os.path.join(DATABASE_DIR, f"{program_name}_database.db")

# Connect to SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    status TEXT,
    details TEXT,
    providers TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Find all the .httpx files in the directory
httpx_files = [os.path.join(HTTPX_DIR, f) for f in os.listdir(HTTPX_DIR) if f.endswith('.httpx')]
if not httpx_files:
    print("Error: No .httpx files found in the specified directory.")
    exit(1)

# Send the current time in Iran timezone as the first message
current_time = get_current_time_in_iran()
current_time_message = f":watch: Current time in Iran: {current_time}"

webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=current_time_message)
response = webhook.execute()

if response.status_code != 200:
    print(f"Failed to send current time. HTTP Status: {response.status_code}")

# Track the total number of URLs sent
total_urls_sent = 0
status_counts = {}

# Process each .httpx file
for httpx_file in httpx_files:
    try:
        with open(httpx_file, 'r') as file:
            lines = file.readlines()

        # Extract URLs from the file
        current_urls = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split(' ', 3)  # Assuming the format is URL, status, details, providers
                if len(parts) == 4:
                    url, status, details, providers = parts
                    current_urls.append((url, status, details, providers))

        # Send start message for this file
        start_message = f":incoming_envelope: Started sending URLs from {httpx_file}."
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=start_message)
        webhook.execute()

        # Filter new URLs and store them in the database
        for url, status, details, providers in current_urls:
            # Check if the URL already exists in the database
            cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
            if cursor.fetchone():
                print(f"URL already exists in the database: {url}")
                continue

            # Insert new URL into the database
            cursor.execute("INSERT INTO urls (url, status, details, providers) VALUES (?, ?, ?, ?)",
                           (url, status, details, providers))
            conn.commit()

            # Count the status code
            status_code = status.split(' ')[0]  # Extract the status code
            if status_code not in status_counts:
                status_counts[status_code] = 1
            else:
                status_counts[status_code] += 1

            # Send message to Discord
            message = f"```URL: {url}\n" \
                      f"Status: {remove_ansi_codes(status)}\n" \
                      f"Details: {remove_ansi_codes(details)}\n" \
                      f"Providers: {remove_ansi_codes(providers)}\n```" \
                      f":floppy_disk: (Fresh Asset) has been added to '{program_name}' program DB"

            retries = 0
            while retries < 5:
                webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
                response = webhook.execute()

                if response.status_code == 200:
                    print(f"Message sent successfully for URL: {url}")
                    total_urls_sent += 1
                    break
                elif response.status_code == 429:
                    retry_after = float(response.headers.get('Retry-After', 1))
                    print(f"Rate limited. Retrying in {retry_after} seconds for URL: {url}")
                    time.sleep(retry_after)
                    retries += 1
                else:
                    print(f"Failed to send message for URL: {url}. HTTP Status: {response.status_code}")
                    break

            # Add a 1-second delay between messages
            time.sleep(3)

        # Send end message for this file
        status_summary = "\n".join([f"Status {remove_ansi_codes(code)}: {count}" for code, count in status_counts.items()])
        end_message = f":crossed_swords: Finished sending URLs from : {httpx_file}.\nTotal URLs sent: {len(current_urls)}\n{status_summary}"
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=end_message)
        webhook.execute()

    except Exception as e:
        print(f"Error processing file {httpx_file}: {e}")

# Send a final summary message
final_message = f"All new URLs have been successfully sent to Discord. Total URLs sent: {total_urls_sent}"
webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=final_message)
webhook.execute()

# Close the database connection
conn.close()
