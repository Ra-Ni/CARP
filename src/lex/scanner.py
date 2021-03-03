import os
import pathlib
import re

from lex.token import token


class scanner:

    def __init__(self, **kwargs):
        self.tokens = None
        self.reserved = None
        self.data = None
        self._opts = {}
        self._opts.update(kwargs)

    def open(self, file: str):
        with open(file, 'r') as fstream:
            data = fstream.read()

        self.data = data

    def __iter__(self):
        line_num = 1

        for tok in re.finditer(self.tokens, self.data):
            kind = tok.lastgroup
            value = tok.group()

            if kind == 'skip':
                continue

            elif kind == 'lf':
                line_num += 1
                continue

            elif kind == 'id' and value in self.reserved:
                kind = str(value)

            elif (kind == 'inline_comment' or kind == 'block_comment') and self._opts['suppress_comments']:
                line_num += value.count('\n')
                continue

            yield token(str(kind), str(value), line_num)

            if kind == 'inline_comment' or kind == 'block_comment':
                line_num += value.count('\n')

    @classmethod
    def load(cls, file: str = None, **kwargs):
        config = pathlib.Path('../_config/lex')

        if config.is_dir():
            os.remove(config)

        with open(config, 'r') as fstream:
            code = fstream.read()

        reader = cls(**kwargs)
        code += "\nreader.tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nreader.reserved = reserved"
        exec(code)

        if file:
            reader.open(file)

        return reader
