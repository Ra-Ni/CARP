import uuid
from collections import deque

from automata.fa.nfa import NFA


class pNFA:
    def __init__(self, token=''):
        final_state = str(uuid.uuid4())

        self.initial_state = str(uuid.uuid4())
        self.final_states = {final_state}
        self.states = self.final_states.union({self.initial_state})
        self.input_symbols = set() if token == '' else {token}
        self.transitions = {self.initial_state: {token: self.final_states.copy()},
                            final_state: {}}

    def print(self):
        print("Start: {}\nFinal: {}\n".format(self.initial_state, self.final_states))
        for k, v in self.transitions.items():
            print('{}: {}'.format(k, v))
        print()

    def copy(self):

        uuid_map = {}
        transitions = {}
        for initial_state, inputs in self.transitions.items():
            new_initial_state = uuid_map.setdefault(initial_state, str(uuid.uuid4()))
            if not inputs:
                input_set = transitions.setdefault(new_initial_state, {}).setdefault('', set())
                transitions[new_initial_state][''] = input_set
            else:
                for symbol, next_states in inputs.items():
                    input_set = transitions.setdefault(new_initial_state, {}).setdefault(symbol, set())

                    new_next_states = {uuid_map.setdefault(next_state, str(uuid.uuid4())) for next_state in next_states}
                    input_set.update(new_next_states)
                    transitions[new_initial_state][symbol] = input_set

        backup = pNFA()
        backup.transitions = transitions
        backup.initial_state = uuid_map[self.initial_state]
        backup.final_states = {uuid_map[final_state] for final_state in self.final_states}
        backup.input_symbols = self.input_symbols
        backup.states = set(list(backup.transitions.keys()))
        return backup

    def normalize(self):
        transition_states = ['q{}'.format(i) for i in range(len(self.states))]
        transitions_map = dict(zip(self.states, transition_states))
        new_transitions = {}

        for initial_state, inputs in self.transitions.items():
            new_inputs = new_transitions.setdefault(initial_state, {})
            for symbol, next_states in inputs.items():
                buffer = [transitions_map[i] for i in next_states]

                buffer = set(buffer)
                self.transitions[initial_state][symbol] = buffer


        for key in list(self.transitions.keys()):
            self.transitions[transitions_map[key]] = self.transitions.pop(key)

        self.final_states = {transitions_map[i] for i in self.final_states}
        self.initial_state = transitions_map[self.initial_state]
        self.states = set(transition_states)


    @classmethod
    def concat(cls, x, y):
        new_NFA = cls()
        u, v = x.copy(), y.copy()

        # update new_NFA to contain the transitions for both u and v
        new_NFA.transitions.update(u.transitions)
        new_NFA.transitions.update(v.transitions)

        # the final states of u point to the initial state of v
        for final_state in u.final_states:
            new_NFA.transitions[final_state][''] = {v.initial_state}

        # the final states of v point to the final state of new_NFA
        for final_state in v.final_states:
            input_set = new_NFA.transitions[final_state].setdefault('', set())
            input_set.update(new_NFA.final_states)
            new_NFA.transitions[final_state][''] = input_set

        # the initial state of new_NFA points to the initial state of u
        new_NFA.transitions[new_NFA.initial_state][''] = {u.initial_state}

        # the states of new_NFA are updated
        new_NFA.states = set(list(new_NFA.transitions.keys()))

        # the input symbols are unionized
        new_NFA.input_symbols = u.input_symbols.union(v.input_symbols)

        return new_NFA

    @classmethod
    def union(cls, x, y):
        new_NFA = cls()
        u, v = x.copy(), y.copy()

        # update the transitions table for the new_NFA
        new_NFA.transitions.update(u.transitions)
        new_NFA.transitions.update(v.transitions)

        # the final states of u and v are now the final states of new_NFA
        final_states = u.final_states.union(v.final_states)
        for final_state in final_states:
            input_set = new_NFA.transitions[final_state].setdefault('', set())
            input_set.update(new_NFA.final_states)
            new_NFA.transitions[final_state][''] = input_set

        # the initial states of u and v are now the initial state of new_NFA
        new_NFA.transitions[new_NFA.initial_state][''] = {u.initial_state, v.initial_state}

        # the states of new_NFA are its keys
        new_NFA.states = set(list(new_NFA.transitions.keys()))

        # the input symbols of new_NFA is union of u and v
        new_NFA.input_symbols = u.input_symbols.union(v.input_symbols)

        return new_NFA

    @classmethod
    def kleene_star(cls, x):
        new_NFA = cls()
        u = x.copy()

        # merge u into the new nfa
        new_NFA.transitions.update(u.transitions)

        # the final state in u is now the final state in new_NFA
        # AND the final states point back to u's initial state
        for final_state in u.final_states:
            input_set = new_NFA.transitions[final_state].setdefault('', set())
            input_set.update(new_NFA.final_states)
            input_set.add(u.initial_state)
            new_NFA.transitions[final_state][''] = input_set

        # the initial state of new_nfa points to its final states
        # AND to u's initial state
        input_set = new_NFA.transitions[new_NFA.initial_state]['']
        input_set.update(new_NFA.final_states)
        input_set.add(u.initial_state)
        new_NFA.transitions[new_NFA.initial_state][''] = input_set

        # update the states available for new_NFA
        new_NFA.states = set(list(new_NFA.transitions.keys()))

        # update the input symbols for new_NFA
        new_NFA.input_symbols.update(u.input_symbols)

        return new_NFA

    @classmethod
    def option(cls, x):
        new_NFA = cls()
        u = x.copy()


        # merge u into the new nfa
        new_NFA.transitions.update(u.transitions)

        # the final state in u is now the final state in new_NFA
        for final_state in u.final_states:
            input_set = new_NFA.transitions[final_state].setdefault('', set())
            input_set.update(new_NFA.final_states)
            new_NFA.transitions[final_state][''] = input_set

        # the initial state of new_nfa points to its final states
        # AND to u's initial state
        input_set = new_NFA.transitions[new_NFA.initial_state]['']
        input_set.update(new_NFA.final_states)
        input_set.add(u.initial_state)
        new_NFA.transitions[new_NFA.initial_state][''] = input_set

        # update the states available for new_NFA
        new_NFA.states = set(list(new_NFA.transitions.keys()))

        # update the input symbols for new_NFA
        new_NFA.input_symbols.update(u.input_symbols)

        return new_NFA

    @classmethod
    def from_dfa(cls, x: NFA):
        new_NFA = cls()

        for init_state, inputs in x.transitions.items():
            for symbol, next_state in inputs.items():
                input_set = new_NFA.transitions.setdefault(init_state, {})
                input_set = input_set.setdefault(symbol, set())
                input_set.add(next_state)
                new_NFA.transitions[init_state][symbol] = input_set
        new_NFA.states = x.states.copy()
        new_NFA.input_symbols = x.input_symbols.copy()
        new_NFA.final_states = x.final_states.copy()
        new_NFA.initial_state = x.initial_state

        return new_NFA