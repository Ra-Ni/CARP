import asyncio
from collections import deque

from automata.base.exceptions import RejectionException
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from base.fDFA import fDFA
from base.fNFA import fNFA
from fileparser import reader, parse
from node import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    second = fNFA()
    second.transitions = {
        '0': {'a':{'1'},'b':{'2'}},
        '1': {'a':{'1'},'b':{'3'}},
        '2': {'a':{'1'},'b':{'2'}},
        '3': {'a':{'1'},'b':{'4'}},
        '4': {'a':{'1'},'b':{'2'}}
    }
    second.states = {'0','1', '2', '3', '4'}
    second.initial_state = '0'
    second.final_states = {'4'}

    third = fNFA()
    third.transitions = {
        'A': {'a': {'B'}, 'b': {'C'}},
        'B': {'a': {'B'}, 'b': {'D'}},
        'C': {'a': {'B'}, 'b': {'C'}},
        'D': {'a': {'B'}, 'b': {'E'}},
        'E': {'a': {'B'}, 'b': {'C'}}
    }
    third.initial_state = 'A'
    third.final_states = {'E'}
    third.states = {'A', 'B', 'C', 'D', 'E'}

    second.union(third)
    second.show_diagram('img/ex.png')
