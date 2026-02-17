import json
import requests
import sys
import os

# CONFIGURATION
LOCAL_FILES = ["starwars_fixed.txt", "starwars_latest.txt", "starwars.txt"]
REMOTE_URL = "https://raw.githubusercontent.com/nitram509/ascii-telnet-server/master/data/starwars.txt"
OUTPUT_FILE = "starwars.jsonl"

FRAME_HEIGHT = 13
FPS_UNIT = 0.067 

def load_data():
    for filename in LOCAL_FILES:
        if os.path.exists(filename):
            print(f"Loading from local file: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                    data = f.read().splitlines()
                    if len(data) < 20:
                        print("WARNING: File seems too short/corrupt.")
                        sys.exit(1)
                    return data
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                sys.exit(1)
    
    print(f"Falling back to remote: {REMOTE_URL}")
    try:
        r = requests.get(REMOTE_URL)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        print(f"Error fetching remote: {e}")
        sys.exit(1)

def convert():
    raw_data = load_data()
    lines_per_block = FRAME_HEIGHT + 1
    total_blocks = len(raw_data) // lines_per_block
    
    current_time = 0.0

    print(f"Converting {total_blocks} frames...")

    with open(OUTPUT_FILE, 'w') as f:
        for i in range(total_blocks):
            base_idx = i * lines_per_block
            
            try:
                duration_line = raw_data[base_idx].strip()
                if not duration_line.isdigit(): continue
                duration_ticks = int(duration_line)
            except IndexError:
                break

            frame_lines = raw_data[base_idx + 1 : base_idx + 1 + FRAME_HEIGHT]
            
            if len(frame_lines) < FRAME_HEIGHT:
                frame_lines += [""] * (FRAME_HEIGHT - len(frame_lines))
            
            # --- THE FIX ---
            # We append \x1b[K (Clear Line) to every single line.
            # This ensures that if the new line is shorter than the old one,
            # the remaining characters from the old line are erased.
            frame_content = "\x1b[K\r\n".join(frame_lines) + "\x1b[K"
            
            ansi_data = f"\x1b[H{frame_content}"

            entry = {
                "t": current_time,
                "d": ansi_data.encode('utf-8').hex()
            }
            f.write(json.dumps(entry) + "\n")

            current_time += (duration_ticks * FPS_UNIT)

    print(f"Success! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    convert()