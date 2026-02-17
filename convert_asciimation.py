import json
import requests
import sys
import os

# CONFIGURATION
# We prioritize the "fixed" export from the corrected JS snippet
LOCAL_FILES = ["starwars", "starwars.ascii", "starwars.txt"]
REMOTE_URL = "https://raw.githubusercontent.com/nitram509/ascii-telnet-server/master/data/starwars.txt"
OUTPUT_FILE = "recording.jsonl"

FRAME_HEIGHT = 13
FPS_UNIT = 0.067  # 15 frames per second

def load_data():
    """Loads data from local file or falls back to URL."""
    # 1. Try Local Files
    for filename in LOCAL_FILES:
        if os.path.exists(filename):
            print(f"Loading from local file: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                    data = f.read().splitlines()
                    
                    # SANITY CHECK:
                    if len(data) < 20:
                        print(f"WARNING: File '{filename}' has only {len(data)} lines.")
                        if len(data) > 0:
                            print(f"First 100 chars: {data[0][:100]}")
                        print("The file might be corrupted or missing line breaks.")
                        print("Try the corrected JS snippet.")
                        sys.exit(1)
                        
                    return data
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                sys.exit(1)
    
    # 2. Fallback to Remote
    print(f"No local files found ({', '.join(LOCAL_FILES)}).")
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
    
    print(f"DEBUG: Loaded {len(raw_data)} lines of data.")
    
    lines_per_block = FRAME_HEIGHT + 1
    total_blocks = len(raw_data) // lines_per_block
    
    if total_blocks == 0:
        print("Error: 0 frames found. The file format is incorrect.")
        return

    print(f"Converting {total_blocks} frames...")
    
    current_time = 0.0

    with open(OUTPUT_FILE, 'w') as f:
        for i in range(total_blocks):
            base_idx = i * lines_per_block
            
            # 1. Parse Duration (first line of the block)
            try:
                duration_line = raw_data[base_idx].strip()
                if not duration_line.isdigit():
                    # If we hit a non-digit where a duration should be, we might have drifted
                    # or hit the end of valid data.
                    continue
                duration_ticks = int(duration_line)
            except IndexError:
                break

            # 2. Parse Frame (next 13 lines)
            frame_lines = raw_data[base_idx + 1 : base_idx + 1 + FRAME_HEIGHT]
            
            # Handle short frames (if file is truncated)
            if len(frame_lines) < FRAME_HEIGHT:
                frame_lines += [""] * (FRAME_HEIGHT - len(frame_lines))
                
            frame_content = "\r\n".join(frame_lines)
            
            # \x1b[H moves cursor to Home (top-left) without clearing everything
            ansi_data = f"\x1b[H{frame_content}"

            entry = {
                "t": current_time,
                "d": ansi_data.encode('utf-8').hex()
            }
            f.write(json.dumps(entry) + "\n")

            current_time += (duration_ticks * FPS_UNIT)

    print(f"Success! Converted {total_blocks} frames to {OUTPUT_FILE}")

if __name__ == "__main__":
    convert()