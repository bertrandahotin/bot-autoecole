import discord
from discord.ext import commands
import os
from flask import Flask
import threading

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

@bot.event
async def on_member_join(member):
    guild = member.guild
    # On cherche ou on crée une catégorie pour les privés
    cat_name = "👋 BIENVENUE ELEVES"
    category = discord.utils.get(guild.categories, name=cat_name)
    if not category:
        category = await guild.create_category(cat_name)

    # Permissions : seulement le nouveau membre + admin peuvent voir
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    # Créer son salon privé
    channel = await guild.create_text_channel(f"prive-{member.name}", overwrites=overwrites, category=category)

    # Message de bienvenue motivant
    message = f"""
Salut {member.mention} 👋 Bienvenue dans l'agence !

Ici le but c'est simple : **on va t'aider à apprendre à conduire et à respecter les règles de la circulation.**

Je t'ai fait simple, pas trop de salons pour pas te perdre :
Tu as juste à aller voir :
📖・bienvenue
📋・règlement
📚 COURS THÉORIQUES pour le code
📝 EXERCICES ET ÉVALUATIONS pour t'entraîner

Prends le temps de tout lire.

Et écoute, dès que t'as ton permis... là c'est toi le boss 😎
Tu vas faire le show, sortir avec tes potes, conduire où tu veux, même rester tranquille avec les filles dans la voiture... 😏

Mais bon, pas trop de bêtises dans la voiture hein ! On veut te voir en vie pour fêter ça !

Reste actif ici, pose tes questions, et on va t'avoir ton permis ensemble ! 🚗💨
"""
    await channel.send(message)
    # On lui envoie aussi en DM au cas où
    try:
        await member.send(message)
    except:
        pass

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    guild = ctx.guild
    await ctx.send("🚀 Création du serveur...")
    cat1 = await guild.create_category("ACCUEIL")
    await guild.create_text_channel("📖・bienvenue", category=cat1)
    await guild.create_text_channel("📋・règlement", category=cat1)
    await guild.create_text_channel("📢・annonces", category=cat1)

    cat2 = await guild.create_category("📚 COURS THÉORIQUES")
    await guild.create_text_channel("📄・code-de-la-route", category=cat2)
    await guild.create_text_channel("🚸・panneaux-de-signalisation", category=cat2)
    await guild.create_text_channel("🚗・règles-de-conduite", category=cat2)
    
    cat3 = await guild.create_category("📝 EXERCICES ET ÉVALUATIONS")
    await guild.create_text_channel("❓・questions-et-réponses", category=cat3)
    await guild.create_text_channel("📝・examens-blancs", category=cat3)

    cat4 = await guild.create_category("🎙️ COURS EN DIRECT")
    await guild.create_voice_channel("🛰️ Salle de cours 1", category=cat4)

    await guild.create_category("👋 BIENVENUE ELEVES")

    await ctx.send("✅ Serveur créé ! Le message de bienvenue privé est activé.")

bot.run(os.environ.get("TOKEN"))
