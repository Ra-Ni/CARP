import uuid
from collections import deque


class pNFA:
    def __init__(self, token=None):
        self.initial_state = str(uuid.uuid4())
        self.final_states = str(uuid.uuid4())
        self.states = set()
        self.transitions = {}
        if token:
            self.transitions[self.initial_state] = {token: {self.final_states}}

    def print(self):
        print("Start: {}\nFinal: {}\n".format(self.initial_state, self.final_states))
        for k, v in self.transitions.items():
            print('{}: {}'.format(k, v))
        print()

    def clone(self):
        backup = pNFA()
        uuid_map = {self.initial_state: backup.initial_state,
                    self.final_states: backup.final_states}

        for k, v in self.transitions.items():
            new_key = uuid_map.setdefault(k, str(uuid.uuid4()))
            entry = backup.transitions.setdefault(new_key, {})

            for kk, sublist in v.items():
                sub_entry = entry.setdefault(kk, set())
                for item in sublist:
                    new_uuid = uuid_map.setdefault(item, str(uuid.uuid4()))
                    sub_entry.add(new_uuid)

        return backup

    def normalize(self):
        num_transitions = len(self.states)
        transition_states = ['q{}'.format(i) for i in range(num_transitions)]
        transitions_map = dict(zip(self.states, transition_states))
        transitions_map[self.final_states] = 'q{}'.format(num_transitions)

        for state, sub_dict in self.transitions.items():
            for input, next_state in sub_dict.items():
                buffer = list(next_state)
                buffer = [transitions_map[buffer[i]] for i in range(len(buffer))]
                self.transitions[state][input] = set(buffer)

        for key in list(self.transitions.keys()):
            self.transitions[transitions_map[key]] = self.transitions.pop(key)

        self.final_states = transitions_map[self.final_states]
        self.initial_state = transitions_map[self.initial_state]
        self.states = {transitions_map[i] for i in self.states}
        final_state = 'q{}'.format(num_transitions)
        self.states.add(final_state)
        self.transitions[final_state] = {}





    @classmethod
    def concat(cls, x, y):
        new_NFA = cls()
        u, v = x.clone(), y.clone()
        new_NFA.transitions.update(u.transitions)
        new_NFA.transitions.update(v.transitions)
        u_final = new_NFA.transitions.setdefault(u.final_states, {})
        v_final = new_NFA.transitions.setdefault(v.final_states, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.initial_state, {})
        u_final[''] = {v.initial_state}
        table_start[''] = {u.initial_state}
        v_final[''] = {new_NFA.final_states}
        new_NFA.states = set(new_NFA.transitions.keys())
        return new_NFA

    @classmethod
    def union(cls, x, y):
        new_NFA = cls()
        u, v = x.clone(), y.clone()
        new_NFA.transitions.update(u.transitions)
        new_NFA.transitions.update(v.transitions)
        u_final = new_NFA.transitions.setdefault(u.final_states, {})
        v_final = new_NFA.transitions.setdefault(v.final_states, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.initial_state, {})
        u_final[''] = {new_NFA.final_states}
        table_start[''] = {u.initial_state, v.initial_state}
        v_final[''] = {new_NFA.final_states}
        new_NFA.states = set(new_NFA.transitions.keys())
        return new_NFA

    @classmethod
    def kleene_star(cls, x):
        new_NFA = cls()
        u = x.clone()
        new_NFA.transitions.update(u.transitions)
        x_final = new_NFA.transitions.setdefault(u.final_states, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.initial_state, {})
        x_final = x_final.setdefault('', set())
        table_start = table_start.setdefault('', set())
        x_final.add(u.initial_state)
        x_final.add(new_NFA.final_states)
        table_start.add(u.initial_state)
        table_start.add(new_NFA.final_states)
        new_NFA.states = set(new_NFA.transitions.keys())
        return new_NFA
