from abc import ABC, abstractmethod


class Command(ABC):
    def __init__(self, name):
        self.name = name
    
    def command_name(self):
        return self.name
    
    #require commands to return a short help string
    @abstractmethod
    def help(self):
        pass

    #require commands to have a method to run the command
    @abstractmethod
    def do(self, message, symbol):
        pass