import json
from collections import deque

from automata.fa.nfa import NFA
from node import pNFA

language = {
    '\\': 1,
    '[': 2,
    ']': 2,
    '(': 3,
    ')': 3,
    '*': 4,
    '?': 4,
    '-': 5,
    ' ': 5,
    '|': 7}

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
            while tokens and tokens[0] not in language:
                token += tokens.popleft()
            if token in reference:

                tokens.extendleft(reversed(list(reference[token])))
            else:
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


def to_pNFA(result: deque):
    stack = list()

    while result:
        current = result.popleft()
        if current not in language:
            stack.append(pNFA(current))
        if current == '*':
            stack.append(pNFA.kleene_star(stack.pop()))
        elif current == ' ':
            stack.append(pNFA.concat(stack.pop(), stack.pop()))
        elif current == '|':
            stack.append(pNFA.union(stack.pop(), stack.pop()))

    if len(stack) != 1:
        print("Stack not eq to 1 in to_pNFA")

    final = stack.pop()


    return final

def parse_language(data):
    for key, value in data.items():
        print(key)
        ans = to_pNFA(shunting(value, data))
        ans.print()
        ans.normalize()

        yield key, ans

def parse(data):
    languages_pnfa = parse_language(data['LANGUAGE'])
    for key, value in languages_pnfa:
        value.print()
        print()
    #print(parse_language(data['LANGUAGE']))

