import discord
from discord import app_commands
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

defis_fichier = "defis.txt"
defis_custom_fichier = "defis_custom.txt"

# Chargement des défis de base et personnalisés
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

# Commande /defi classique avec tous les défis
@bot.tree.command(name="defi", description="Tire un défi aléatoire !")
async def defi(interaction: discord.Interaction):
    defis = charger_defis() + charger_defis_custom()
    if defis:
        defis_tire = random.choice(defis)
        await interaction.response.send_message(f"🎲 {interaction.user.mention}, ton défi est : **{defis_tire}**")
    else:
        await interaction.response.send_message("⚠️ Aucun défi n'est disponible.")

# Commande /defilbl qui ne tire que les défis personnalisés
@bot.tree.command(name="defilbl", description="Tire un défi personnalisé ajouté par les membres !")
async def defiLBL(interaction: discord.Interaction):
    defis = charger_defis_custom()
    if defis:
        defis_tire = random.choice(defis)
        await interaction.response.send_message(f"🎲 {interaction.user.mention}, ton défi personnalisé est : **{defis_tire}**")
    else:
        await interaction.response.send_message("⚠️ Aucun défi personnalisé n'est disponible.")

# Commande /ajoutdefi pour ajouter un défi personnalisé
@bot.tree.command(name="ajoutdefi", description="Ajoute un défi personnalisé !")
@app_commands.describe(defi="Décris ton défi à ajouter.")
async def ajoutdefi(interaction: discord.Interaction, defi: str):
    with open(defis_custom_fichier, "a", encoding="utf-8") as f:
        f.write(defi + "\n")
    await interaction.response.send_message("✅ Défi ajouté avec succès !", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} - Slash commands synchronisées.")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commande(s) synchronisée(s).")
    except Exception as e:
        print(f"❌ Erreur de synchronisation : {e}")

# Lancement du bot (token à fournir via Railway dans les variables d'environnement)
bot.run(os.environ["DISCORD_TOKEN"])
