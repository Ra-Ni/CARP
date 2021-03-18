import re

from _config import CONFIG
from lex.token import Token


class Scanner:

    def __init__(self):
        self._tokens = None
        self._reserved = None
        self._data = None
        self._opts = None

    def open(self, file: str):
        with open(file, 'r') as fstream:
            data = fstream.read()

        self._data = data
        return self

    def open_text(self, text: str):
        self._data = text
        return self

    def read(self):
        for token in self.__iter__():
            yield token

    def readall(self):
        return list(self.read())

    def __iter__(self):
        line_num = 1

        for tok in re.finditer(self._tokens, self._data):
            kind = str(tok.lastgroup)
            value = str(tok.group())

            if kind == 'skip':
                continue

            elif kind == 'lf':
                line_num += 1
                continue

            elif kind == 'id' and value in self._reserved:
                kind = value

            elif 'comment' in kind and self._opts['suppress_comments']:
                line_num += value.count('\n')
                continue

            yield Token(kind, value, line_num)

            if 'comment' in kind:
                line_num += value.count('\n')

    @classmethod
    def load(cls, src_file: str = None, **kwargs):
        data = CONFIG['LEX_FILE'].read_text()
        data += "\nobj._tokens = '|'.join('(?P<%s>%s)' % pair for pair in tokens)\nobj._reserved = reserved"
        obj = cls()
        exec(data)

        opts = {'suppress_comments': 0}
        opts.update(kwargs)
        obj._opts = opts

        if src_file:
            obj.open(src_file)
        return obj
