from sortedcontainers import SortedSet
from .fa import fa, generate_uid


class nfa(fa):
    def __init__(self, symbol: str = None, label: str = None):
        super().__init__(label)
        self.transitions = {self.initial_state: {}}

        if not symbol:
            self.final_states.add(self.initial_state)
        else:
            final_state = generate_uid()
            self.final_states.add(final_state)
            self.transitions[self.initial_state][symbol] = self.final_states.copy()
            self.transitions[final_state] = {}
        self.states.update(self.final_states)


    @classmethod
    def from_dfa(cls, dfa):
        newNFA = cls()
        newNFA.transitions.clear()
        newNFA.initial_state = dfa.initial_state
        newNFA.final_states = dfa.final_states.copy()
        newNFA.states = dfa.states.copy()
        newNFA.label = dfa.label

        for state in dfa.states:
            transition = dfa.transitions[state]
            for symbol, next_state in transition.items():
                newNFA.transitions\
                    .setdefault(state, {})\
                    .setdefault(symbol, SortedSet())\
                    .add(next_state)
        return newNFA

    @classmethod
    def union(cls, x, y):
        other = y.copy()
        newNFA = x.copy()

        newNFA.transitions.update(other.transitions)
        newNFA.final_states.update(other.final_states)
        newNFA.states.update(other.states)

        new_final_state = generate_uid()
        new_initial_state = generate_uid()
        newNFA.states.update([new_final_state, new_initial_state])

        newNFA.transitions[new_final_state] = {}
        newNFA.transitions[new_initial_state] = {'': SortedSet([newNFA.initial_state, other.initial_state])}

        for final_state in newNFA.final_states:
            newNFA.transitions[final_state]\
                .setdefault('', SortedSet())\
                .add(new_final_state)

        newNFA.final_states = SortedSet([new_final_state])
        return newNFA

    @classmethod
    def concat(cls, x, y):
        other = y.copy()
        newNFA = x.copy()
        newNFA.transitions.update(other.transitions)
        newNFA.states.update(other.states)

        for final_state in newNFA.final_states:
            newNFA.transitions[final_state].setdefault('', SortedSet()).add(other.initial_state)

        newNFA.final_states.clear()
        newNFA.final_states.update(other.final_states)
        return newNFA

    @classmethod
    def kleene(cls, x):
        newNFA = x.copy()
        new_initial_state = generate_uid()
        new_final_state = generate_uid()

        newNFA.transitions[new_initial_state] = {'': SortedSet([newNFA.initial_state, new_final_state])}
        newNFA.transitions[new_final_state] = {}

        for final_state in newNFA.final_states:
            newNFA.transitions[final_state]\
                .setdefault('', SortedSet()) \
                .update(SortedSet([newNFA.initial_state, new_final_state]))

        newNFA.final_states.clear()
        newNFA.final_states.add(new_final_state)
        newNFA.initial_state = new_initial_state
        newNFA.states.update([new_final_state, new_initial_state])
        return newNFA

    @classmethod
    def optional(cls, x):
        newNFA = x.copy()
        new_initial_state = generate_uid()
        new_final_state = generate_uid()

        for final_state in newNFA.final_states:
            newNFA.transitions[final_state] = {'': SortedSet([new_final_state])}

        newNFA.transitions[new_initial_state] = {'': SortedSet([newNFA.initial_state, new_final_state])}
        newNFA.initial_state = new_initial_state
        newNFA.final_states = SortedSet([new_final_state])
        newNFA.states.update([new_initial_state, new_final_state])

        return newNFA

    # def __minimum_dfa(self):
    #     k = 0
    #     P_k = {str(self.final_states)}
    #     non_final_states = set(list(self.transitions.keys())).difference(self.final_states)
    #     if non_final_states:
    #         P_k.update(str(non_final_states))
    #
    #     P_k_next = set()
    #
    #     while P_k != P_k_next:
    #         for state in P_k:
    #             state_set = literal_eval(state)
    #
    #             for first, second in combinations(state_set, 2):
    #                 first_dict = self.transitions[first]
    #                 second_dict = self.transitions[second]
    #                 inputs = set(second_dict.keys()).union(set(first_dict.keys()))
    #                 indistinguishable = all({k in second_dict and k in first_dict and second_dict[k] == first_dict[k]
    #                          for k in inputs})
    #                 if not indistinguishable:
    #                     P_k_next.add(str(set(first)))
    #                     P_k_next.add(str(set(second)))
    #                     P_k -= first
    #                     P_k -= second
    #                 else:
    #


