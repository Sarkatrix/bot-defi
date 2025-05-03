import discord
from discord import app_commands
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.reactions = True
intents.message_content = True
intents.members = True  # nécessaire pour lister les membres
bot = commands.Bot(command_prefix="/", intents=intents)

defis_fichier = "defis.txt"
defis_custom_fichier = "defis_custom.txt"

# Chargement des défis
def charger_defis():
    defis = []
    if os.path.exists(defis_fichier):
        with open(defis_fichier, "r", encoding="utf-8") as f:
            defis.extend([ligne.strip() for ligne in f if ligne.strip()])
    return defis

def charger_defis_custom():
    defis = []
    if os.path.exists(defis_custom_fichier):
        with open(defis_custom_fichier, "r", encoding="utf-8") as f:
            defis.extend([ligne.strip() for ligne in f if ligne.strip()])
    return defis

classement_fichier = "classement.txt"

def ajouter_point(utilisateur):
    classement = {}
    if os.path.exists(classement_fichier):
        with open(classement_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                nom, points = ligne.strip().split(":")
                classement[nom] = int(points)

    classement[utilisateur] = classement.get(utilisateur, 0) + 1

    with open(classement_fichier, "w", encoding="utf-8") as f:
        for nom, points in classement.items():
            f.write(f"{nom}:{points}\n")

async def choisir_membre_aleatoire(guild, exclure=None):
    membres = [m for m in guild.members if not m.bot and (exclure is None or m.id != exclure.id)]
    return random.choice(membres) if membres else None

@bot.tree.command(name="defi", description="Tire un défi aléatoire pour un membre du serveur.")
async def defi(interaction: discord.Interaction):
    defis = charger_defis() + charger_defis_custom()
    if defis:
        membre = await choisir_membre_aleatoire(interaction.guild)
        if not membre:
            await interaction.response.send_message("⚠️ Aucun membre valide à défier.", ephemeral=True)
            return

        defi_choisi = random.choice(defis)
        await interaction.response.send_message(f"🎯 Le défi est pour {membre.mention} : **{defi_choisi}**", ephemeral=False)
        message = await interaction.channel.send(f"🎯 {membre.mention}, ton défi est : **{defi_choisi}**\n\nUn autre membre doit réagir avec ✅ pour valider ce défi !")
        await message.add_reaction("✅")

        def check(reaction, user):
            return (
                reaction.message.id == message.id and
                str(reaction.emoji) == "✅" and
                user.id != membre.id and
                not user.bot
            )

        reaction, user = await bot.wait_for("reaction_add", check=check)
        ajouter_point(membre.name)
        await interaction.channel.send(f"✅ {membre.mention} a validé son défi grâce à {user.mention} ! +1 point.")
    else:
        await interaction.response.send_message("⚠️ Aucun défi n'est disponible.")

@bot.tree.command(name="defilbl", description="Tire un défi personnalisé pour un membre aléatoire.")
async def defilbl(interaction: discord.Interaction):
    defis = charger_defis_custom()
    if defis:
        membre = await choisir_membre_aleatoire(interaction.guild)
        if not membre:
            await interaction.response.send_message("⚠️ Aucun membre valide à défier.", ephemeral=True)
            return

        defi_choisi = random.choice(defis)
        await interaction.response.send_message(f"🎯 Le défi personnalisé est pour {membre.mention} : **{defi_choisi}**", ephemeral=False)
        message = await interaction.channel.send(f"🎯 {membre.mention}, ton défi personnalisé est : **{defi_choisi}**\n\nUn autre membre doit réagir avec ✅ pour valider ce défi !")
        await message.add_reaction("✅")

        def check(reaction, user):
            return (
                reaction.message.id == message.id and
                str(reaction.emoji) == "✅" and
                user.id != membre.id and
                not user.bot
            )

        reaction, user = await bot.wait_for("reaction_add", check=check)
        ajouter_point(membre.name)
        await interaction.channel.send(f"✅ {membre.mention} a validé son défi grâce à {user.mention} ! +1 point.")
    else:
        await interaction.response.send_message("⚠️ Aucun défi personnalisé n'est disponible.")

@bot.tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé !")
@app_commands.describe(defi="Décris ton défi à ajouter.")
async def ajoutdefi(interaction: discord.Interaction, defi: str):
    with open(defis_custom_fichier, "a", encoding="utf-8") as f:
        f.write(defi + "\n")
    await interaction.response.send_message("✅ Défi ajouté avec succès !", ephemeral=True)

@bot.tree.command(name="classement", description="Affiche le classement des joueurs.")
async def classement(interaction: discord.Interaction):
    classement = []
    if os.path.exists(classement_fichier):
        with open(classement_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                nom, points = ligne.strip().split(":")
                classement.append((nom, int(points)))

    classement.sort(key=lambda x: x[1], reverse=True)
    message = "🏆 **Classement des défis** :\n"
    for i, (nom, points) in enumerate(classement, start=1):
        message += f"{i}. {nom} - {points} point(s)\n"
    await interaction.response.send_message(message)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} - Slash commands synchronisées.")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

bot.run(os.environ["DISCORD_TOKEN"])
