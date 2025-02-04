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
import aiohttp  # Added for Ollama API

engine = pyttsx3.init()

# Initialize the bot
def read_token():
    try:
        with open("token.txt", "r") as file:
            token_line = file.readline().strip()
            token = token_line.split('=')[1].strip().strip('"')
            return token
    except Exception as e:
        print(f"Error reading token: {e}")
        return None

TOKEN = read_token()
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.messages = True 
bot = commands.Bot(command_prefix="!", intents=intents)

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# New Answer Command
@bot.command(name='answer')
async def answer(ctx, *, query: str):
    """Get an AI-generated response using Ollama"""
    try:
        async with ctx.typing():
            model_name = "hf.co/TheBloke/deepseek-llm-7B-chat-GGUF:Q4_K_M"
            url = "http://localhost:11434/api/generate"
            
            payload = {
                "model": model_name,
                "prompt": query,
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 500
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data['response'].strip()
                        if len(answer) > 2000:
                            for chunk in [answer[i:i+2000] for i in range(0, len(answer), 2000)]:
                                await ctx.send(chunk)
                        else:
                            await ctx.send(answer)
                    else:
                        await ctx.send(f"Error: Received status code {response.status}")
    
    except aiohttp.ClientConnectorError:
        await ctx.send("Couldn't connect to Ollama. Is it running? (http://localhost:11434)")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name='code')
async def code_command(ctx, *, query: str):
    """Get coding help using Deepseek Coder"""
    try:
        async with ctx.typing():
            model_name = "deepseek-coder:6.7b-instruct-q4_K_M"  # Different model
            url = "http://localhost:11434/api/generate"
            
            payload = {
                "model": model_name,
                "prompt": f"You are an expert programmer. Help with: {query}",
                "stream": False,
                "temperature": 0.5,  # Lower temp for code generation
                "max_tokens": 1000   # Allow longer responses for code
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data['response'].strip()
                        # Format code blocks with markdown
                        formatted_response = f"```\n{answer}\n```"
                        if len(formatted_response) > 2000:
                            for chunk in [formatted_response[i:i+2000] for i in range(0, len(formatted_response), 2000)]:
                                await ctx.send(chunk)
                        else:
                            await ctx.send(formatted_response)
                    else:
                        await ctx.send(f"Error: Received status code {response.status}")
    
    except aiohttp.ClientConnectorError:
        await ctx.send("Couldn't connect to Ollama. Is it running? (http://localhost:11434)")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def aaja(ctx):
    print("Command aaja triggered.")
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await ctx.send("Agaya mai gays.")
    else:
        await ctx.send("Saale pehle khud to vc join kar le.")
        

@bot.command()
async def bhag(ctx):
    print("Command bhag triggered.")
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Thik hai bhai bhaga diya bhadwa.")
    else:
        await ctx.send("Saale mai hu hi nahi bhagu kaise.")
        
@bot.command()
async def sunn(ctx, duration: int = 10):
    print(f"Recording for {duration} seconds.")
    if ctx.voice_client:
        vc = ctx.voice_client
        sink = WaveSink()
        async def on_recording_finished(sink, *args):
            print("Recording finished.")
            if not sink.audio_data:
                print("No audio data captured.")
                return
            for user_id, audio in sink.audio_data.items():
                user_filename = f"recording_{ctx.message.id}_user_{user_id}.wav"
                user_filepath = os.path.join(RECORDINGS_DIR, user_filename)
                try:
                    with wave.open(user_filepath, "wb") as wf:
                        wf.setnchannels(2)
                        wf.setsampwidth(2)
                        wf.setframerate(48000)
                        wf.writeframes(audio.file.getvalue())
                    print(f"Saved recording for user {user_id} as {user_filename}")
                except Exception as e:
                    print(f"Error saving recording for user {user_id}: {e}")
        vc.start_recording(sink, on_recording_finished, ctx.channel)
        await asyncio.sleep(duration)
        vc.stop_recording()
        print("Recording stopped.")
    else:
        await ctx.send("Mai nahi hu bhai vc me.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(TOKEN)