from abc import ABC, abstractmethod

class Behavior():
    def __init__(self, name):
        self.name = name

    def behavior_name(self):
        return self.name
    
    @abstractmethod
    def help(self):
        pass
    
    @abstractmethod
    def do(self, message):
        pass