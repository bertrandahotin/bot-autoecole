from discord.ext import commands
import os
from flask import Flask
import threading

# Serveur pour Render (ne pas toucher)
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot Auto-Ecole en ligne!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot en ligne: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    await ctx.send("🚀 Création de ton serveur comme sur la capture...")

    # 1. ACCUEIL
    cat1 = await guild.create_category("ACCUEIL")
    await guild.create_text_channel("📖・bienvenue", category=cat1)
    await guild.create_text_channel("📋・règlement", category=cat1)
    await guild.create_text_channel("📢・annonces", category=cat1)

    # 2. COURS THÉORIQUES
    cat2 = await guild.create_category("📚 COURS THÉORIQUES")
    await guild.create_text_channel("📄・code-de-la-route", category=cat2)
    await guild.create_text_channel("🚸・panneaux-de-signalisation", category=cat2)
    await guild.create_text_channel("🚗・règles-de-conduite", category=cat2)
    await guild.create_text_channel("🛡️・sécurité-routière", category=cat2)

    # 3. EXERCICES ET ÉVALUATIONS
    cat3 = await guild.create_category("📝 EXERCICES ET ÉVALUATIONS")
    await guild.create_text_channel("❓・questions-et-réponses", category=cat3)
    await guild.create_text_channel("📝・examens-blancs", category=cat3)
    await guild.create_text_channel("🏆・résultats", category=cat3)

    # 4. COURS EN DIRECT (Vocal)
    cat4 = await guild.create_category("🎙️ COURS EN DIRECT")
    await guild.create_voice_channel("🛰️ Salle de cours 1", category=cat4)
    await guild.create_voice_channel("🛰️ Salle de cours 2", category=cat4)

    await ctx.send("✅ TERMINÉ ! Ton serveur est exactement comme sur ta capture d'écran !")

bot.run(os.environ.get("TOKEN"))
