import unittest

from my_automata.regex import *

class TestStringMethods(unittest.TestCase):

    def test_scan(self):
        path = '../examples/lexpositivegrading.src'
        output = ''
        scanner = scan(path)
        prev_line = 1
        for inp in scanner:

            if inp.location != prev_line:
                prev_line = inp.location
                output += '\n'
            else:
                output += ' '
            output = output + str(inp)


        with open('output.txt', 'w') as outwrite:
            outwrite.write(output)


if __name__ == '__main__':
    unittest.main()