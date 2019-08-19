from Commands.Command import Command

class Help(Command):
    def __init__(self, name):
        super().__init__(name)
    
    def add_available_commands(self, available_commands):
        """pass a list of active (not in-dev) commands so that the help menu can see them"""
        self.available_commands = available_commands

    def do(self, message):
        return self.generate_help(message)
    
    def generate_help(self, message):
        """Generate a message when a user asks for help"""
        
        #get number of spaces equal to longest command length (this is for formatting)
        maxlen = 0
        for c in self.available_commands:
            if len(c.command_name()) >= maxlen:
                maxlen = len(c.name)

        #generate the helpstring from each command's help message
        helpstring = ""
        if len(self.available_commands) > 0:
            helpstring += "**Commands** \n```"
            for c in self.available_commands:
                helpstring += self.spacing(c.command_name(), maxlen) + c.help() + "\n"

    def spacing(self, name, maxlen):
        """Determine the number of spaces needed for helpstring formatting"""
        if len(name) == maxlen:
            return name + "\t"
        else:
            spaces = ""
            for s in range(0, maxlen - len(name)):
                spaces += " "
            return name + spaces + "\t"