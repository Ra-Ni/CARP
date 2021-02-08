import unittest

from lex import scanner

DEFAULT_CONFIG = '../config'

class TestStringMethods(unittest.TestCase):
    s = scanner(DEFAULT_CONFIG)

    def _apply(self, type: str, test: str, expected: list):
        output = [o.lexeme for o in TestStringMethods.s.read(test) if o.type == type]
        self.assertEqual(expected, output)

    def test_id(self):
        self._apply('id', 'a123', ['a123'])
        self._apply('id', 'a123a', ['a123a'])
        self._apply('id', '_a', ['a'])
        self._apply('id', '123', [])
        self._apply('id', 'a_', ['a_'])
        self._apply('id', 'a_0', ['a_0'])
        self._apply('id', 'lol', ['lol'])


    def test_integer(self):
        pass

    def test_float(self):
        pass

    def test_string(self):
        pass

    def test_eq(self):
        pass

    def test_neq(self):
        pass

    def test_lt(self):
        pass

    def test_gt(self):
        pass

    def test_leq(self):
        pass

    def test_geq(self):
        pass

    def test_plus(self):
        pass

    def test_minus(self):
        pass

    def test_mult(self):
        pass

    def test_div(self):
        pass

    def test_assign(self):
        pass

    def test_or(self):
        pass

    def test_and(self):
        pass

    def test_not(self):
        pass

    def test_optional(self):
        pass

    def test_openpar(self):
        pass

    def test_closepar(self):
        pass

    def test_opencubr(self):
        pass

    def test_closecubr(self):
        pass

    def test_opensqr(self):
        pass

    def test_closesqr(self):
        pass

    def test_semi(self):
        pass

    def test_comma(self):
        pass

    def test_dot(self):
        pass

    def test_colon(self):
        pass

    def test_coloncolon(self):
        pass

    def test_if(self):
        pass

    def test_then(self):
        pass

    def test_else(self):
        pass

    def test_intnum(self):
        pass

    def test_floatnum(self):
        pass

    def test_stringlit(self):
        pass

    def test_void(self):
        pass

    def test_public(self):
        pass

    def test_private(self):
        pass

    def test_func(self):
        pass

    def test_var(self):
        pass

    def test_class(self):
        pass

    def test_while(self):
        pass

    def test_read(self):
        pass

    def test_write(self):
        pass

    def test_return(self):
        pass

    def test_main(self):
        pass

    def test_inherits(self):
        pass

    def test_break(self):
        pass

    def test_continue(self):
        self._apply('continue', 'cont', [])
        self._apply('continue', '', [])
        self._apply('continue', '\nc\no\nn\nt\ni\nu\ne', [])
        self._apply('continue', 'icontinue', [])
        self._apply('continue', 'i continue', ['continue'])
        self._apply('continue', 'i continue cont', ['continue'])
        self._apply('continue', 'i continue cont continu \n```contn`4continue', ['continue', 'continue'])



if __name__ == '__main__':
    unittest.main()
