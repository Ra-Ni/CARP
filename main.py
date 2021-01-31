import asyncio
from collections import deque

from automata.base.exceptions import RejectionException
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from base.Automaton import Automaton
from fileparser import reader, parse
from node import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    first = Automaton()
    first.transitions = {
                         'A': {'0': {'B', 'C'}, '1': {'A'}, '': {'B'}},
                         'B': {'1': {'B'}, '': {'C'}},
                         'C': {'0': {'C'}, '1': {'C'}}
                         }
    first.initial_state = 'A'
    first.final_states = {'C'}
    first.minify(True)
    print(first)
    print(first.accepts('00'))
    print(first.accepts('-12'))
    for i,j in first.walk('011'):
        print(i, j)
    # mode = 'total'
    # query = {'12.1', 'if', 'else', 'then'}
    #
    # config = reader()
    # ref = parse(config)
    # dfa = ref[mode]
    #
    # for q in query:
    #     print('Accepts input \"{}\"? {}'.format(q, dfa.accepts_input(q)))
        # print('Accept states: {}'.format(str(dfa.final_states)))
        # try:
        #     for answer in dfa.read_input_stepwise(query):
        #         print(answer)
        #
        # except RejectionException:
        #     print("Rejected")

        #table4 = NFA.union(table2, table3)
    #table5 = NFA.kleene_star(table4)
    # table6 = table.clone()
    # table.print()
    # table2.print()
    # table6.print()
    #table3.print()
    #table4.print()
    #table5.print()