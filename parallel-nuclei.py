import json
import subprocess
import os
import random
from concurrent.futures import ThreadPoolExecutor

def sample_random_lines(folder_path, num_lines=50):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        random_file = random.choice(files)
        with open(os.path.join(folder_path, random_file), 'r') as file:
            lines = file.readlines()
            return random.sample(lines, min(num_lines, len(lines)))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return []

def run_commands(x):
    file_path = './domains'
    sampled_lines = sample_random_lines(file_path)
    
    if not sampled_lines:
        return

    assetfinder_domains = subprocess.run(
        f"echo {x} | assetfinder --subs-only",
        shell=True, capture_output=True, text=True
    ).stdout.splitlines()

    httprobe_results = subprocess.run(
        ["httprobe", "-c", "50"],
        input="\n".join(sampled_lines),
        capture_output=True, text=True
    ).stdout.splitlines()

    nuclei_output = subprocess.run(
        ["nuclei", "-as", "-json"],
        input="\n".join(httprobe_results),
        capture_output=True, text=True
    ).stdout

    try:
        data = json.loads(nuclei_output)
        matched_at_values = [item["matched-at"] for item in data if "matched-at" in item]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing JSON output for {x}: {e}")
        return

    for matched_at in matched_at_values:
        cirrus_output = subprocess.run(
            ["cirrusgo", "salesforce", "-u", matched_at, "--gobj"],
            capture_output=True, text=True
        ).stdout
        # TODO process cirrus output

def update_targets_with_new_domains():
    subprocess.run(['node', 'fetch-bw-api.ts'], check=True)

    last_file = subprocess.run(
        'ls -Art ./initial_bw/*.txt | tail -n 1',
        shell=True, capture_output=True, text=True
    ).stdout.strip()

    if last_file:
        with open(last_file, 'r') as file:
            new_domains = file.read()
        with open('targets.txt', 'a') as file:
            file.write(new_domains)

def main():
    update_targets_with_new_domains()
    
    with open('targets.txt', 'r') as file:
        x_values = file.read().splitlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(run_commands, x_values)

if __name__ == "__main__":
    main()