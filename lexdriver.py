import re
from collections import deque

from my_automata.regex import scan

if __name__ == '__main__':

    path = 'examples/lexnegativegrading.src'
    output_path = re.sub(r'(?!\.)src$', '', path)
    tokens = deque()

    prev_line = 1
    for inp in scan(path):
        tokens.append(inp)

    with open(f'{output_path}outlexerrors', 'w') as errors:
        with open(f'{output_path}outlextokens', 'w') as output:
            prev_line = 1
            while tokens:
                tok = tokens.popleft()
                fill_char = ' ' if prev_line == tok.location else '\n'
                prev_line = tok.location

                if tok.lexeme == 'invalidchar':
                    errors.write(str(tok) + '\n')

                output.write(fill_char + str(tok))
