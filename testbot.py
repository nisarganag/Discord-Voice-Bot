import discord
from discord.ext import commands
import asyncio
import wave
import os
from discord.sinks import WaveSink
from pydub import AudioSegment
import io

def read_token():
    try:
        with open("token.txt", "r") as file:
            # Read the first line of the file and extract the token
            token_line = file.readline().strip()
            token = token_line.split('=')[1].strip().strip('"')
            return token
    except Exception as e:
        print(f"Error reading token: {e}")
        return None

TOKEN = read_token()

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Enable voice state intent
bot = commands.Bot(command_prefix="!", intents=intents)

# Directory for recordings
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Join voice channel command
@bot.command()
async def come(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await ctx.send(f"Joined {channel.name}")
    else:
        await ctx.send("You need to join a voice channel first!")

# Record audio command
@bot.command()
async def listen(ctx, duration: int = 10):
    if ctx.voice_client:
        vc = ctx.voice_client
        filename = f"combined_recording_{ctx.message.id}.wav"
        filepath = os.path.join(RECORDINGS_DIR, filename)
        
        # Create a sink for the recording
        sink = WaveSink()
        
        # Define an async callback function
        async def on_recording_finished(sink, *args):
            print("Recording finished")
            # Check if audio data is present
            if not sink.audio_data:
                print("No audio data captured.")
                await ctx.send("No audio data captured.")
                return
            
            # Initialize an empty AudioSegment for mixing
            combined_audio = AudioSegment.silent(duration=0)
            
            # Mix all user audio streams
            for user_id, audio in sink.audio_data.items():
                print(f"Processing audio for user {user_id}")
                # Convert the audio data to an AudioSegment
                try:
                    user_audio = AudioSegment.from_file(io.BytesIO(audio.file.getvalue()), format="wav")
                    combined_audio = combined_audio.overlay(user_audio)
                except Exception as e:
                    print(f"Error processing audio for user {user_id}: {e}")
            
            # Export the combined audio to a file
            combined_audio.export(filepath, format="wav")
            await ctx.send(f"Recording saved as {filename}")
        
        # Start recording
        vc.start_recording(
            sink,
            on_recording_finished,  # Use the async function as the callback
            ctx.channel
        )
        
        await ctx.send(f"Recording for {duration} seconds...")
        await asyncio.sleep(duration)
        
        # Stop recording
        vc.stop_recording()
    else:
        await ctx.send("The bot is not connected to a voice channel!")

# Leave voice channel command
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("The bot is not in a voice channel!")

# Run the bot
bot.run(TOKEN)