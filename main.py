import discord
from discord.ext import commands
import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Auto-Ecole Multi-Choice OK"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== TON BAREME DE LA PHOTO =====
BAREME = {
    1: [3,5,14,17,27,36,46,56,64,84,95,157,206,218,258,274,288,310,329,331],
    2: [8,19,26,41,51,68,89,108,140,208,113,226,240,289,299,308,307,353,343,358],
    3: [2,9,22,31,50,58,69,85,90,99,109,118,141,150,164,209,227,292,305,330],
    4: [4,13,23,34,42,53,59,87,110,114,128,145,159,174,182,220,229,236,254,291],
    5: [6,16,30,40,52,65,91,98,111,124,143,165,171,184,225,237,256,290,309,318],
    6: [7,24,33,48,60,79,104,119,142,166,175,188,201,207,228,241,253,260,272,283],
    7: [55,71,86,100,120,131,19,18,32,37,190,203,234,252,287,230,146,161,179,306],
    8: [11,28,47,61,70,88,103,123,144,167,173,186,196,211,221,231,255,269,292,293],
    9: [12,21,38,57,74,83,94,102,122,136,147,156,169,185,198,214,230,242,251,263],
    10: [15,29,43,63,80,96,121,133,148,160,172,194,215,233,248,259,267,279,295,311],
}

# ===== BANQUE EXEMPLE - REMPLACE AVEC TES VRAIES QUESTIONS =====
BANQUE = {
    3: {"q": "Q03 - Cette signalisation indique?", "options": ["A) Virages", "B) Succession de virages", "C) Route sinueuse", "D) Chaussée glissante"], "rep": ["A","B"], "exp": "Panneau succession de virages, il faut ralentir."},
    5: {"q": "Q05 - Vous devez?", "options": ["A) Rouler vite", "B) Ralentir", "C) Klaxonner", "D) Freiner"], "rep": ["B"], "exp": "Lieu-dit = on ralentit."},
}

# ===== VUE MULTI-CHOIX AVEC A,B,C,D =====
class MultiChoiceView(discord.ui.View):
    def __init__(self, user, num_sujet, q_index, score):
        super().__init__(timeout=300)
        self.user = user
        self.num_sujet = num_sujet
        self.q_index = q_index
        self.score = score
        self.selection = set() # ce que l'élève a coché

        self.num_banque = BAREME[num_sujet][q_index]
        self.data = BANQUE.get(self.num_banque, {"q": f"Question {self.num_banque} en cours...", "options": ["A)...", "B)...", "C)...", "D)..."], "rep": ["A"], "exp": ""})

        # Crée les boutons A,B,C,D dynamiquement selon le nombre d'options
        for opt_text in self.data["options"]:
            lettre = opt_text[0].upper() # A, B, C, D
            self.add_item(BoutonToggle(lettre, opt_text[:80]))

        self.add_item(BoutonValider())

    def get_embed(self, couleur=0xf1c40f):
        sel_txt = ", ".join(sorted(self.selection)) if self.selection else "Aucune"
        embed = discord.Embed(
            title=f"Sujet {self.num_sujet} - Question {self.q_index+1}/20 (Banque N°{self.num_banque})",
            description=f"{self.data['q']}\n\n**Coché:** {sel_txt}",
            color=couleur
        )
        embed.set_footer(text=f"Score: {self.score}/{self.q_index} | Coche A,B,C,D puis clique VALIDER")
        return embed

class BoutonToggle(discord.ui.Button):
    def __init__(self, lettre, label):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"toggle_{lettre}")
        self.lettre = lettre
    async def callback(self, interaction):
        view: MultiChoiceView = self.view
        if interaction.user.id!= view.user.id:
            await interaction.response.send_message("Pas ton examen!", ephemeral=True)
            return
        if self.lettre in view.selection:
            view.selection.remove(self.lettre)
            self.style = discord.ButtonStyle.secondary
        else:
            view.selection.add(self.lettre)
            self.style = discord.ButtonStyle.primary

        await interaction.response.edit_message(embed=view.get_embed(), view=view)

class BoutonValider(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✅ VALIDER", style=discord.ButtonStyle.success, row=2)
    async def callback(self, interaction):
        view: MultiChoiceView = self.view
        if interaction.user.id!= view.user.id:
            await interaction.response.send_message("Pas ton examen!", ephemeral=True)
            return
        if not view.selection:
            await interaction.response.send_message("Coche au moins une réponse!", ephemeral=True)
            return

        bonne = set([r.upper() for r in view.data["rep"]])
        choisie = set([s.upper() for s in view.selection])

        # LOGIQUE QUE TU VEUX: exacte correspondance
        est_vrai = (choisie == bonne)

        if est_vrai:
            embed = discord.Embed(
                title=f"✅ VRAI! (Q{view.num_banque})",
                description=f"Bravo! Bonne réponse: **{', '.join(sorted(bonne))}**\n\n{view.data['exp']}",
                color=0x00ff00
            )
            nouveau_score = view.score + 1
        else:
            embed = discord.Embed(
                title=f"❌ FAUX - Question en ROUGE (Q{view.num_banque})",
                description=f"Tu as coché: **{', '.join(sorted(choisie))}**\nBonne réponse: **{', '.join(sorted(bonne))}**\n\n{view.data['exp']}",
                color=0xff0000 # ROUGE comme tu veux
            )
            nouveau_score = view.score

        # Question suivante
        next_index = view.q_index + 1
        if next_index < 20:
            next_view = MultiChoiceView(view.user, view.num_sujet, next_index, nouveau_score)
            await interaction.response.edit_message(embed=embed, view=None)
            await interaction.followup.send(embed=next_view.get_embed(), view=next_view, ephemeral=True)
        else:
            embed_fin = discord.Embed(title=f"🏁 Fin Sujet {view.num_sujet} - Score {nouveau_score}/20", description=f"Barème: {BAREME[view.num_sujet]}", color=0x3498db)
            await interaction.response.edit_message(embed=embed, view=None)
            await interaction.followup.send(embed=embed_fin, ephemeral=True)

class SujetModal(discord.ui.Modal, title="Choisis le sujet 1-10"):
    numero = discord.ui.TextInput(label="Numéro du sujet (1 à 10)", placeholder="Ex: 1", min_length=1, max_length=2)
    async def on_submit(self, interaction):
        try:
            num = int(self.numero.value)
            if num not in BAREME: raise ValueError
        except:
            await interaction.response.send_message("❌ Tape 1 à 10", ephemeral=True)
            return
        view = MultiChoiceView(interaction.user, num, 0, 0)
        await interaction.response.send_message(embed=view.get_embed(), view=view, ephemeral=True)

class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📝 EXAMEN", style=discord.ButtonStyle.success, custom_id="examen_multichoice")
    async def start(self, interaction, button):
        await interaction.response.send_modal(SujetModal())

@bot.event
async def on_ready():
    print(f"Bot prêt: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def examen(ctx):
    embed = discord.Embed(title="🚗 EXAMEN BENIN - 10 Sujets", description="1. Clique 📝 EXAMEN\n2. Tape 1 à 10\n3. Coche A,B,C,D\n4. Clique VALIDER\n\nSi tu coches A,B,C alors que c'était A,B → FAUX en ROUGE", color=0x2ecc71)
    await ctx.send(embed=embed, view=StartView())

bot.run(os.environ.get("TOKEN"))
