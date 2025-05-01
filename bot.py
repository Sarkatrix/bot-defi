import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import json
import asyncio

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
        synced = await bot.tree.sync()
        print(f"🌐 {len(synced)} commande(s) slash synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")


async def envoyer_defi(ctx, defis):
    if not defis:
        await ctx.response.send_message("❌ Aucun défi disponible.", ephemeral=True)
        return

    defi_choisi = random.choice(defis)
    auteur = ctx.user
    message = await ctx.channel.send(f"{auteur.mention}, ton défi est : **{defi_choisi}**\n✅ Un autre membre doit réagir pour valider le point.")
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
        await ctx.channel.send(f"🎉 Défi validé par {user.mention} ! {auteur.mention} gagne 1 point.")
    except asyncio.TimeoutError:
        await ctx.channel.send(f"⏱️ Défi expiré : personne n’a validé dans l’heure.")

@tree.command(name="defi", description="Tire un défi aléatoire parmi tous les défis")
async def slash_defi(interaction: discord.Interaction):
    defis = defis_de_base + charger_defis_perso()
    await envoyer_defi(interaction, defis)

@tree.command(name="defilbl", description="Tire un défi uniquement parmi les défis personnalisés")
async def slash_defilbl(interaction: discord.Interaction):
    defis = charger_defis_perso()
    await envoyer_defi(interaction, defis)

@tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé de façon secrète")
@app_commands.describe(texte="Le texte du défi à ajouter")
async def slash_ajoutdefi(interaction: discord.Interaction, texte: str):
    sauvegarder_defi(texte)
    await interaction.response.send_message("✅", ephemeral=True, delete_after=1)

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

bot.run(os.getenv("DISCORD_TOKEN"))
