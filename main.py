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
    
    # On récupère les vrais salons pour pouvoir les taguer
    def get_channel(nom_partiel):
        for ch in guild.text_channels:
            if nom_partiel in ch.name:
                return ch
        return None

    ch_bienvenue = get_channel("bienvenue")
    ch_reglement = get_channel("règlement")
    ch_code = get_channel("code-de-la-route")
    ch_panneaux = get_channel("panneaux")
    ch_questions = get_channel("questions")
    ch_examens = get_channel("examens")

    # Textes avec tags cliquables
    def mention(ch):
        return ch.mention if ch else f"#{ch.name if ch else 'salon'}"

    txt_bienvenue = mention(ch_bienvenue) if ch_bienvenue else "#bienvenue"
    txt_reglement = mention(ch_reglement) if ch_reglement else "#reglement"
    txt_code = mention(ch_code) if ch_code else "#code-de-la-route"
    txt_panneaux = mention(ch_panneaux) if ch_panneaux else "#panneaux"
    txt_questions = mention(ch_questions) if ch_questions else "#questions-et-reponses"
    txt_examens = mention(ch_examens) if ch_examens else "#examens-blancs"

    # Création catégorie privée
    cat_name = "👋 BIENVENUE ELEVES"
    category = discord.utils.get(guild.categories, name=cat_name)
    if not category:
        category = await guild.create_category(cat_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await guild.create_text_channel(f"prive-{member.name}", overwrites=overwrites, category=category)

    message = f"""
Salut {member.mention} 👋 Bienvenue dans l'agence !

Ici le but c'est simple : **on va t'aider à apprendre à conduire et à respecter les règles.**

Je t'ai fait simple, clique directement sur les salons pour y aller :

**Pour commencer :**
👉 {txt_bienvenue} - Présentation de l'agence
👉 {txt_reglement} - Lis bien les règles

**Pour apprendre :**
📚 {txt_code} - Le code de la route
🚸 {txt_panneaux} - Les panneaux
❓ {txt_questions} - Pose tes questions ici
📝 {txt_examens} - Entraîne-toi pour l'examen

Prends le temps de tout lire.

Et écoute, dès que t'as ton permis... là c'est toi le boss 😎
Tu vas faire le show, sortir avec tes potes, conduire où tu veux, même rester tranquille avec les filles dans la voiture... 😏
Mais pas trop de bêtises hein !

Reste actif et on va t'avoir ton permis ensemble ! 🚗💨
"""
    await channel.send(message)
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
    await ctx.send("✅ Serveur créé ! Maintenant les tags sont cliquables.")

bot.run(os.environ.get("TOKEN"))
