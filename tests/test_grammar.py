import unittest

from lex import scanner
from syntax import Parser

_DIR = '../src/_config/'
f = Parser.load(config_dir=_DIR)
s = scanner(config_dir=_DIR, suppress_comments=1)


def _run(file):
    path = file
    s.open(path)
    return f.parse(s)


class test_scanner(unittest.TestCase):

    def test_var(self):
        assert _run('grammar/TEST_var.src')

    def test_class(self):
        assert _run('grammar/TEST_class.src')

    def test_exp(self):
        assert _run('grammar/TEST_exp.src')

    def test_func_def(self):
        assert _run('grammar/TEST_func_def.src')

    def test_func_body(self):
        assert _run('grammar/TEST_func_body.src')

    def test_variable(self):
        assert _run('grammar/TEST_variable.src')

    def test_no_main(self):
        assert not _run('grammar/TEST_no_main.src')

    def test_mult_main(self):
        assert not _run('grammar/TEST_mult_main.src')

    def test_array_return(self):
        assert not _run('grammar/TEST_array_return.src')

    def test_mult_var_block(self):
        assert not _run('grammar/TEST_mult_var_block.src')

    def test_func_var(self):
        assert _run('grammar/TEST_func_var.src')

