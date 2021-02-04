import unittest
from copy import deepcopy

from sortedcontainers import SortedSet

from my_automata.automata import *


class TestStringMethods(unittest.TestCase):

    def test_init(self):
        a = automata()

        for attr in a.__dict__.keys():
            self.assertEqual(getattr(a, attr), None)

    def test_advanced_init(self):
        input = {
            'start': '1',
            'final': {'2'},
            'alphabets': {'3','4'},
            'states': {1, 2, 3},
            'transitions': {1: {2: {3}}, 2: {3: {4}}}
        }

        a = automata(**input)

        for attr in a.__dict__.keys():
            self.assertEqual(getattr(a, attr), input[attr])

    def test_union(self):
        first = {
            'start': 1,
            'final': {2},
            'alphabets': {'a', 'b'},
            'states': {1, 2},
            'transitions': {1: {'a': {2}}}
        }
        second = {
            'start': 1,
            'final': {2},
            'alphabets': {'c'},
            'states': {1, 2},
            'transitions': {1: {'c': {2}}}
        }

        a = automata(**first)
        b = automata(**second)
        c = union(a,b)
        print(c)

    def test_concat(self):
        first = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'a', 'b'},
                 'states': {1, 2},
                 'transitions': {1: {'a': {2}}}
        }

        a = automata(**first)
        b = automata(**first)
        c = concat(a, b)
        print(c)

    def test_optional(self):
        first = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'a', 'b'},
                 'states': {1, 2},
                 'transitions': {1: {'a': {2}}}
        }

        a = automata(**first)
        print(optional(a))

    def test_kleene(self):
        first = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'a', 'b'},
                 'states': {1, 2},
                 'transitions': {1: {'a': {2}}}
        }

        a = automata(**first)
        b = kleene(a)
        print(b)
        print(epsilon_closure(b, b.start))

    def test_nfa_to_dfa(self):
        first = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'a'},
                 'states': {1, 2},
                 'transitions': {1: {'a': {2}}}
                 }
        second = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'b'},
                 'states': {1, 2},
                 'transitions': {1: {'b': {2}}}
                 }

        a = automata(**first)
        b = automata(**second)

        c = union(a, b)
        d = kleene(c)
        c = concat(d, a)
        c = concat(c, b)
        c = concat(c, b)
        c = concat(c, d)

        c = dfa(c)
        simplify(c)
        render(c, 'nfa_to_dfa.png')

    def test_remove_unreachable(self):
        first = {'start': 1,
                  'final': SortedSet([2]),
                  'alphabets': {'b'},
                  'states': {1, 2, 3},
                  'transitions': {1: {'b': {2}}, 3: {'b': {2}}}
                  }

        a = automata(**first)
        a = deepcopy(a)
        remove_unreachable_states(a)
        render(a, 'test_remove_unreachable.png')

    def test_minimize(self):
        first = {'start': 1,
                 'final': SortedSet([2]),
                 'alphabets': {'a'},
                 'states': {1, 2},
                 'transitions': {1: {'a': {2}}}
                 }
        second = {'start': 1,
                  'final': SortedSet([2]),
                  'alphabets': {'b'},
                  'states': {1, 2},
                  'transitions': {1: {'b': {2}}}
                  }

        a = automata(**first)
        b = automata(**second)

        c = union(a, b)
        d = kleene(c)
        c = concat(d, a)
        c = concat(c, b)
        c = concat(c, b)
        c = concat(c, d)

        c = dfa(c)

        simplify(c)
        minimize(c)
        simplify(c)

        render(c, 'test_remove_unreachable.png')

if __name__ == '__main__':
    unittest.main()