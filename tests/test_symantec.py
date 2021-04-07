import logging
import unittest
from pathlib import Path

from _config import CONFIG
from lex import Scanner
from symantec import SymantecTable
from syntax import Parser

CONFIG['LEX_FILE'] = Path('../src/_config/lex.conf')
CONFIG['LL1_FILE'] = Path('../src/_config/ll1.bak.xz')
CONFIG['VITALS_FILE'] = Path('../src/_config/vitals.bak.xz')
CONFIG['GRAMMAR_FILE'] = Path('../src/_config/grammar.conf')

f = Parser.load()
s = Scanner.load(suppress_comments=1)

def _run(file):
    s.open(file)
    resp = f.parse(s)

    path = Path(file)
    path = str(path.parent) + '\\out\\' + str(path.stem)
    errors = path + '.log'
    path = path + '.png'

    errors = logging.FileHandler(errors, mode='w', encoding='utf-8', delay=True)
    errors.setLevel(logging.DEBUG)

    if f.ast:
        sym = SymantecTable.from_ast(f.ast, errors)
        sym.render(path)


    return resp


class test_scanner(unittest.TestCase):

    def test_var(self):
        _run('symantec/TEST_var.src')

    def test_class(self):
        _run('symantec/TEST_class.src')

    def test_exp(self):
        _run('symantec/TEST_exp.src')

    def test_func_def(self):
        _run('symantec/TEST_func_def.src')

    def test_func_body(self):
        _run('symantec/TEST_func_body.src')

    def test_variable(self):
        _run('symantec/TEST_variable.src')

    def test_no_main(self):
        _run('symantec/TEST_no_main.src')

    def test_mult_main(self):
        _run('symantec/TEST_mult_main.src')

    def test_array_return(self):
        _run('symantec/TEST_array_return.src')

    def test_mult_var_block(self):
        _run('symantec/TEST_mult_var_block.src')

    def test_func_var(self):
        _run('symantec/TEST_func_var.src')

