import discord
from discord.ext import commands
import asyncio
import wave
import os
from discord.sinks import WaveSink
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydub import AudioSegment
import io

TOKEN = "MTMyNDY1MzIzOTYxNzk4MjUxNA.Gh8sGo.T_nEevvP_5yvKlnrMLpPLLRDJYHj6NiR3_KjQ8"
# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Enable voice state intent
intents.messages = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# Directory for recordings
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Load GPT-J model
# model_id = "EleutherAI/gpt-j-6B"  # GPT-J model ID
# tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForCausalLM.from_pretrained(model_id)

# # Move model to GPU if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)

# # Function to generate a response using the GPT-J model
# def generate_response(prompt):
#     print(f"Generating response for prompt: {prompt}")
#     try:
#         # Create a structured prompt for the model
#         enhanced_prompt = (
#             "You are a helpful assistant. "
#             f"Human: {prompt}\n"
#             "Assistant: "
#         )
        
#         # Tokenization
#         inputs = tokenizer(enhanced_prompt, return_tensors="pt").to(device)
        
#         # Generate with adjusted parameters for more natural conversation
#         with torch.no_grad():
#             response = model.generate(
#                 inputs['input_ids'],
#                 max_length=150,          # Allow for more detailed responses
#                 min_length=20,           # Ensure meaningful responses
#                 num_return_sequences=1,
#                 temperature=0.7,         # Slightly higher for more creative responses
#                 do_sample=True,
#                 top_p=0.9,               # More diverse sampling
#                 top_k=50,                # More focused vocabulary
#                 no_repeat_ngram_size=3,  # Prevent repetition
#                 pad_token_id=tokenizer.pad_token_id,
#                 eos_token_id=tokenizer.eos_token_id,
#                 repetition_penalty=1.2,   # Moderate repetition penalty
#             )
        
#         # Decode and clean up the response
#         generated_text = tokenizer.decode(response[0], skip_special_tokens=True)
        
#         # Extract just the assistant's response
#         if "Assistant:" in generated_text:
#             generated_text = generated_text.split("Assistant:")[-1].strip()
        
#         # Clean up the text
#         generated_text = generated_text.replace("Human:", "").replace(prompt, "")
#         generated_text = ' '.join(generated_text.split())  # Normalize whitespace
        
#         # Ensure proper ending
#         if not any(generated_text.endswith(char) for char in ['.', '!', '?']):
#             generated_text += '.'
            
#         return generated_text
        
#     except Exception as e:
#         print(f"Error during generation: {str(e)}")
#         return f"Error during generation: {str(e)}"
# Join voice channel command
@bot.command()
async def aaja(ctx):
    print("Command aaja triggered.")  # Debugging line
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        await ctx.send(f"Agaya mai gays.")
        await sunn(ctx, duration=60)
    else:
        await ctx.send("Saale pehle khud to vc join kar le.")

# Record audio command
@bot.command()
async def sunn(ctx, duration: int = 10):
    print(f"Recording for {duration} seconds.")  # Debugging line
    if ctx.voice_client:
        vc = ctx.voice_client
        sink = WaveSink()  # Create a WaveSink to capture audio

        async def on_recording_finished(sink, *args):
            if not sink.audio_data:
                # await ctx.send("No audio data captured.")
                return

            for user_id, audio in sink.audio_data.items():
                user_filename = f"recording_{ctx.message.id}_user_{user_id}.wav"
                user_filepath = os.path.join(RECORDINGS_DIR, user_filename)

                with wave.open(user_filepath, "wb") as wf:
                    wf.setnchannels(2)  # Stereo
                    wf.setsampwidth(2)  # Bytes per sample
                    wf.setframerate(48000)  # Sample rate
                    wf.writeframes(audio.file.getvalue())

                # await ctx.send(f"Saved recording for user {user_id} as {user_filename}")
                print(f"Saved recording for user {user_id} as {user_filename}")

        # Start recording
        vc.start_recording(sink, on_recording_finished, ctx.channel)
        # await ctx.send(f"Recording for {duration} seconds...")
        await asyncio.sleep(duration)
        vc.stop_recording()
    else:
        await ctx.send("Mai nahi hu bhai vc me.")

# Leave voice channel command
@bot.command()
async def bhag(ctx):
    print("Command bhag triggered.")  # Debugging line
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Thik hai bhai bhaga diya bhadwa.")
    else:
        await ctx.send("Saale mai hu hi nahi bhagu kaise.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Respond when the bot is mentioned
    if bot.user in message.mentions:
        # Remove the mention from the message content
        content_without_mention = message.content.replace(f"<@{bot.user.id}>", "").strip()
        await message.channel.send(f"yes {content_without_mention}")

    await bot.process_commands(message)
    
# @bot.command()
# async def bata(ctx, *, question: str):
#     print(f"Received question: {question}")  # Debugging line
#     try:
#         prompt = f"You are a helpful assistant. {question}"
#         print(f"Prompt for model: {prompt}")  # Debugging line
#         answer = generate_response(prompt)
#         print(f"Generated answer: {answer}")  # Debugging line
#         await ctx.send(answer)
#     except Exception as e:
#         print(f"Error occurred: {e}")  # Debugging line
#         await ctx.send(f"An error occurred: {e}")

# Start the bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Failed to start the bot: {e}")
