from typing import Union


class token:
    def __init__(self, type: str, value: Union[int, str], line: int):
        self.type = type
        self.lexeme = repr(value)[1:-1]
        self.location = line

    def __str__(self):
        return f'[{self.type}, {self.lexeme}, {self.location}]'
