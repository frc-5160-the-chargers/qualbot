import discord
import json
import traceback
import time
import base64

from fancy_logger import Logger
from slack import send_message_to_slack

class Hook:
    def __init__(self, hook_name, config_file="config.json"):
        self.config_file = config_file
        self.hook_name = hook_name
        with open(config_file, 'r') as f:
            data = json.load(f)
            self.config_data = data["webhooks"][hook_name]
            self.delay = self.config_data["sending-delay"]
        self.logger = Logger(hook_name, config_file=config_file)
        self.logger.info("Initialized")
    
    def update_hook_data(self, key, value):
        '''write data specific to this hook for internal usage to the config file'''
        self.config_data["hook-data"][key] = value
        with open(self.config_file, 'r') as f:
            data = json.load(f)
        with open(self.config_file, 'w') as f:
            data["webhooks"][self.hook_name] = self.config_data
            json.dump(data, f)

    def get_hook_data(self, key):
        '''get a value from the cached hook data'''
        return self.config_data["hook-data"][key]

    def generate_embed(self):
        '''this function should be overridden by other objects. generate the embed for the webhook'''
        pass

    def send_to_service(self, embed):
        '''this should be overridden based on the type of service'''
        pass

    def get_embed_str(self, embed):
        '''get a string representation of an embed'''
        return ""

    def send(self):
        '''this shouldn't be overridden. sends the hoook created by generate_embed'''
        self.logger.info("Sending embed...")
        last_sent_time = int(time.time()-self.get_hook_data("last-sent"))
        if last_sent_time < self.delay:
            self.logger.warning("Not sent:\n\tLast sent {}s ago".format(last_sent_time))
            return
        embed = None
        try:
            embed = self.generate_embed()
        except Exception as e:
            traceback.print_exc()
            self.logger.error("Error generating embed:\n\t{}".format(e))
        if embed != None:
            try:
                last_embed_str = self.get_embed_str(embed)
                if last_embed_str == self.get_hook_data("last-sent-b64"):
                    self.logger.warning("This hook has already been sent")
                    return
                self.update_hook_data("last-sent-b64", last_embed_str)

                self.send_to_service(embed)
                
                self.logger.info("Embed sent")
            except Exception as e:
                traceback.print_exc()
                self.logger.error("Error while sending embed:\n\t{}".format(e))
        else:
            self.logger.warning("Generated embed was empty")
        try:
            self.update_hook_data("last-sent", int(time.time()))
        except Exception as e:
            traceback.print_exc()
            self.logger.error("Error recording last time sent:\n\t{}".format(e))

class DiscordHook(Hook):
    def __init__(self, hook_name, config_file="config.json"):
        super().__init__(hook_name, config_file)

    def get_embed_str(self, embed):
        return str(base64.b64encode(json.dumps(embed.to_dict(), sort_keys=True).encode('utf-8')), 'utf-8')

    def send_to_service(self, embed):
        discord_hook = discord.Webhook.partial(self.config_data["discord-id"], self.config_data["discord-token"], adapter=discord.RequestsWebhookAdapter())
        discord_hook.send(embed=embed)

class SlackHook(Hook):
    def __init__(self, hook_name, config_file="config.json"):
        super().__init__(hook_name, config_file)

    def get_embed_str(self, embed):
        return str(base64.b64encode(json.dumps(embed, sort_keys=True).encode('utf-8')), 'utf-8')

    def send_to_service(self, embed):
        send_message_to_slack(embed, self.config_data["slack-url"], self.logger)
