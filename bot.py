import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json
from dotenv import load_dotenv

# Charger les variables d'environnement (comme le token)
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

FICHIER_DEFIS = "defis.txt"
FICHIER_POINTS = "points.json"

# Défis de base
defis_de_base = [
    "Crie un mot au hasard en vocal maintenant.",
    "Change ton pseudo en 'GigaNoob' pendant 10 minutes.",
    "Fais un compliment sincère à un autre membre du serveur.",
    "Fais un vocal de 10 secondes où tu parles comme un robot.",
    "Envoie une photo de ton frigo sans contexte."
]

# Charger les défis personnalisés depuis defis.txt
def charger_defis_perso():
    if os.path.exists(FICHIER_DEFIS):
        with open(FICHIER_DEFIS, "r", encoding="utf-8") as f:
            return [ligne.strip() for ligne in f if ligne.strip()]
    return []

# Tirage d’un défi
def piocher_defi(perso=False):
    defis = charger_defis_perso() if perso else defis_de_base + charger_defis_perso()
    return random.choice(defis) if defis else "Aucun défi disponible."

# Gestion des points
def charger_points():
    if os.path.exists(FICHIER_POINTS):
        with open(FICHIER_POINTS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_points(points):
    with open(FICHIER_POINTS, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=4)

# Slash command : tirer un défi classique
@tree.command(name="defi", description="Tire un défi au hasard (base + personnalisés)")
async def defi(interaction: discord.Interaction):
    texte = piocher_defi()
    await interaction.response.send_message(f"🎯 Défi : {texte}")
    message = await interaction.original_response()
    await message.add_reaction("✅")

    def check(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "✅" and not user.bot

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=3600.0, check=check)
        points = charger_points()
        points[str(user.id)] = points.get(str(user.id), 0) + 1
        sauvegarder_points(points)
        await message.channel.send(f"✅ {user.mention} a validé le défi et gagne 1 point !")
    except Exception:
        pass

# Slash command : tirer un défi personnalisé (LBL)
@tree.command(name="defilbl", description="Tire un défi parmi ceux ajoutés via /ajoutdefi.")
async def defilbl(interaction: discord.Interaction):
    texte = piocher_defi(perso=True)
    await interaction.response.send_message(f"🎯 Défi LBL : {texte}")
    message = await interaction.original_response()
    await message.add_reaction("✅")

    def check(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "✅" and not user.bot

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=3600.0, check=check)
        points = charger_points()
        points[str(user.id)] = points.get(str(user.id), 0) + 1
        sauvegarder_points(points)
        await message.channel.send(f"✅ {user.mention} a validé le défi et gagne 1 point !")
    except Exception:
        pass

# Slash command : ajouter un défi perso sans l'afficher
@tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé (non visible par les autres).")
@app_commands.describe(texte="Le défi à ajouter")
async def ajoutdefi(interaction: discord.Interaction, texte: str):
    if not texte.strip():
        await interaction.response.send_message("❌ Le défi ne peut pas être vide.", ephemeral=True)
        return

    with open(FICHIER_DEFIS, "a", encoding="utf-8") as f:
        f.write(texte.strip() + "\n")

    await interaction.response.send_message("", ephemeral=True)

# Slash command : classement des points
@tree.command(name="points", description="Affiche le classement des membres")
async def points(interaction: discord.Interaction):
    points = charger_points()
    classement = sorted(points.items(), key=lambda x: x[1], reverse=True)

    if not classement:
        await interaction.response.send_message("📊 Le classement est vide pour le moment.")
        return

    message = "**🏆 Classement des membres :**\n"
    for i, (user_id, score) in enumerate(classement, start=1):
        membre = await bot.fetch_user(int(user_id))
        message += f"{i}. {membre.name} — {score} point(s)\n"

    await interaction.response.send_message(message)

# Bot prêt
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🌐 {len(synced)} commande(s) slash synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# Lancer le bot
bot.run(os.getenv("DISCORD_TOKEN"))
