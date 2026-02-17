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

# Global cache so we don't re-read file for every user
GLOBAL_FRAMES = []

def load_frames_globally():
    """Loads recording once at startup."""
    global GLOBAL_FRAMES
    print(f"Loading {RECORDING_FILE}...")
    try:
        with open(RECORDING_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    GLOBAL_FRAMES.append(json.loads(line))
        print(f"Loaded {len(GLOBAL_FRAMES)} frames.")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load frames: {e}")
        sys.exit(1)

def filter_telnet_commands(data: bytes) -> str:
    """
    Strips Telnet IAC sequences (e.g., IAC WILL SGA) from the byte stream
    so that protocol bytes (like 0x03 SGA) aren't mistaken for keys (like Ctrl+C).
    """
    clean_bytes = bytearray()
    i = 0
    length = len(data)
    
    while i < length:
        byte = data[i]
        
        if byte == IAC:
            # Check strictly for IAC boundaries to avoid skipping too much
            if i + 1 >= length:
                break # Truncated command, ignore
                
            command = data[i+1]
            
            if command in (WILL, WONT, DO, DONT):
                # These are 3-byte sequences: IAC CMD OPTION
                i += 3
            else:
                # These are 2-byte sequences: IAC CMD (e.g. NOP, SE, etc)
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
        """Main playback loop."""
        if not self.frames:
            return

        # Clear Screen (ANSI)
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
                data = bytes.fromhex(frame['d'])
                self.writer.write(data)
                await self.writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                break

            self.index += 1

            # Loop at end
            if self.index >= len(self.frames):
                 self.index = 0
                 start_time = loop.time()
                 time_offset = 0

    def handle_input(self, text):
        # 1. Handle Arrow Keys
        if '\x1b[C' in text: # Right
            self.skip(5)
            return True
        if '\x1b[D' in text: # Left
            self.skip(-5)
            return True
        
        # 2. Handle Single Char Commands
        for char in text:
            if char == ' ':
                self.playing = not self.playing
            # We strictly check for 'q'. 
            # We rely on filter_telnet_commands to remove protocol 0x03 bytes.
            elif char in ('q', 'Q', '\x03'): 
                return False 
        
        return True

    def skip(self, seconds):
        if not self.frames: return
        
        current_frame_time = self.frames[self.index]['t']
        target_time = current_frame_time + seconds
        
        if target_time < 0: target_time = 0
        if target_time > self.frames[-1]['t']: target_time = 0 
        
        for i, frame in enumerate(self.frames):
            if frame['t'] >= target_time:
                self.index = i
                break

async def handle_telnet_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")
    
    # --- TELNET NEGOTIATION ---
    try:
        # IAC WILL ECHO, IAC WILL SGA, IAC DO SGA
        msg = bytes([IAC, WILL, 0x01, IAC, WILL, 0x03, IAC, DO, 0x03])
        writer.write(msg)
        await writer.drain()
    except Exception as e:
        print(f"Negotiation failed for {addr}: {e}")
        writer.close()
        return

    player = Player(writer)
    play_task = asyncio.create_task(player.play())

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                print(f"Client {addr} disconnected (EOF).")
                break
            
            # --- THE FIX: Filter raw Telnet commands before decoding ---
            text = filter_telnet_commands(data)
            
            if not text:
                continue # It was just protocol noise, ignore

            if not player.handle_input(text):
                print(f"Client {addr} quit via input.")
                break
                
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        play_task.cancel()
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass
        print(f"Connection closed {addr}")

async def main():
    load_frames_globally()
    
    server = await asyncio.start_server(
        handle_telnet_client, '0.0.0.0', PORT
    )
    print("starwars_server.py v0.3")
    print(f"Serving ASCII animation on port {PORT}...")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")