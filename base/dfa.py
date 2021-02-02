import itertools
from ast import literal_eval

from sortedcontainers import SortedSet

from base.fa import fa, generate_uid
from base.nfa import nfa


class dfa(fa):

    def __init__(self):
        super().__init__()

    # todo Needs works
    def minimize(self):
        raise NotImplementedError
        # marked = set()
        # unmarked = set()
        # prev_unmarked = set()
        #
        # for entry in itertools.combinations(self.transitions.keys(), 2):
        #     first, second = entry
        #     if first in self.final_states or second in self.final_states:
        #         marked.add(str(entry))
        #     else:
        #         unmarked.add(str(entry))
        #
        # while unmarked != prev_unmarked:
        #     prev_unmarked = unmarked.copy()
        #
        #     for state in unmarked:
        #         first, second = eval(state)
        #         custom_dict = self.transitions[first].copy()
        #         custom_dict.update(self.transitions[second])
        #         stop = False
        #
        #         for symbol, next_state in custom_dict.items():
        #             if symbol not in self.transitions[first] or self.transitions[first][symbol] != next_state:
        #                 unmarked.remove(state)
        #                 marked.add(state)
        #                 stop = True
        #                 break
        #
        #         if stop:
        #             break
        # print(unmarked)
        # if unmarked:
        #     replacement_map = {}
        #     for resp in unmarked:
        #         first, second = eval(resp)
        #         replacement_map.setdefault(first, set()).add(second)
        #
        #     replacement_map = dict(sorted(replacement_map.items(), reverse=True))
        #
        #     for state in list(self.transitions.keys()):
        #         if state in replacement_map:
        #
        #     for state in list(self.transitions.keys()):
        #         transition = self.transitions[state]
        #         if state in unmarked:
        #             self.transitions.pop(state)
        #         else:
        #             for symbol, next_state in transition.items():
        #                 if next_state in unmarked:
        #                     self.transitions[state][symbol] = original

    def rehash(self, simplified: bool = False):
        if not simplified:
            uuid_map = {uid: generate_uid() for uid in self.transitions.keys()}
        else:
            keys = list(self.states)
            n = len(keys)
            uuid_map = {keys[uid]: f'S{uid}' for uid in range(n)}

        for state in self.states:
            transition = self.transitions[state]
            for symbol, next_states in transition.items():
                self.transitions[state][symbol] = uuid_map[next_states]
            self.transitions[uuid_map[state]] = self.transitions.pop(state)

        self.final_states = SortedSet([uuid_map[uid] for uid in self.final_states])
        self.initial_state = uuid_map[self.initial_state]
        self.states = set(list(self.transitions.keys()))

    @classmethod
    def from_NFA(cls, nfa: nfa):
        dfa = cls()

        def _epsilon_closure(*states):
            _stack = [*states]
            _visited = SortedSet()
            _acceptable = False

            while _stack:
                _state = _stack.pop()

                if _state not in _visited:
                    _visited.add(_state)

                    if not _acceptable and _state in nfa.final_states:
                        _acceptable = True

                    if '' in nfa.transitions[_state]:
                        _stack.extend(nfa.transitions[_state][''])

            return _visited, _acceptable

        def _next_state_iterator(states: str) -> (str, str, bool):
            _states = eval(states)
            _transitions = {}

            for _state in _states:
                for _symbol, _next_states in nfa.transitions[_state].items():
                    if _symbol != '':
                        _transitions.setdefault(_symbol, SortedSet()).update(_next_states)

            for _symbol in list(_transitions.keys()):
                _state, is_final = _epsilon_closure(*_transitions.pop(_symbol))
                yield _symbol, str(_state), is_final

        dfa.initial_state, accept = _epsilon_closure(nfa.initial_state)
        dfa.initial_state = str(dfa.initial_state)
        dfa.states.add(dfa.initial_state)

        if accept:
            dfa.final_states.add(dfa.initial_state)
        stack = [dfa.initial_state]

        while stack:
            current_state = stack.pop()
            for symbol, next_state, acceptable in _next_state_iterator(current_state):
                if next_state not in dfa.states:
                    stack.append(next_state)
                    dfa.states.add(next_state)
                    if acceptable:
                        dfa.final_states.add(next_state)

                dfa.transitions \
                    .setdefault(current_state, {}) \
                    .setdefault(symbol, next_state)

        return dfa
