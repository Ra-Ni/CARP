
class Token:
    def __init__(self, type: str, value: str, line: int):
        self.type = type
        self.lexeme = value
        self.location = line

    def __str__(self):
        return self.type
