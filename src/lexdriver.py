import os
import sys
from pathlib import Path

from lex import *

EXAMPLE = '../examples/lexnegativegrading.src'
OUT_ERRORS = '.outlexerrors'
OUT_DERIVATIONS = '.outlextokens'


def help(exception: Exception = None):
    print(
        """lexdriver.py <file>

    <file>:
        Source code file ending with the extension .src\n""")

    if exception:
        print(exception)

    exit(0)


if __name__ == '__main__':
    prev_line = 1
    path = Path(sys.argv[1] if len(sys.argv) >= 2 else EXAMPLE)

    try:
        out = str(path.parent) + '\\' + str(path.stem)
        output_path, _ = os.path.splitext(path)
        out_errors = Path(out + OUT_ERRORS)
        out_derivations = Path(out + OUT_DERIVATIONS)

        with open(path, 'r') as fstream:
            data = fstream.read()

        s = Scanner.load(src_file=path)

        with open(out_errors, 'w') as errors:
            with open(out_derivations, 'w') as output:
                for token in iter(s):

                    fill_char = ' ' if prev_line == token.location else '\n'
                    prev_line = token.location

                    if token.type == 'invalidchar':
                        errors.write('Lexical error: Invalid character: "{}": line {}.\n'
                                     .format(token.lexeme, token.location))

                    output.write(fill_char + str(token))

        print(f'Results stored in:\n\t{out_derivations}\n\t{out_errors}')
    except Exception as err:
        help(err)
