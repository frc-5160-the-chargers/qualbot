import json
import time

class Logger:
    def __init__(self, service_name, prefix="", suffix="", config_file="config.json"):
        with open(config_file, 'r') as f:
            self.config_data = json.load(f)["logging"]

        self.prefix = "{}{}:".format(service_name, " " + prefix if prefix != "" else "", )
        self.suffix = suffix

    def write_to_log(self, data):
        '''write something to the log using the config'''
        file = open(self.config_data["log-file"], "a")
        file.write("{} {} {} {}\n".format(self.prefix, int(time.time()), data, self.suffix))
        file.close()

    def error(self, data):
        self.write_to_log("[ ERROR ] {}".format(data))

    def warning(self, data):
        self.write_to_log("[ WARNING ] {}".format(data))

    def info(self, data):
        self.write_to_log("[ INFO ] {}".format(data))
