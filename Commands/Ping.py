from Commands.Command import Command

class Ping(Command):
    def help(self):
        return "pong!"
    
    def do(self, message, symbol):
        return "pong!"