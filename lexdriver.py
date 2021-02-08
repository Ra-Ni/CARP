import os
from collections import deque
import sys
from lex import scanner

def help(exception: Exception = None):
    print(
"""lexdriver.py <file> [config]

    <file>:
        Source code file ending with the extension .src
    [config]:
        Segment of program containing the tokens and regular expressions
        
        Must contain variables "reserved" and "tokens", where:
            type(reserved) -> list(str(phrase))
            type(tokens) -> list(tuple(str(id), str(regex))\n""")

    if exception:
        print(exception)

    exit(0)


if __name__ == '__main__':
    args = len(sys.argv)
    prev_line = 1

    path = sys.argv[1] if args >= 2 else 'examples/lexnegativegrading.src'
    config = sys.argv[2] if args >= 3 else 'config'
    lex_errors = ''
    try:
        with open(path, 'r') as fstream:
            data = fstream.read()

        output_path, _ = os.path.splitext(path)
        s = scanner(config)
        tokens = deque(list(s.read(data)))
        lex_errors = f'{output_path}.outlexerrors'
        lex_tokens = f'{output_path}.outlextokens'

        with open(lex_errors, 'w') as errors:
            with open(lex_tokens, 'w') as output:
                while tokens:
                    tok = tokens.popleft()
                    fill_char = ' ' if prev_line == tok.location else '\n'
                    prev_line = tok.location

                    if tok.type == 'invalidchar':
                        errors.write('Lexical error: Invalid character: "{}": line {}.\n'
                                     .format(tok.lexeme, tok.location))

                    output.write(fill_char + str(tok))

        print(f'Results stored in:\n\t{lex_tokens}\n\t{lex_errors}')
    except Exception as err:
        help(err)
