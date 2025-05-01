import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json

# Récupération du token depuis l'environnement Render
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

FICHIER_DEFIS = "defis.txt"
FICHIER_POINTS = "points.json"

defis_de_base = [
    "Crie un mot au hasard en vocal maintenant.",
    "Change ton pseudo en 'GigaNoob' pendant 10 minutes.",
    "Fais un compliment sincère à un autre membre du serveur.",
    "Fais un vocal de 10 secondes où tu parles comme un robot.",
    "Envoie une photo de ton frigo sans contexte."
]

def charger_defis_perso():
    if os.path.exists(FICHIER_DEFIS):
        with open(FICHIER_DEFIS, "r", encoding="utf-8") as f:
            return [ligne.strip() for ligne in f if ligne.strip()]
    return []

def sauvegarder_defi(defi):
    with open(FICHIER_DEFIS, "a", encoding="utf-8") as f:
        f.write(defi + "\n")

def charger_points():
    if os.path.exists(FICHIER_POINTS):
        with open(FICHIER_POINTS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_points(points):
    with open(FICHIER_POINTS, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=4)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🌐 {len(synced)} commande(s) slash synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

async def envoyer_defi(interaction: discord.Interaction, defis):
    if not defis:
        await interaction.response.send_message("❌ Aucun défi disponible.", ephemeral=True)
        return

    defi_choisi = random.choice(defis)
    auteur = interaction.user
    await interaction.response.send_message(f"{auteur.mention}, ton défi est : **{defi_choisi}**\n✅ Un autre membre doit réagir pour valider le point.")
    message = await interaction.original_response()
    await message.add_reaction("✅")

    def check(reaction, user):
        return (
            reaction.message.id == message.id and
            str(reaction.emoji) == "✅" and
            user != auteur and
            not user.bot
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=3600.0, check=check)
        points = charger_points()
        auteur_id = str(auteur.id)
        points[auteur_id] = points.get(auteur_id, 0) + 1
        sauvegarder_points(points)
        await message.channel.send(f"🎉 Défi validé par {user.mention} ! {auteur.mention} gagne 1 point.")
    except:
        await message.channel.send("⏱️ Temps écoulé. Personne n’a validé le défi.")

@tree.command(name="defi", description="Tire un défi aléatoire parmi tous les défis")
async def slash_defi(interaction: discord.Interaction):
    defis = defis_de_base + charger_defis_perso()
    await envoyer_defi(interaction, defis)

@tree.command(name="defilbl", description="Tire un défi uniquement parmi les défis personnalisés")
async def slash_defilbl(interaction: discord.Interaction):
    defis = charger_defis_perso()
    await envoyer_defi(interaction, defis)

@tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé (visible uniquement pour toi)")
@app_commands.describe(texte="Le texte du défi à ajouter")
async def slash_ajoutdefi(interaction: discord.Interaction, texte: str):
    if not texte.strip():
        await interaction.response.send_message("❌ Le défi ne peut pas être vide.", ephemeral=True)
        return

    sauvegarder_defi(texte.strip())
    await interaction.response.send_message("✅ Défi ajouté avec succès.", ephemeral=True)

@tree.command(name="classement", description="Affiche le classement des membres par points")
async def slash_classement(interaction: discord.Interaction):
    points = charger_points()
    classement = sorted(points.items(), key=lambda x: x[1], reverse=True)
    if not classement:
        await interaction.response.send_message("Le classement est vide pour le moment.")
        return
    message = "**🏆 Classement des membres :**\n"
    for i, (user_id, score) in enumerate(classement, start=1):
        membre = await bot.fetch_user(int(user_id))
        message += f"{i}. {membre.name} — {score} point(s)\n"
    await interaction.response.send_message(message)

# Lancer le bot avec le token lu depuis l'environnement
bot.run(TOKEN)
