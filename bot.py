import asyncio

import discord

import Commands

#create client
client = discord.Client()
myprefix = "-"

#declare commands
helpcommand = Commands.Ping("ping")

@client.event
async def on_ready():
    """Display information when client logged in"""
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")

@client.event
async def on_message(message):
    """Respond to messages"""


#TODO: Add thing to read the API key from a gitignored file
client.run("")