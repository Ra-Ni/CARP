import asyncio
from collections import deque

from node import *


def shunting(text):
    operations = []
    output = deque()

    tokens = deque(text)
    language = {
        '\\': 1,
        '[': 2,
        ']': 2,
        '(': 3,
        ')': 3,
        '*': 4,
        '?': 4,
        ' ': 5,
        '|': 7}

    while tokens:
        token = tokens.popleft()

        if token not in language:
            while tokens and tokens[0] not in language:
                token += tokens.popleft()
            output.append(token)

        elif token == '\\' and tokens:
            token += tokens.popleft()
            output.append(token)

        elif token == '(' or token == '[':
            operations.append(token)

        elif token == ')' or token == ']':
            target_token = '(' if token == ')' else '['
            found = False
            while operations and not found:
                operation = operations.pop()
                if operation == target_token:
                    found = True
                else:
                    output.append(operation)
            if token == ']':
                output.append('?')
            # todo if found, if not found

        else:
            token_priority = language[token]

            if not operations:
                op_priority = -1
            else:
                op_priority = language[operations[-1]]

            if token_priority <= op_priority:
                output.append(token)
            else:
                operations.append(token)

    while operations:
        output.append(operations.pop())

    return output


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    table = NFA('x')
    table2 = NFA('y')
    tabl4 = table.clone()
    table3 = NFA.union(table.clone(), table2.clone())
    table5 = NFA.concat(table3.clone(), table.clone())

    table5.print()
    s = table5.eclosure(table5.start)
    print(s)
    d = table5.traverse(s)
    print(d)


    #table4 = NFA.union(table2, table3)
    #table5 = NFA.kleene_star(table4)
    # table6 = table.clone()
    # table.print()
    # table2.print()
    # table6.print()
    #table3.print()
    #table4.print()
    #table5.print()