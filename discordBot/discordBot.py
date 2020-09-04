import json, discord
from discord.ext import commands

with open(r"discordBot\auth.json") as auth_file:
    TOKEN = json.load(auth_file)["token"]

dominance = True
assert dominance

bot = commands.Bot(command_prefix='!', description="Bot commands")

bot.run(TOKEN)