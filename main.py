import asyncio
from collections import deque

from automata.base.exceptions import RejectionException
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from fileparser import reader, parse
from node import *



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mode = 'id'
    query = 'abc1'

    config = reader()
    ref = parse(config)
    dfa = ref[mode]

    print('Accepts input \"{}\"? {}'.format(query, dfa.accepts_input(query)))
    print('Accept states: {}'.format(str(dfa.final_states)))
    try:
        for answer in dfa.read_input_stepwise(query):
            print(answer)

    except RejectionException:
        print("Rejected")

        #table4 = NFA.union(table2, table3)
    #table5 = NFA.kleene_star(table4)
    # table6 = table.clone()
    # table.print()
    # table2.print()
    # table6.print()
    #table3.print()
    #table4.print()
    #table5.print()