import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

import os
import random

def sample_random_lines(folder_path, num_lines=50):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        random_file = random.choice(files)
        with open(os.path.join(folder_path, random_file), 'r') as file:
            lines = file.readlines()
            sampled_lines = random.sample(lines, min(num_lines, len(lines)))
        with open('dom50.txt', 'w') as outfile:
            for line in sampled_lines:
                outfile.write(line)
    except FileNotFoundError:
        return ["File not found."]

def run_commands(x):
    
    file_path = './domains'
    dom = sample_random_lines(file_path)
    
    commands = [
        f"echo {x} | assetfinder --subs-only | anew domains50/{x}",
        f"cam dom50.txt | httprobe -c 50 | anew hosts/h_{x}",
        f"cat hosts/* | nuclei -as -json-export out/o_{x}.json" #| anew c_out/c_o_{x}.json"
    ]
    #hosts/h_{x}
    
    for cmd in commands:
        subprocess.run(cmd, shell=True)

    try:
        with open(f"out/o_{x}.json", 'r') as json_file:
            data = json.load(json_file)
            matched_at_values = [item["matched-at"] for item in data if "matched-at" in item]
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing JSON file for {x}: {e}")
        return

    for matched_at in matched_at_values:
        cirrus_cmd = f"cirrusgo salesforce -u {matched_at} --gobj | anew cirrus-out/{matched_at}-vuln"
        subprocess.run(cirrus_cmd, shell=True)
        
def update_targets_with_new_domains():
    subprocess.run(['node', 'fetch-bw-api.ts'])

    subprocess.run('ls -Art ./initial_bw/*.txt | tail -n 1 | xargs cat | anew targets.txt', shell=True)

def main():
    update_targets_with_new_domains()
    
    with open('targets.txt', 'r') as file:
        x_values = file.read().splitlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(run_commands, x_values)

if __name__ == "__main__":
    main()
