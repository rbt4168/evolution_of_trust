from random import choice
from uuid import uuid4

class Bot():
    def __init__(self):
        self.history = []
        self.uuid = uuid4()
    
    def clear_history(self):
        self.history = []
    
    @property
    def uid(self):
        return self.uuid

    def move(self):
        raise NotImplementedError
        
    def append_history(self, move):
        self.history.append(move)

class Cooperator(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        return "C"

class Cheater(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        return "N"

class Copycat(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if len(self.history) < 1:
            return "C"
        return self.history[-1]

class Copykitten(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if len(self.history) < 2:
            return "C"
        if self.history[-2:] == ["N", "N"]:
            return "N"
        return "C"

class Copy3kitten(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if len(self.history) < 3:
            return "C"
        if self.history[-3:] == ["N", "N", "N"]:
            return "N"
        return "C"

class CopyNkitten(Bot):
    def __init__(self, n=3):
        super().__init__()
        self.n = n
    
    def move(self):
        if len(self.history) < self.n:
            return "C"
        if self.history[-self.n:] == ["N"] * self.n:
            return "N"
        return "C"

class NegtiveCopycat(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if len(self.history) < 1:
            return "N"
        return self.history[-1]

class NegtiveCopykitten(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if len(self.history) < 2:
            return "N"
        if self.history[-2:] == ["C", "C"]:
            return "C"
        return "N"
    
class Grudger(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        if "N" in self.history:
            return "N"
        return "C"

class Random(Bot):
    def __init__(self):
        super().__init__()
    
    def move(self):
        return choice("CN")
