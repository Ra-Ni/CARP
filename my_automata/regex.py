import re
import uuid
from collections import deque
from typing import Union

from my_automata import *


class token:
    def __init__(self, type: str, value: Union[int, str], line: int):
        self.type = type
        self.lexeme = repr(value)[1:-1]
        self.location = line

    def __str__(self):
        return f'[{self.type}, {self.lexeme}, {self.location}]'


op_order = {'NOP': 5, '?': 0, '*': 0, '.': 1, '|': 2, '(': 4, ')': 4}

nonzero = r'[1-9]'
letter = r'[a-zA-Z]'
digit = fr'(?:0|{nonzero})'
alphanum = rf'(?:{letter}|{digit}|_)'
character = rf'(?:{alphanum}| )'
fractnum = rf'[.](?:0|{digit}*{nonzero})'
intnum = rf'(?:{nonzero}{digit}*|0)'
floatnum = rf'{intnum}{fractnum}(?:e[+\-]?{intnum})?'
stringlit = rf'"{character}*"'
id = rf'{letter}{alphanum}*'
inline_comment = r'//.*'
block_comment = r'/\*(?:.|\s)*?\*/'
reserved = {'if', 'then', 'else',
            'integer', 'float', 'string',
            'void', 'public', 'private',
            'func', 'var', 'class',
            'while', 'read',
            'write', 'return', 'main',
            'inherits', 'break', 'continue'}
operators = {'=', '<', ''}
tokens = [
    ('id', id),
    ('floatnum', floatnum),
    ('intnum', intnum),
    ('stringlit', stringlit),
    ('inline_comment', inline_comment),
    ('block_comment', block_comment),
    ('lf', r'\n'),
    ('skip', r'[ \t]+'),
    ('opencubr', r'\{'),
    ('closecubr', r'\}'),
    ('colon', r':'),
    ('eq', '=='),
    ('assign', '='),
    ('minus', r'\-'),
    ('plus', r'\+'),
    ('or', r'\|'),
    ('openpar', r'\)'),
    ('closepar', r'\('),
    ('opensqbr', r'\['),
    ('coloncolon', '::'),
    ('div', '/'),
    ('mult', r'\*'),
    ('qmark', r'\?'),
    ('noteq', '<>'),
    ('and', '&'),
    ('closesqbr', '\]'),
    ('comma', ','),
    ('lt', '<'),
    ('gt', '>'),
    ('geq', '>='),
    ('leq', '<='),
    ('semi', ';'),
    ('dot', '\.'),
    ('not', '!'),
    ('invalidchar', rf'.')
]


def scan(path: str):
    with open(path, 'r') as scanner:
        data = scanner.read()

    grammar = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    line_start = 0
    line_num = 1

    for tok in re.finditer(grammar, data):

        kind = tok.lastgroup
        value = tok.group()

        if kind == 'skip':
            continue

        elif kind == 'lf':
            line_num += 1
            continue

        elif kind == 'id' and value in reserved:
            kind = str(value)

        yield token(str(kind), str(value), line_num)

        if kind == 'inline_comment' or kind == 'block_comment':
            line_num += value.count('\n')
