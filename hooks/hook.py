import discord
import json
import traceback

from fancy_logger import Logger

class Hook:
    def __init__(self, hook_name, config_file="config.json"):
        with open(config_file, 'r') as f:
            data = json.load(f)
            self.config_data = data["webhooks"][hook_name]
        self.logger = Logger(hook_name, config_file=config_file)
        self.logger.info("Initialized")
    
    def generate_embed(self):
        '''this function should be overridden by other objects. generate the embed for the webhook'''
        pass

    def send(self):
        '''this shouldn't be overridden. sends the hoook created by generate_embed'''
        self.logger.info("Sending embed...")
        embed = None
        try:
            embed = self.generate_embed()
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error generating embed:\n\t{e}")
        if embed != None:
            try:
                discord_hook = discord.Webhook.partial(self.config_data["discord-id"], self.config_data["discord-token"], adapter=discord.RequestsWebhookAdapter())
                discord_hook.send(embed=embed)
                self.logger.info("Embed sent")
            except Exception as e:
                traceback.print_exc()
                self.logger.error(f"Error while sending embed:\n\t{e}")
        else:
            self.logger.warning("Generated embed was empty")