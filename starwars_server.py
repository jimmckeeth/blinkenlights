import asyncio
import json
import sys

# CONFIGURATION
RECORDING_FILE = "starwars.jsonl"
PORT = 2323

# TELNET CONSTANTS
IAC  = 0xff
WILL = 0xfb
WONT = 0xfc
DO   = 0xfd
DONT = 0xfe

GLOBAL_FRAMES = []

def load_frames_globally():
    global GLOBAL_FRAMES
    print(f"Loading {RECORDING_FILE}...")
    try:
        with open(RECORDING_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    GLOBAL_FRAMES.append(json.loads(line))
        print(f"Loaded {len(GLOBAL_FRAMES)} frames.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
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

    async def play(self):
        if not self.frames: return

        # Initial Clear
        self.writer.write(b"\x1b[2J\x1b[H")
        
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        time_offset = 0 
        
        while self.index < len(self.frames):
            if not self.playing:
                await asyncio.sleep(0.1)
                start_time = loop.time() - (self.frames[self.index]['t'] - time_offset)
                continue

            frame = self.frames[self.index]
            target_time = frame['t'] - time_offset
            current_time = loop.time() - start_time

            if current_time < target_time:
                await asyncio.sleep(target_time - current_time)
            
            try:
                self.writer.write(bytes.fromhex(frame['d']))
                await self.writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                break

            self.index += 1

            if self.index >= len(self.frames):
                 self.index = 0
                 start_time = loop.time()
                 time_offset = 0

    def handle_input(self, text):
        # Debug print to see what raw codes your terminal sends
        # print(f"DEBUG INPUT: {repr(text)}") 

        # 1. Handle Arrow Keys (Support both [ and O styles)
        if '\x1b[C' in text or '\x1bOC' in text: # Right
            self.skip(10) # Increased to 10s to make it more obvious
            return True
        if '\x1b[D' in text or '\x1bOD' in text: # Left
            self.skip(-10)
            return True
        
        # 2. Handle Commands
        for char in text:
            if char == ' ':
                self.playing = not self.playing
            elif char in ('q', 'Q', '\x03'): 
                return False 
        return True

    def skip(self, seconds):
        if not self.frames: return
        current = self.frames[self.index]['t']
        target = current + seconds
        
        # Clamp
        if target < 0: target = 0
        if target > self.frames[-1]['t']: target = 0 
        
        # Search
        for i, frame in enumerate(self.frames):
            if frame['t'] >= target:
                self.index = i
                break
        
        # Visual feedback for skip
        try:
            msg = f"\x1b[HSkipping to {int(target)}s..."
            self.writer.write(msg.encode('utf-8'))
        except:
            pass

async def handle_telnet_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")
    
    # Negotiate Character Mode
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
        print(f"Error {addr}: {e}")
    finally:
        task.cancel()
        try: writer.close(); await writer.wait_closed()
        except: pass
        print(f"Closed {addr}")

async def main():
    load_frames_globally()
    server = await asyncio.start_server(handle_telnet_client, '0.0.0.0', PORT)
    print('v0.4')
    print(f"Serving on {PORT}...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass