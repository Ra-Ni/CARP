import json
from collections import deque
from codecs import decode
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from node import pNFA

language = {
    '*': 0,
    '?': 0,
    ' ': 1,
    '|': 2,
    '\\': 3,
    '[': 4,
    ']': 4,
    '(': 4,
    ')': 4,
}

escape_codes = {
    '\\s': ' ',
}


def reader():
    with open('config') as json_file:
        data = json.load(json_file)

        return data


def shunting(text, reference):
    operations = []
    output = deque()
    tokens = deque(text)

    while tokens:
        token = tokens.popleft()

        if token not in language:
            if type(token) is pNFA:
                output.append(token)
            else:

                while tokens and tokens[0] not in language and type(tokens[0]) is not pNFA:
                    token += tokens.popleft()
                if token in reference:
                    if type(reference[token]) is not pNFA:
                        tokens.extendleft(reversed(list(reference[token])))
                    else:
                        output.append(reference[token])
                else:
                    output.append(token)

        elif token == "\\" and tokens:
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
            operation_complete = False
            while operations and not operation_complete:
                operation_priority = language[operations[-1]]
                if token_priority >= operation_priority:
                    output.append(operations.pop())
                else:
                    operation_complete = True
            operations.append(token)

    while operations:
        output.append(operations.pop())

    return output


def to_pNFA(result: deque):
    stack = list()

    while result:
        current = result.popleft()
        if current not in language:
            if type(current) is pNFA:
                stack.append(current)
            else:
                if current in escape_codes:
                    current = escape_codes[current]
                stack.append(pNFA(current))
        elif current == '*':
            stack.append(pNFA.kleene_star(stack.pop()))
        elif current == ' ':
            second, first = stack.pop(), stack.pop()
            stack.append(pNFA.concat(first, second))
        elif current == '|':
            stack.append(pNFA.union(stack.pop(), stack.pop()))
        elif current == '?':
            stack.append(pNFA.option(stack.pop()))
    if len(stack) != 1:
        print("Stack not eq to 1 in to_pNFA")

    final = stack.pop()

    return final


def parse(data):
    reference = data['LANGUAGE']
    language_dfas = {}
    for key, value in reference.items():
        ans = to_pNFA(shunting(value, reference))
        # ans.normalize()
        language_dfas[key] = ans

    reference = data['TOKEN'].copy()
    reference.update(language_dfas)
    for key, value in data['TOKEN'].items():
        ans = shunting(value, reference)

        ans = to_pNFA(ans)
        reference[key] = ans


    output = [reference[i] for i in data['TOKEN'].keys()]
    while len(output) >= 2:
        output.append(pNFA.union(output.pop(), output.pop()))
    reference['total'] = output.pop()


    for key, ans in reference.items():

        nfa = NFA(
            states=ans.states,
            input_symbols=ans.input_symbols,
            transitions=ans.transitions,
            initial_state=ans.initial_state,
            final_states=ans.final_states
        )

        dfa = DFA.from_nfa(nfa)
        dfa.simplify('q')
        dfa = dfa.minify()
        dfa.simplify('s')
        reference[key] = dfa

        dfa.show_diagram('img/{}.png'.format(key))
    return reference