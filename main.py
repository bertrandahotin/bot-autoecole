import discord
from discord.ext import commands
import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Auto-Ecole en ligne!"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========== TES 5 SUJETS ==========
QUESTIONS = {
    1: [
        {"q": "Ce panneau STOP signifie quoi?", "options": ["Stop obligatoire", "Cédez le passage", "Interdit", "Fin de route"], "correct": 0, "explication": "STOP = arrêt total obligatoire, même si y'a personne."},
        {"q": "Panneau triangle avec!?", "options": ["Danger général", "Travaux", "École", "Virage"], "correct": 0, "explication": "C'est danger général, tu ralentis."},
    ],
    2: [
        {"q": "Sans panneau au carrefour, qui passe?", "options": ["Moi", "À droite", "À gauche", "Le plus rapide"], "correct": 1, "explication": "Sans panneau = priorité à droite au Bénin et en France."},
        {"q": "Feu orange tu fais quoi?", "options": ["J'accélère", "Je m'arrête si possible", "Je klaxonne", "Je recule"], "correct": 1, "explication": "Orange = tu t'arrêtes sauf si tu es déjà engagé."},
    ],
    3: [],
    4: [],
    5: [],
}

# ========== LOGIQUE EXAMEN ==========
class QuestionView(discord.ui.View):
    def __init__(self, user, num_sujet, index, score):
        super().__init__(timeout=120)
        self.user = user
        self.num_sujet = num_sujet
        self.index = index
        self.score = score
        q_data = QUESTIONS[num_sujet][index]
        for i, opt in enumerate(q_data["options"]):
            self.add_item(QuestionButton(label=opt[:80], custom_id=str(i), correct=(i==q_data["correct"])))

class QuestionButton(discord.ui.Button):
    def __init__(self, label, custom_id, correct):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)
        self.correct = correct
    async def callback(self, interaction):
        view: QuestionView = self.view
        if interaction.user.id!= view.user.id:
            await interaction.response.send_message("Ce n'est pas ton examen!", ephemeral=True)
            return
        q_data = QUESTIONS[view.num_sujet][view.index]
        nouveau_score = view.score + (1 if self.correct else 0)

        if self.correct:
            embed = discord.Embed(title="✅ VRAI!", description=f"Bien joué!\n\n**Explication:** {q_data['explication']}", color=0x00ff00)
        else:
            bonne = q_data["options"][q_data["correct"]]
            embed = discord.Embed(title="❌ FAUX", description=f"Mauvaise réponse. Bonne réponse: **{bonne}**\n\n**Explication:** {q_data['explication']}", color=0xff0000)

        next_index = view.index + 1
        if next_index < len(QUESTIONS[view.num_sujet]):
            embed.set_footer(text=f"Score: {nouveau_score}/{next_index} | Question {next_index+1}")
            next_view = QuestionView(view.user, view.num_sujet, next_index, nouveau_score)
            q_suivante = QUESTIONS[view.num_sujet][next_index]["q"]
            embed_next = discord.Embed(title=f"Sujet {view.num_sujet} - Question {next_index+1}/{len(QUESTIONS[view.num_sujet])}", description=q_suivante, color=0xf1c40f)
            # On combine explication + prochaine question
            await interaction.response.edit_message(embed=embed, view=None)
            await interaction.followup.send(embed=embed_next, view=next_view, ephemeral=True)
        else:
            embed_fin = discord.Embed(title=f"🏁 Fin Sujet {view.num_sujet}", description=f"Score final: **{nouveau_score}/{len(QUESTIONS[view.num_sujet])}**\n\nRetapes!examen pour refaire.", color=0x3498db)
            await interaction.response.edit_message(embed=embed_fin, view=None)

class SujetModal(discord.ui.Modal, title="Choisis ton sujet"):
    numero = discord.ui.TextInput(label="Numéro du sujet (1 à 5)", placeholder="Ex: tape 2 pour Sujet 2", min_length=1, max_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            num = int(self.numero.value)
        except:
            await interaction.response.send_message("❌ Tape juste un chiffre entre 1 et 5", ephemeral=True)
            return

        if num not in QUESTIONS or len(QUESTIONS[num]) == 0:
            await interaction.response.send_message(f"❌ Le sujet {num} est vide ou n'existe pas. Tape 1 ou 2 pour l'instant.", ephemeral=True)
            return

        q_data = QUESTIONS[num][0]
        embed = discord.Embed(title=f"Sujet {num} - Question 1/{len(QUESTIONS[num])}", description=q_data["q"], color=0xf1c40f)
        view = QuestionView(interaction.user, num, 0, 0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ExamenStartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📝 EXAMEN", style=discord.ButtonStyle.primary, custom_id="start_exam_final")
    async def start(self, interaction, button):
        await interaction.response.send_modal(SujetModal())

@bot.event
async def on_ready():
    print(f"Bot en ligne: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def examen(ctx):
    embed = discord.Embed(title="🚗 EXAMEN CODE", description="Clique sur 📝 EXAMEN et tape le numéro du sujet que tu veux (1 à 5).\n\n**Sujet 1 = Panneaux\nSujet 2 = Priorités** etc...", color=0x2ecc71)
    await ctx.send(embed=embed, view=ExamenStartView())

# Garde ta commande!drive que tu as déjà
@bot.command()
@commands.has_permissions(administrator=True)
async def drive(ctx):
    guild = ctx.guild
    cat_name = "🔒 DRIVE - PRIVE"
    category = discord.utils.get(guild.categories, name=cat_name)
    if not category:
        overwrites_cat = {guild.default_role: discord.PermissionOverwrite(read_messages=False), guild.owner: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        category = await guild.create_category(cat_name, overwrites=overwrites_cat)
    for i in range(1, 4):
        if not discord.utils.get(guild.text_channels, name=f"drive-{i}"): await guild.create_text_channel(f"drive-{i}", category=category)
    await ctx.send(f"✅ Drives OK")

bot.run(os.environ.get("TOKEN"))
