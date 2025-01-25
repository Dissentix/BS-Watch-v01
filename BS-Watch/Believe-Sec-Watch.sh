#!/bin/bash

# Function to print messages with color
print_message() {
    local message=$1
    local color=$2
    case $color in
        "green") echo -e "\033[32m$message\033[0m" ;;  # Green
        "blue") echo -e "\033[34m$message\033[0m" ;;   # Blue
        "yellow") echo -e "\033[33m$message\033[0m" ;;  # Yellow
        "red") echo -e "\033[31m$message\033[0m" ;;     # Red
        *) echo "$message" ;;
    esac
}

# Step 1: Execute BS-Watch.py for Subdomain Enumeration 3 times with 3-minute intervals
print_message "Starting the Subdomain Enumeration process And Web Service Discovery by executing BS-Watch.py..." "green"
for i in {1..3}
do
    python3 /root/BS-Watch/BS-Watch.py
    print_message "Subdomain Enumeration completed. Waiting for 3 minutes before rerunning..." "yellow"
    sleep 180  # Wait for 3 minutes
done

# Step 2: Execute send-httpx-discord.py for Web Service Discovery
print_message "Executing send-httpx-discord.py to send the results to Discord..." "blue"
python3 /root/BS-Watch/send-httpx-discord.py

print_message "All processes completed successfully!" "green"
