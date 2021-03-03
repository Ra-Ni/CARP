import os
from pathlib import Path
import re

from lex.token import token


class scanner:

    def __init__(self):
        self.tokens = None
        self.reserved = None
        self.data = None
        self.opts = {}

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

            elif (kind == 'inline_comment' or kind == 'block_comment') and self.opts['suppress_comments']:
                line_num += value.count('\n')
                continue

            yield token(str(kind), str(value), line_num)

            if kind == 'inline_comment' or kind == 'block_comment':
                line_num += value.count('\n')


def load(**kwargs):
    opts = {'dir': '../_config/',
            'lex_config': 'lex',
            'lex_suppress_comments': 0}
    opts.update(kwargs)

    opts['lex_config'] = Path(opts['dir'] + opts['lex_config'])

    if opts['lex_config'].is_dir():
        os.remove(opts['lex_config'])

    with open(opts['lex_config'], 'r') as fstream:
        injection = fstream.read()

    injection += "\nreader.tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nreader.reserved = reserved"
    reader = scanner()
    exec(injection)

    if 'lex_data' in opts:
        reader.open(opts['lex_data'])

    reader.opts['suppress_comments'] = opts['lex_suppress_comments']

    return reader
