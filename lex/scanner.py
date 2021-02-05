import re
from lex import token


class scanner:

    def __init__(self, config_file: str = None):
        if config_file:
            self.tokens = None
            self.reserved = None
            if config_file:
                self.load(config_file)

    def load(self, config_file: str):
        with open(config_file, 'r') as fstream:
            config = fstream.read()
            config += "\nself.tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nself.reserved = reserved"
            exec(config)

    def read(self, path: str):
        with open(path, 'r') as fstream:
            data = fstream.read()

        line_num = 1

        for tok in re.finditer(self.tokens, data):

            kind = tok.lastgroup
            value = tok.group()

            if kind == 'skip':
                continue

            elif kind == 'lf':
                line_num += 1
                continue

            elif kind == 'id' and value in self.reserved:
                kind = str(value)

            yield token(str(kind), str(value), line_num)

            if kind == 'inline_comment' or kind == 'block_comment':
                line_num += value.count('\n')
