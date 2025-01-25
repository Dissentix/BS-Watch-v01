#!/usr/bin/env python3

import os
from colorama import Fore, Style, init

# Enable colorama for colored output
init(autoreset=True)

# Directory to store the output files
output_dir = "program-domains"

# Ensure the directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Ask the user for the target name
target_name = input(f"{Fore.CYAN}{Style.BRIGHT}Please enter the target name: ")

# Ask the user for the domains
domains_input = input(f"{Fore.MAGENTA}{Style.BRIGHT}Please enter the domains (separate with commas): ")

# Convert the input string into a list of domains
domains = domains_input.split(',')

# Clean up the domains list by stripping extra spaces
domains = [domain.strip() for domain in domains]

# Create an output filename based on the target name
output_filename = os.path.join(output_dir, f"{target_name}.domains")

# Write the domains into the output file
with open(output_filename, 'w') as file:
    for domain in domains:
        file.write(f"{domain}\n")

# Display success message with the filename
print(f"{Fore.YELLOW}{Style.BRIGHT}Domains have been successfully saved in the file {Fore.GREEN}{output_filename}{Fore.YELLOW}.")
