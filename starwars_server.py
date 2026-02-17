import asyncio
import json
import sys
import argparse

# CONFIGURATION
VERSION = "v0.32"
RECORDING_FILE = "starwars.jsonl"
PORT = 2323

# TELNET CONSTANTS
IAC  = 0xff
WILL = 0xfb
WONT = 0xfc
DO   = 0xfd
DONT = 0xfe

# Global State
GLOBAL_FRAMES = []
ENABLE_LOGGING = False

def log(msg):
    if ENABLE_LOGGING:
        print(msg)

def load_frames_globally():
    global GLOBAL_FRAMES
    log(f"Loading {RECORDING_FILE}...")
    try:
        with open(RECORDING_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    GLOBAL_FRAMES.append(json.loads(line))
        log(f"Loaded {len(GLOBAL_FRAMES)} frames.")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load frames: {e}")
        sys.exit(1)

def filter_telnet_commands(data: bytes) -> str:
    clean_bytes = bytearray()
    i = 0
    length = len(data)
    while i < length:
        byte = data[i]
        if byte == IAC:
            if i + 1 >= length: break 
            command = data[i+1]
            if command in (WILL, WONT, DO, DONT):
                i += 3
            else:
                i += 2
        else:
            clean_bytes.append(byte)
            i += 1
    return clean_bytes.decode('utf-8', errors='ignore')

class Player:
    def __init__(self, writer):
        self.writer = writer
        self.frames = GLOBAL_FRAMES
        self.playing = True
        self.index = 0
        self.seek_pending = False 

    async def play(self):
        if not self.frames: return

        # Initial Clear
        self.writer.write(b"\x1b[2J\x1b[H")
        
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        
        while self.index < len(self.frames):
            # 1. Handle Seek/Skip
            # If we skipped, we reset the 'start_time' so the math works for the NEW index.
            # New Start Time = Current Real Time - New Frame's Timestamp
            if self.seek_pending:
                start_time = loop.time() - self.frames[self.index]['t']
                self.seek_pending = False

            # 2. Handle Pause
            if not self.playing:
                await asyncio.sleep(0.1)
                # Keep shifting start_time forward while paused so we don't jump when resuming
                start_time = loop.time() - self.frames[self.index]['t']
                continue

            frame = self.frames[self.index]
            target_time = frame['t']
            current_time = loop.time() - start_time

            # 3. Wait for frame time
            if current_time < target_time:
                wait_s = target_time - current_time
                if wait_s > 0:
                    await asyncio.sleep(wait_s)
            
            # 4. Render
            try:
                self.writer.write(bytes.fromhex(frame['d']))
                await self.writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                break

            self.index += 1

            # 5. Loop at end
            if self.index >= len(self.frames):
                 self.index = 0
                 start_time = loop.time() # Reset for loop

    def handle_input(self, text):
        # 1. Handle Arrow Keys
        if '\x1b[C' in text or '\x1bOC' in text: # Right
            self.skip_frames(5)
            return True
        if '\x1b[D' in text or '\x1bOD' in text: # Left
            self.skip_frames(-5)
            return True
        
        # 2. Handle Commands
        for char in text:
            if char == ' ':
                self.playing = not self.playing
                log(f"Paused: {not self.playing}")
            elif char in ('q', 'Q', '\x03'): 
                return False 
        return True

    def skip_frames(self, count):
        if not self.frames: return
        
        old_index = self.index
        new_index = self.index + count
        
        # Clamp
        if new_index < 0: new_index = 0
        if new_index >= len(self.frames): new_index = 0 # Loop or stop
        
        self.index = new_index
        self.seek_pending = True # Signal the loop to reset the clock
        
        log(f"Skipped {count} frames (Index {old_index} -> {self.index})")

async def handle_telnet_client(reader, writer):
    addr = writer.get_extra_info('peername')
    log(f"New connection from {addr}")
    
    try:
        msg = bytes([IAC, WILL, 0x01, IAC, WILL, 0x03, IAC, DO, 0x03])
        writer.write(msg)
        await writer.drain()
    except:
        return

    player = Player(writer)
    task = asyncio.create_task(player.play())

    try:
        while True:
            data = await reader.read(1024)
            if not data: break
            
            text = filter_telnet_commands(data)
            if not text: continue

            if not player.handle_input(text):
                break
    except Exception as e:
        log(f"Error {addr}: {e}")
    finally:
        task.cancel()
        try: writer.close(); await writer.wait_closed()
        except: pass
        log(f"Closed {addr}")

async def main():
    parser = argparse.ArgumentParser(description=f'Starwars Telnet Server {VERSION}')
    parser.add_argument('--log', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    global ENABLE_LOGGING
    ENABLE_LOGGING = args.log

    print(f"starwars_server.py {VERSION}")
    if ENABLE_LOGGING:
        print("Logging Enabled")
    else:
        print("Logging Disabled (use --log to enable)")

    load_frames_globally()
    
    server = await asyncio.start_server(handle_telnet_client, '0.0.0.0', PORT)
    print(f"Serving on {PORT}...")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass