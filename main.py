import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot en ligne: {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="setup", description="Crée les salons de l'agence")
async def setup(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    cat1 = await guild.create_category("📚 ACCUEIL")
    await guild.create_text_channel("📖・bienvenue", category=cat1)
    await guild.create_text_channel("📋・reglement", category=cat1)
    cat2 = await guild.create_category("📚 COURS THEORIQUES")
    await guild.create_text_channel("📘・code-de-la-route", category=cat2)
    await guild.create_text_channel("🚧・panneaux", category=cat2)
    await guild.create_text_channel("🛡️・securite", category=cat2)
    cat3 = await guild.create_category("📝 EXERCICES")
    await guild.create_text_channel("❓・questions", category=cat3)
    cat4 = await guild.create_category("🎙️ COURS EN DIRECT")
    await guild.create_voice_channel("🔊 Salle de cours 1", category=cat4)
    await interaction.followup.send("✅ Agence créée !")

bot.run(TOKEN)
