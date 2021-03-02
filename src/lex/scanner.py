import re

from lex.token import token


class scanner:

    def __init__(self):
        self.tokens = None
        self.reserved = None
        self.text = None
        self._opts = {}

    def __inject__(self, code: str):
        exec(code)

    def open(self, file: str):
        with open(file, 'r') as fstream:
            text = fstream.read()
        self.text = text

    def options(self, **kwargs):
        self._opts.update(kwargs)

    def __iter__(self):
        line_num = 1

        for tok in re.finditer(self.tokens, self.text):
            kind = tok.lastgroup
            value = tok.group()

            if kind == 'skip':
                continue

            elif kind == 'lf':
                line_num += 1
                continue

            elif kind == 'id' and value in self.reserved:
                kind = str(value)

            elif kind == 'inline_comment' or kind == 'block_comment' and self._opts['suppress_comments']:
                line_num += value.count('\n')
                continue

            yield token(str(kind), str(value), line_num)

            if kind == 'inline_comment' or kind == 'block_comment':
                line_num += value.count('\n')

    @classmethod
    def load(cls, config: str, file: str = None):
        reader = cls()
        with open(config, 'r') as fstream:
            code = fstream.read()
            code += "\nself.tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nself.reserved = reserved"
            reader.__inject__(code)
        if file:
            reader.open(file)

        return reader
