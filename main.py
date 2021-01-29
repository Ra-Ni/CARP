import asyncio
from collections import deque
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
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
    table = pNFA('x')
    table2 = pNFA('y')
    #(x|y)xy
    table3 = pNFA.union(table, table2)
    table5 = pNFA.concat(table3, table)
    table5 = pNFA.concat(table5, table2)
    table5.print()
    print(table5.states)
    table5.normalize()
    table5.print()

    print(table5.transitions)
    nfa = NFA(
        states=table5.states,
        input_symbols={'x', 'y'},
        transitions=table5.transitions,
        initial_state=table5.initial_state,
        final_states={table5.final_states}
    )
    print(nfa.accepts_input(''))
    print({table5.final_states})
    print(nfa.validate())
    dfa= DFA.from_nfa(nfa)
    dfa = dfa.minify()
    dfa.show_diagram('test.png')
    #table4 = NFA.union(table2, table3)
    #table5 = NFA.kleene_star(table4)
    # table6 = table.clone()
    # table.print()
    # table2.print()
    # table6.print()
    #table3.print()
    #table4.print()
    #table5.print()