import unittest
from typing import Union

from lex import scanner

DEFAULT_CONFIG = '../examples/config'


class test_scanner(unittest.TestCase):
    s = scanner(DEFAULT_CONFIG)

    def _apply(self, type: str, test: str, expected: Union[int, list]):
        output = [o.lexeme for o in test_scanner.s.open(test) if o.type == type]
        if isinstance(expected, int):
            output = len(output)
        self.assertEqual(expected, output)

    def _reserved_apply(self, type: str):
        test_str = f'{type[1:]}\nt{type}\n{type}a\n\n{" ".join(type)}\n{type}'
        self._apply(type, test_str, 1)

    def test_id(self):
        self._apply('id', 'a123', ['a123'])
        self._apply('id', 'a123a', ['a123a'])
        self._apply('id', '_a', ['a'])
        self._apply('id', '123', [])
        self._apply('id', 'a_', ['a_'])
        self._apply('id', 'a_0', ['a_0'])
        self._apply('id', 'lol', ['lol'])

    def test_intnum(self):
        self._apply('intnum', '1\n10\n0\n010\n\n', ['1', '10', '0', '0', '10'])

    def test_floatnum(self):
        self._apply('floatnum',
                    """
                    .2
                    .0
                    0.0 0.1
                    0.a
                    0.
                    0.1e1
                    0.1e
                    0.1e-
                    0.1e-12
                    """,
                    ['0.0', '0.1', '0.1e1', '0.1', '0.1', '0.1e-12'])

    def test_stringlit(self):
        self._apply('stringlit', '"this is a " another string""', ['"this is a "', '""'])

    def test_eq(self):
        self._apply('eq',
                    """
                    ==
                    =   =
                    = =
                    
                    =
                    """, 1)

    def test_noteq(self):
        self._apply('noteq',
                    """
                    < >
                    <
                    >
                    <>
                    ><
                    """, 1)

    def test_lt(self):
        self._apply('lt',
                    """
                    <>
                    >
                    <=
                    <   =
                    <
                    
                    """, 2)

    def test_gt(self):
        self._apply('gt',
                    """
                    <>
                    <
                    >
                    
                    ><
                    >   =
                    >
                    >=
                    """, 4)

    def test_leq(self):
        self._apply('leq',
                    """
                    >=
                    < =
                    <=
                    <   =
                    <

                    """, 1)

    def test_geq(self):
        self._apply('geq',
                    """
                    >=
                    > =
                    >=
                    >   =
                    >

                    """, 2)

    def test_plus(self):
        self._apply('plus',
                    """
                    a+b+c
                    ++
                    12.3e+2
                    -
                    
                    """, 4)

    def test_minus(self):
        self._apply('minus',
                    """
                    a-b-c
                    --
                    +
                    12.3e-1

                    """, 4)

    def test_dot(self):
        self._apply('dot',
                    """
                    .
                    12.3
                    hi.how.are.you
                    
                    """, 4)

    def test_colon(self):
        self._apply('colon',
                    """
                    :
                    ::
                    : :
                    
                    """, 3)

    def test_coloncolon(self):
        self._apply('coloncolon',
                    """
                    : :
                    :
                    ::
                    ::=
                    """, 2)

    def test_if(self):
        self._reserved_apply('if')

    def test_then(self):
        self._reserved_apply('then')

    def test_else(self):
        self._reserved_apply('else')

    def test_void(self):
        self._reserved_apply('void')

    def test_public(self):
        self._reserved_apply('public')

    def test_private(self):
        self._reserved_apply('private')

    def test_func(self):
        self._reserved_apply('func')

    def test_var(self):
        self._reserved_apply('var')

    def test_class(self):
        self._reserved_apply('class')

    def test_while(self):
        self._reserved_apply('while')

    def test_read(self):
        self._reserved_apply('read')

    def test_write(self):
        self._reserved_apply('write')

    def test_return(self):
        self._reserved_apply('return')

    def test_main(self):
        self._reserved_apply('main')

    def test_inherits(self):
        self._reserved_apply('inherits')

    def test_break(self):
        self._reserved_apply('break')

    def test_continue(self):
        self._reserved_apply('continue')

    def test_float(self):
        self._reserved_apply('float')

    def test_string(self):
        self._reserved_apply('string')

    def test_integer(self):
        self._reserved_apply('integer')


if __name__ == '__main__':
    unittest.main()
