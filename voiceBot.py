import discord
from discord.ext import commands
import speech_recognition as sr
import asyncio
import wave
import os
from discord.sinks import WaveSink
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydub import AudioSegment
import io
import pyttsx3
from gtts import gTTS

engine = pyttsx3.init()

# Initialize the bot
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

TOKEN = read_token()  # Replace with your actual bot token
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Enable voice state intent
intents.messages = True 
bot = commands.Bot(command_prefix="!", intents=intents)

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)
# Function to listen for voice commands
async def listen_for_commands(ctx):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        while True:
            print("Listening for commands...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"Recognized command: {command}")
                # Check for specific commands
                if "assemble" in command.lower():
                    if ctx.author.voice:  # Check if the user is in a voice channel
                        channel = ctx.author.voice.channel
                        if ctx.voice_client is None:  # Check if the bot is not already in a voice channel
                            await channel.connect()
                            await ctx.send("Agaya mai gays.")
                            print("Bot joined the voice channel.")
                        else:
                            print("Bot is already in a voice channel.")
                    else:
                        print("User is not in a voice channel.")
                elif "sayonara" in command.lower():
                    if ctx.voice_client is not None:  # Check if the bot is in a voice channel
                        print("Attempting to leave the voice channel...")
                        await ctx.voice_client.disconnect()
                        await ctx.send("Thik hai bhai bhaga diya bhadwa.")
                    else:
                        print("Bot is not in a voice channel.")
                        
                elif "record" in command.lower():
                    parts = command.split()
                    if len(parts) > 1:
                        duration_str = parts[1]
                        try:
                            duration = int(duration_str)
                            await sunn(ctx, duration)
                        except ValueError:
                            print("Invalid duration specified.")
                    else:
                        print("Duration not specified.")
                else:
                    if ctx.voice_client:
                        await speak(ctx, command)  # Speak the command dynamically
                    else:
                        await ctx.send("You need to be in a voice channel for me to speak.")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
# Join voice channel command (optional, can be removed if not needed)
@bot.command()
async def aaja(ctx):
    print("Command aaja triggered.")  # Debugging line
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await ctx.send("Agaya mai gays.")
        
        # Start listening for commands in a separate task
        bot.loop.create_task(listen_for_commands(ctx))
    else:
        await ctx.send("Saale pehle khud to vc join kar le.")
        
@bot.command()
async def speak(ctx, text):
    """Make the bot speak the given text in the voice channel."""
    try:
        tts = gTTS(text=text, lang='ru')
        tts.save("command.mp3")
        if ctx.voice_client is None:  # Check if bot is not connected
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You need to be in a voice channel for me to speak.")
                return
        vc = ctx.voice_client
        if not vc.is_playing():  # Ensure no audio is playing
            vc.play(discord.FFmpegPCMAudio("command.mp3"), after=lambda e: print(f"Finished speaking: {e}"))
            while vc.is_playing():
                await asyncio.sleep(1)  # Wait for the audio to finish playing
    except Exception as e:
        print(f"Error in speak function: {e}")
# Leave voice channel command (optional, can be removed if not needed)
@bot.command()
async def bhag(ctx):
    print("Command bhag triggered.")  # Debugging line
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Thik hai bhai bhaga diya bhadwa.")
    else:
        await ctx.send("Saale mai hu hi nahi bhagu kaise.")
        
@bot.command()
async def sunn(ctx, duration: int = 10):
    print(f"Recording for {duration} seconds.")  # Debugging line
    if ctx.voice_client:
        vc = ctx.voice_client
        sink = WaveSink()  # Create a WaveSink to capture audio
        async def on_recording_finished(sink, *args):
            print("Recording finished.")
            if not sink.audio_data:
                # await ctx.send("No audio data captured.")
                print("No audio data captured.")
                return
            for user_id, audio in sink.audio_data.items():
                user_filename = f"recording_{ctx.message.id}_user_{user_id}.wav"
                user_filepath = os.path.join(RECORDINGS_DIR, user_filename)
                try:
                    with wave.open(user_filepath, "wb") as wf:
                        wf.setnchannels(2)  # Stereo
                        wf.setsampwidth(2)  # Bytes per sample
                        wf.setframerate(48000)  # Sample rate
                        wf.writeframes(audio.file.getvalue())
                    # await ctx.send(f"Saved recording for user {user_id} as {user_filename}")
                    print(f"Saved recording for user {user_id} as {user_filename}")
                except Exception as e:
                    # await ctx.send(f"Error saving recording for user {user_id}: {e}")
                    print(f"Error saving recording for user {user_id}: {e}")
        # Start recording
        vc.start_recording(sink, on_recording_finished, ctx.channel)
        # await ctx.send(f"Recording for {duration} seconds...")
        await asyncio.sleep(duration)
        vc.stop_recording()
        print("Recording stopped.")
    else:
        await ctx.send("Mai nahi hu bhai vc me.")
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
# Run the bot
bot.run(TOKEN)
