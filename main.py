import asyncio
from collections import deque
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
from fileparser import reader, parse
from node import *



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    table = pNFA('x')
    table2 = pNFA('y')
    #(x|y)xy
    table3 = pNFA.union(table, table2)
    table3.print()
    table5 = pNFA.concat(table3, table)
    table5.print()
    table5 = pNFA.concat(table5, table2)

    table5.print()

    table5.normalize()
    table5.print()


    config = reader()
    parse(config)
    #table4 = NFA.union(table2, table3)
    #table5 = NFA.kleene_star(table4)
    # table6 = table.clone()
    # table.print()
    # table2.print()
    # table6.print()
    #table3.print()
    #table4.print()
    #table5.print()