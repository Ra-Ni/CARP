from sortedcontainers import SortedSet
from base.fa import fa, generate_uid


class nfa(fa):
    def __init__(self, symbol: str = None, label: str = None):
        super().__init__(label)
        self.final_states.add(generate_uid() if symbol else self.initial_state)
        self.transitions = {self.initial_state: {symbol: self.final_states.copy()} if symbol else {}}

    def union(self, other, overwrite=True):
        self.transitions.update(other.transitions)
        self.final_states.update(other.final_states)
        self.states.update(other.states)

        new_final_state = generate_uid()
        new_initial_state = generate_uid()
        self.states.update([new_final_state, new_initial_state])

        self.transitions[new_final_state] = {}
        self.transitions[new_initial_state] = {'': SortedSet([self.initial_state, other.initial_state])}

        for final_state in self.final_states:
            self.transitions[final_state]\
                .setdefault('', SortedSet())\
                .add(new_final_state)

        if overwrite:
            del other

    def concat(self, other, overwrite=True):
        self.transitions.update(other.transitions)
        self.states.update(other.states)

        for final_state in self.final_states:
            self.transitions[final_state].setdefault('', SortedSet()).add(other.initial_state)

        self.final_states.clear()
        self.final_states.update(other.final_states)

        if overwrite:
            del other

    def kleene(self):
        new_initial_state = generate_uid()
        new_final_state = generate_uid()

        self.transitions[new_initial_state] = {'': SortedSet([self.initial_state, new_final_state])}
        self.transitions[new_final_state] = {}

        for final_state in self.final_states:
            self.transitions[final_state]\
                .setdefault('', SortedSet()) \
                .update(SortedSet([self.initial_state, new_final_state]))

        self.final_states.clear()
        self.final_states.add(new_final_state)
        self.initial_state = new_initial_state
        self.states.update([new_final_state, new_initial_state])

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


