import asyncio

import discord

import Commands

#create client
client = discord.Client()
myprefix = "-"

#declare commands
helpcommand = Commands.Help("help")
pingcommand = Commands.Ping("ping")
#put commands into list of available commands
available_commands = [helpcommand, pingcommand]

#notify help command of available commands
helpcommand.add_available_commands(available_commands)

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

    for cmd in available_commands:
        if message.content.startswith(myprefix + cmd.command_name().lower()):
            cmd_response = cmd.do(message)
            await message.channel.send(cmd_response)



#get key from gitignored text file
#key.txt should be in the top-level directory and should ONLY contain the api key with no whitespace.
key = ""
with open("key.txt", "r") as keyfile:
    key = str.strip(keyfile.readline())

#TODO: Add thing to read the API key from a gitignored file
client.run(key)