import json
from collections import deque

from automata.fa.dfa import DFA
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
        elif current == '*':
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

        ans = to_pNFA(shunting(value, data))

        ans.normalize()
        nfa = NFA(
            states=ans.states,
            input_symbols=ans.input_symbols,
            transitions=ans.transitions,
            initial_state=ans.initial_state,
            final_states=ans.final_states
        )

        dfa = DFA.from_nfa(nfa)
        # dfa = dfa.minify()


        states = dfa.states
        transition_states = ['q{}'.format(i) for i in range(len(states))]
        transitions_map = dict(zip(states, transition_states))
        for init_state, inputs in dfa.transitions.items():
            for symbol, next_states in inputs.items():

                dfa.transitions[init_state][symbol] = transitions_map[next_states]

        for init_state in list(dfa.transitions.keys()):
            dfa.transitions[transitions_map[init_state]] = dfa.transitions.pop(init_state)

        dfa.states = set(transition_states)

        dfa.final_states = set([transitions_map[i] for i in dfa.final_states])
        dfa.initial_state = transitions_map[dfa.initial_state]
        dfa = dfa.minify()
        states = dfa.states
        transition_states = ['s{}'.format(i) for i in range(len(states))]
        transitions_map = dict(zip(states, transition_states))
        for init_state, inputs in dfa.transitions.items():
            for symbol, next_states in inputs.items():
                dfa.transitions[init_state][symbol] = transitions_map[next_states]

        for init_state in list(dfa.transitions.keys()):
            dfa.transitions[transitions_map[init_state]] = dfa.transitions.pop(init_state)

        dfa.states = set(transition_states)

        dfa.final_states = set([transitions_map[i] for i in dfa.final_states])
        dfa.initial_state = transitions_map[dfa.initial_state]

        print(dfa.transitions)
        print(dfa.states)
        print(dfa.final_states)
        dfa.show_diagram('{}.png'.format(key))

        yield key, ans

def parse(data):
    languages_pnfa = parse_language(data['LANGUAGE'])

    for key, value in languages_pnfa:

        print()
    #print(parse_language(data['LANGUAGE']))

