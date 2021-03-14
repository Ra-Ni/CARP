import os
from pathlib import Path
import re

from lex.token import token


class scanner:

    def __init__(self, config_dir: str = './_config/', **kwargs):
        self.tokens = None
        self.reserved = None

        self.opts = {'suppress_comments': 0}
        self.opts.update(**kwargs)

        data = Path(config_dir + 'lex').read_text()
        data += "\nself.tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nself.reserved = reserved"
        self.data = exec(data)

    def open(self, file: str):
        with open(file, 'r') as fstream:
            data = fstream.read()

        self.data = data

    def __iter__(self):
        line_num = 1

        for tok in re.finditer(self.tokens, self.data):
            kind = str(tok.lastgroup)
            value = str(tok.group())

            if kind == 'skip':
                continue

            elif kind == 'lf':
                line_num += 1
                continue

            elif kind == 'id' and value in self.reserved:
                kind = value

            elif 'comment' in kind and self.opts['suppress_comments']:
                line_num += value.count('\n')
                continue

            yield token(kind, value, line_num)

            if 'comment' in kind:
                line_num += value.count('\n')
