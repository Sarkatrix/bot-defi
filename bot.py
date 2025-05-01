import discord
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

@bot.command()
async def defi(ctx):
    defis = defis_de_base + charger_defis_perso()
    defi_choisi = random.choice(defis)
    auteur = ctx.author

    message = await ctx.send(f"{auteur.mention}, ton défi est : **{defi_choisi}**\n✅ Un autre membre doit réagir pour valider le point.")
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
        await ctx.send(f"🎉 Défi validé par {user.mention} ! {auteur.mention} gagne 1 point.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏱️ Défi expiré : personne n’a validé dans l’heure.")

@bot.command()
async def ajoutdefi(ctx, *, nouveau_defi):
    sauvegarder_defi(nouveau_defi)
    await ctx.send(f"✅ Défi ajouté : « {nouveau_defi} » par {ctx.author.display_name}.")

@bot.command()
async def classement(ctx):
    points = charger_points()
    classement = sorted(points.items(), key=lambda x: x[1], reverse=True)
    if not classement:
        await ctx.send("Le classement est vide pour le moment.")
        return
    message = "**🏆 Classement des membres :**\n"
    for i, (user_id, score) in enumerate(classement, start=1):
        membre = await bot.fetch_user(int(user_id))
        message += f"{i}. {membre.name} — {score} point(s)\n"
    await ctx.send(message)

bot.run(os.getenv("DISCORD_TOKEN"))
