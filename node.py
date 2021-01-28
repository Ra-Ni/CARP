import uuid
from collections import deque


class NFA:
    def __init__(self, token=None):
        self.start = str(uuid.uuid4())
        self.final = str(uuid.uuid4())
        self.transitions = {}
        if token:
            self.transitions[self.start] = {token: {self.final}}

    def print(self):
        print("Start: {}\nFinal: {}\n".format(self.start, self.final))
        for k, v in self.transitions.items():
            print('{}: {}'.format(k, v))
        print()

    def clone(self):
        backup = NFA()
        uuid_map = {self.start: backup.start,
                    self.final: backup.final}

        for k, v in self.transitions.items():
            new_key = uuid_map.setdefault(k, str(uuid.uuid4()))
            entry = backup.transitions.setdefault(new_key, {})

            for kk, sublist in v.items():
                sub_entry = entry.setdefault(kk, set())
                for item in sublist:
                    new_uuid = uuid_map.setdefault(item, str(uuid.uuid4()))
                    sub_entry.add(new_uuid)

        return backup

    def eclosure(self, entry):
        path = deque([entry])
        closure = []
        while path:
            entry = path.popleft()
            if entry in self.transitions:
                closure.append(entry)
                inputs = self.transitions[entry]
                if None in inputs:
                    path.extend(inputs[None])

        return closure

    def traverse(self, closure_set):
        union_inputs = {}
        for state in closure_set:
            for k, v in self.transitions[state].items():
                input = union_inputs.setdefault(k, set())
                union_inputs[k] = input.union(v)

        del union_inputs['']
        for k, v in union_inputs.items():
            union_inputs[k] = list(v)
        return union_inputs

    def finals(self):

        return NotImplementedError


    @classmethod
    def concat(cls, x, y):
        new_NFA = cls()
        new_NFA.transitions.update(x.transitions)
        new_NFA.transitions.update(y.transitions)
        x_final = new_NFA.transitions.setdefault(x.final, {})
        y_final = new_NFA.transitions.setdefault(y.final, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.start, {})

        x_final[''] = {y.start}
        table_start[''] = {x.start}
        y_final[''] = {new_NFA.final}
        return new_NFA

    @classmethod
    def union(cls, x, y):
        new_NFA = cls()
        new_NFA.transitions.update(x.transitions)
        new_NFA.transitions.update(y.transitions)
        x_final = new_NFA.transitions.setdefault(x.final, {})
        y_final = new_NFA.transitions.setdefault(y.final, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.start, {})

        x_final[''] = {new_NFA.final}
        table_start[''] = {x.start, y.start}
        y_final[''] = {new_NFA.final}
        return new_NFA

    @classmethod
    def kleene_star(cls, x):
        new_NFA = cls()
        new_NFA.transitions.update(x.transitions)
        x_final = new_NFA.transitions.setdefault(x.final, {})
        table_start = new_NFA.transitions.setdefault(new_NFA.start, {})
        x_final = x_final.setdefault('', set())
        table_start = table_start.setdefault('', set())

        x_final.add(x.start)
        x_final.add(new_NFA.final)
        table_start.add(x.start)
        table_start.add(new_NFA.final)
        return new_NFA
