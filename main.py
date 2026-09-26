import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# --- Petit serveur web pour Render ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot en ligne !"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
# --- Fin serveur web ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot en ligne: {bot.user}")

bot.run(os.environ.get("TOKEN"))
