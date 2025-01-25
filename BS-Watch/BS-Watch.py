#!/usr/bin/env python3

import subprocess
import os
from colorama import Fore, Style, init

# Enable colorama for colored output
init(autoreset=True)

# Function to find the .domains file in the "program-domains" directory
def find_domains_file():
    program_domains_dir = "/root/BS-Watch/program-domains"
    if not os.path.exists(program_domains_dir):
        print(f"{Fore.RED}{Style.BRIGHT}Error: Directory '{program_domains_dir}' does not exist.")
        exit(1)

    for file in os.listdir(program_domains_dir):
        if file.endswith('.domains'):
            return os.path.join(program_domains_dir, file)
    return None

# Try to find the .domains file
filename = find_domains_file()

if filename is None:
    print(f"{Fore.RED}{Style.BRIGHT}Error: No .domains file found in the 'program-domains' directory.")
    exit(1)

# Create a directory for storing outputs
output_dir = "/root/BS-Watch/sub-discovery"
os.makedirs(output_dir, exist_ok=True)

# Open the file and read domains
try:
    with open(filename, 'r') as file:
        domains = []
        for line in file.readlines():
            domain = line.strip()
            # Check if the line is not empty and not a comment
            if domain and '.' in domain and not domain.startswith('#'):
                domains.append(domain)

    # Display a message confirming the domains are loaded
    print(f"{Fore.YELLOW}{Style.BRIGHT}Domains loaded from {Fore.GREEN}{filename}{Fore.YELLOW}:")
    for domain in domains:
        print(f"{Fore.CYAN}{domain}")

except FileNotFoundError:
    print(f"{Fore.RED}{Style.BRIGHT}Error: The file {Fore.GREEN}{filename}{Fore.RED} was not found.")
    exit(1)

# Function to run shell commands
def run_command_with_bashrc(command, use_bashrc=False):
    if use_bashrc:
        load_bashrc_command = f"bash -l -c '{command}'"
    else:
        load_bashrc_command = command

    process = subprocess.Popen(load_bashrc_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode('utf-8'), err.decode('utf-8')

# crtsh function
def crtsh(query_domain):
    query = f"""
        SELECT
            ci.NAME_VALUE
        FROM
            certificate_and_identities ci
        WHERE
            plainto_tsquery('certwatch', '{query_domain}') @@ identities(ci.CERTIFICATE)
    """
    result = subprocess.run(f"echo \"{query}\" | psql -t -h crt.sh -p 5432 -U guest certwatch", shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    
    if output:
        output = "\n".join(sorted(set(output.splitlines())))
        print(f"{Fore.GREEN}{Style.BRIGHT}Crtsh output for {query_domain} has been saved!")
        with open(os.path.join(output_dir, f"{query_domain}.crtsh"), 'w') as crtsh_file:
            crtsh_file.write(output)
    else:
        print(f"{Fore.RED}Error: No results from crtsh for {query_domain}")

# 1. Run subfinder for each domain (no need for bash -l)
print(f"{Fore.CYAN}{Style.BRIGHT}Starting operation with Subfinder...")
for domain in domains:
    command = f"subfinder -d {domain} -all -silent | sort -u | anew {os.path.join(output_dir, f'{domain}.subfinder')}"
    out, err = run_command_with_bashrc(command, use_bashrc=False)  # No bash -l for subfinder
    if err:
        print(f"{Fore.RED}Error in running subfinder for {domain}: {err}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}Subfinder output for {domain} has been saved!")

# 2. Run crtsh for each domain using the custom function
print(f"{Fore.MAGENTA}{Style.BRIGHT}Starting operation with CRTSH...")
for domain in domains:
    crtsh(domain)  # Use the custom crtsh function

# 3. Combine and resolve subdomains using dnsx
print(f"{Fore.BLUE}{Style.BRIGHT}Starting DNS resolution with dnsx...")

try:
    # Write the list of domains to "main-domain" file in the output directory
    main_domain_file = os.path.join(output_dir, "main-domain")
    with open(main_domain_file, "w") as main_file:
        main_file.write("\n".join(domains))  # This ensures all domains are written

    # Run DNS resolution command using dnsx
    command = f"for d in $(cat {main_domain_file}); do cat {os.path.join(output_dir, '$d.*')} | sort -u | dnsx -t 10 -r ~/resolvers/resolvers.txt -silent | anew {os.path.join(output_dir, '$d.dnsx-resolved')}; done"
    print(f"Running command: {command}")  # Print the command for debugging
    out, err = run_command_with_bashrc(command, use_bashrc=True)

    if err:
        print(f"{Fore.RED}Error during DNS resolution: {err}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}DNS resolution completed and saved for all domains!")

except Exception as e:
    print(f"{Fore.RED}An error occurred during DNS resolution setup: {e}")

# 4. Perform HTTP Service Discovery with httpx using the new command
print(f"{Fore.CYAN}{Style.BRIGHT}Starting HTTP Service Discovery with httpx...")

try:
    # Run HTTP Service Discovery command using httpx
    command = f"""
    for d in $(cat {main_domain_file}); do
        cat {os.path.join(output_dir, "$d.dnsx*")} | sort -u | httpx -silent -follow-host-redirects -title -status-code -cdn -tech-detect \
            -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0" \
            -H "Referer: $d" | anew {os.path.join(output_dir, "$d.httpx")} ;
    done
    """

    # Execute the command
    out, err = run_command_with_bashrc(command, use_bashrc=True)

    if err:
        print(f"{Fore.RED}Error during HTTP Service Discovery: {err}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}HTTP Service Discovery completed and saved for all domains!")

except Exception as e:
    print(f"{Fore.RED}An error occurred during HTTP Service Discovery setup: {e}")


# 5. Delete the main-domain file after the process
try:
    if os.path.exists(main_domain_file):
        os.remove(main_domain_file)
except Exception:
    pass
