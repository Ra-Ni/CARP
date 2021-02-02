from lexer import nfa
from lexer import dfa

# Press the green button in the gutter to run the script.
from lexer.generator import generator

if __name__ == '__main__':

    second = nfa()
    second.transitions = {
        '0': {'a':{'1'},'b':{'2'}},
        '1': {'a':{'1'},'b':{'3'}},
        '2': {'a':{'1'},'b':{'2'}},
        '3': {'a':{'1'},'b':{'4'}},
        '4': {}
    }
    second.states = {'0','1', '2', '3', '4'}
    second.initial_state = '0'
    second.final_states = {'4'}

    third = nfa()
    third.transitions = {
        'A': {'a': {'B'}, 'b': {'C'}},
        'B': {'a': {'B'}, 'b': {'D'}},
        'C': {'a': {'B'}, 'b': {'C'}},
        'D': {'a': {'B'}, 'b': {'E'}},
        'E': {}
    }
    third.initial_state = 'A'
    third.final_states = {'E'}
    third.states = {'A', 'B', 'C', 'D', 'E'}

    nfa.kleene(second)
    # second = dfa.from_NFA(second)
    # second.rehash(True)

    second.show('img/ex.png')
    second = second.copy()
    # second = dfa.from_NFA(second)
    # second.rehash(True)

    second.show('img/ex2.png')
    print(second)

    gen = generator()
    gen.load('test')
    gen.exec()