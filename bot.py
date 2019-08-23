import asyncio

import discord

import Commands
import Behaviors

#create client
client = discord.Client()
myprefix = "-"

#declare commands
helpcommand = Commands.Help("help")
pingcommand = Commands.Ping("ping")

#declare behaviors
comment = Behaviors.TeamComment("comment")

#put commands into list of available commands
available_commands = [helpcommand, pingcommand]
#pub behaviors into list of available behaviors
available_behaviors = [comment]

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

    #this loop does any interactable commands
    for cmd in available_commands:
        if message.content.startswith(myprefix + cmd.command_name().lower()):
            cmd_response = cmd.do(message)
            await message.channel.send(cmd_response)
    
    #this loop handles any behaviors that need to be performed based on the message
    for be in available_behaviors:
        if be.check(message):
            be.do(message)


#get key from gitignored text file
#key.txt should be in the top-level directory and should ONLY contain the api key with no whitespace.
key = ""
with open("key.txt", "r") as keyfile:
    key = str.strip(keyfile.readline())

#run the client with the key retrieved from key.txt
client.run(key)