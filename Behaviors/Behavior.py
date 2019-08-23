from abc import ABC, abstractmethod

class Behavior(ABC):
    def __init__(self, name):
        self.name = name

    def behavior_name(self):
        return self.name

    @abstractmethod
    def check(self, message):
        pass
    
    @abstractmethod
    def do(self, message):
        pass