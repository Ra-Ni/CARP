class token:

    def __init__(self):
        self.type = None
        self.lexeme = None
        self.line = None


class parser:

    def __init__(self):
        self.target_path = None

    def bind(self, target_path):
        self.target_path = target_path

    def exec(self):
        stream = open(self.target_path, 'r')
        text = stream.read()

        for char in text:
            yield char


