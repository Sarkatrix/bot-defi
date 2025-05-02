import discord
from discord import app_commands
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# Chargement des fichiers
defis_fichier = "defis.txt"
defis_perso_fichier = "defis_perso.txt"
classement_fichier = "classement.txt"

# Création des fichiers si inexistants
for fichier in [defis_fichier, defis_perso_fichier, classement_fichier]:
    if not os.path.exists(fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            pass

def ajouter_point(utilisateur):
    classement = {}
    with open(classement_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            nom, points = ligne.strip().split(":")
            classement[nom] = int(points)

    classement[utilisateur] = classement.get(utilisateur, 0) + 1

    with open(classement_fichier, "w", encoding="utf-8") as f:
        for nom, points in classement.items():
            f.write(f"{nom}:{points}\n")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🌐 {len(synced)} commande(s) slash synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

@tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé.")
@app_commands.describe(defi="Le texte du défi à ajouter.")
async def ajoutdefi(interaction: discord.Interaction, defi: str):
    with open(defis_perso_fichier, "a", encoding="utf-8") as f:
        f.write(defi + "\n")
    await interaction.response.send_message("Défi ajouté !", ephemeral=True)

@tree.command(name="defi", description="Tire un défi au hasard (de base ou perso).")
async def defi(interaction: discord.Interaction):
    with open(defis_fichier, "r", encoding="utf-8") as f:
        defis = f.readlines()
    with open(defis_perso_fichier, "r", encoding="utf-8") as f:
        defis += f.readlines()

    if not defis:
        await interaction.response.send_message("Aucun défi disponible.")
        return

    defi_choisi = random.choice(defis).strip()
    message = await interaction.channel.send(f"🎯 Défi : **{defi_choisi}**\n\nRéagissez avec ✅ pour valider ce défi !")
    await message.add_reaction("✅")

    def check(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "✅" and user != interaction.client.user

    # Attente indéfinie d'une réaction (timer supprimé)
    reaction, user = await bot.wait_for("reaction_add", check=check)
    ajouter_point(user.name)
    await interaction.channel.send(f"✅ Défi validé par {user.mention} ! +1 point.")

@tree.command(name="defilbl", description="Tire un défi parmi ceux ajoutés via /ajoutdefi.")
async def defilbl(interaction: discord.Interaction):
    with open(defis_perso_fichier, "r", encoding="utf-8") as f:
        defis = f.readlines()

    if not defis:
        await interaction.response.send_message("Aucun défi personnalisé disponible.")
        return

    defi_choisi = random.choice(defis).strip()
    message = await interaction.channel.send(f"🎯 Défi LBL : **{defi_choisi}**\n\nRéagissez avec ✅ pour valider ce défi !")
    await message.add_reaction("✅")

    def check(reaction, user):
        return reaction.message.id == message.id and str(reaction.emoji) == "✅" and user != interaction.client.user

    reaction, user = await bot.wait_for("reaction_add", check=check)
    ajouter_point(user.name)
    await interaction.channel.send(f"✅ Défi validé par {user.mention} ! +1 point.")

@tree.command(name="classement", description="Affiche le classement des joueurs.")
async def classement(interaction: discord.Interaction):
    classement = []
    with open(classement_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            nom, points = ligne.strip().split(":")
            classement.append((nom, int(points)))

    classement.sort(key=lambda x: x[1], reverse=True)

    message = "🏆 **Classement des défis** :\n"
    for i, (nom, points) in enumerate(classement, start=1):
        message += f"{i}. {nom} - {points} point(s)\n"

    await interaction.response.send_message(message)

# Lancement du bot
if __name__ == "__main__":
    import asyncio
    import os

    TOKEN = os.environ["DISCORD_TOKEN"]
    asyncio.run(bot.start(TOKEN))
