import asyncio
import json
import sys

# CONFIGURATION
RECORDING_FILE = "recording.jsonl"
PORT = 2323

class Player:
    def __init__(self, writer):
        self.writer = writer
        self.frames = []
        self.playing = True
        self.index = 0
        self.load_frames()

    def load_frames(self):
        """Loads the entire recording into memory."""
        try:
            with open(RECORDING_FILE, 'r') as f:
                for line in f:
                    self.frames.append(json.loads(line))
        except FileNotFoundError:
            self.writer.write(b"Error: recording.jsonl not found.\r\n")
            self.playing = False

    async def play(self):
        """Main playback loop."""
        if not self.frames:
            return

        # Ensure terminal is reset for the client immediately
        self.writer.write(b"\x1b[2J\x1b[H")
        
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        time_offset = 0 
        
        while self.index < len(self.frames):
            if not self.playing:
                await asyncio.sleep(0.1)
                # Reset start time so we don't jump ahead when resuming
                # current_time - new_start = frame_time  =>  new_start = current_time - frame_time
                start_time = loop.time() - (self.frames[self.index]['t'] - time_offset)
                continue

            frame = self.frames[self.index]
            target_time = frame['t'] - time_offset
            current_time = loop.time() - start_time

            if current_time < target_time:
                # Wait until it's time for the next frame
                await asyncio.sleep(target_time - current_time)
            
            # Send data
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

    def handle_input(self, char):
        """Controls logic."""
        if char == ' ':
            self.playing = not self.playing
        elif char == 'q' or char == '\x03': # q or Ctrl+C
            return False 
        elif '\x1b[C' in char: # Right Arrow
            self.skip(5)
        elif '\x1b[D' in char: # Left Arrow
            self.skip(-5)
        return True

    def skip(self, seconds):
        """Skips forward or backward by N seconds."""
        if not self.frames: return
        
        current_frame_time = self.frames[self.index]['t']
        target_time = current_frame_time + seconds
        
        # Clamp target time
        if target_time < 0: target_time = 0
        if target_time > self.frames[-1]['t']: target_time = 0 # Loop if skip past end
        
        # Find new index
        for i, frame in enumerate(self.frames):
            if frame['t'] >= target_time:
                self.index = i
                break

async def handle_telnet_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr}")
    
    player = Player(writer)
    play_task = asyncio.create_task(player.play())

    try:
        while True:
            # Read input (keys)
            data = await reader.read(1024)
            if not data:
                break
            
            char = data.decode('utf-8', errors='ignore')
            
            if not player.handle_input(char):
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
    server = await asyncio.start_server(
        handle_telnet_client, '0.0.0.0', PORT
    )
    print(f"Serving ASCII animation on port {PORT}...")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")