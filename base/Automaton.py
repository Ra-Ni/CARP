import uuid
from tabulate import tabulate
from ast import literal_eval
from collections import deque
from ordered_set import OrderedSet

class RejectStateException(BaseException):
    def __init__(self, token):
        super(RejectStateException, self).__init__(token)
        self.msg = 'Input of "{}" not in automaton\'s language'.format(token)

    def __str__(self):
        return self.msg

class Automaton:
    def __init__(self, symbol: str = None, label: str = None):
        self.label = label
        self.initial_state = self.__generate_uid()

        if symbol:
            final_state = self.__generate_uid()
            self.final_states = {final_state}
            self.transitions = {self.initial_state: {symbol: final_state}}
        else:
            self.final_states = {self.initial_state}
            self.transitions = {self.initial_state: {}}

    def __del__(self):
        del self.initial_state
        del self.final_states
        del self.transitions

    def __str__(self):
        tabulate_list = [['STATE', 'INPUT', 'NEXT STATE']]

        for state, transition in self.transitions.items():
            for symbol, next_state in transition.items():
                tabulate_list.append([state, symbol, next_state])

        return tabulate(tabulate_list, tablefmt='grid')

    @staticmethod
    def __generate_uid():
        return str(uuid.uuid4())

    def union(self, other, overwrite=True):
        self.transitions.update(other.transitions)
        self.final_states.update(other.final_states)

        new_final_state = self.__generate_uid()
        new_initial_state = self.__generate_uid()

        self.transitions[new_final_state] = {}
        self.transitions[new_initial_state] = {'': {self.initial_state, other.initial_state}}

        for final_state in self.final_states:
            symbol_set = self.transitions[final_state].setdefault('', set())
            symbol_set.update(new_final_state)

        if overwrite:
            del other

    def concat(self, other, overwrite=True):
        self.transitions.update(other.transitions)

        for final_state in self.final_states:
            self.transitions[final_state].setdefault('', set()).add(other.initial_state)

        self.final_states.clear()
        self.final_states.update(other.final_states)

        if overwrite:
            del other

    def kleene(self):
        new_initial_state = self.__generate_uid()
        new_final_state = self.__generate_uid()

        self.transitions[new_initial_state] = {'': {new_final_state, self.initial_state}}
        self.transitions[new_final_state] = {}

        for final_state in self.final_states:
            self.transitions[final_state].setdefault('', set()) \
                .union({self.initial_state, new_final_state})

        self.final_states.clear()
        self.final_states.add(new_final_state)
        self.initial_state = new_initial_state

    def __epsilon_closure(self, state):
        stack = []
        encountered_states = set()
        stack.append(state)

        while stack:
            state = stack.pop()
            if state not in encountered_states:
                encountered_states.add(state)
                if '' in self.transitions[state]:
                    stack.extend(self.transitions[state][''])

        return encountered_states

    def __rehash(self, simplified: bool = False):
        if not simplified:
            uuid_map = {uid: self.__generate_uid() for uid in self.transitions.keys()}
        else:
            keys = list(self.transitions.keys())
            n = len(keys)
            uuid_map = {keys[uid]: 'S{}'.format(uid) for uid in range(n)}

        for state in list(self.transitions.keys()):
            transition = self.transitions[state]
            try:
                for symbol, next_states in transition.items():
                    self.transitions[state][symbol] = uuid_map[str(next_states)]
            except KeyError:
                print("Found")
            self.transitions[uuid_map[state]] = self.transitions.pop(state)

        self.final_states = {uuid_map[uid] for uid in self.final_states}
        self.initial_state = uuid_map[self.initial_state]

    def minify(self, simplified: bool = False):
        min_transitions = {}
        min_init_state = None
        min_final_states = set()

        queue = deque(self.initial_state)
        visited = set(self.initial_state)

        while queue:
            current_state = queue.popleft()

            state_set = self.__epsilon_closure(current_state)
            current_state = str(state_set)
            if current_state != str(state_set):
                print("Found2")
            if not min_init_state:
                min_init_state = current_state

            for state in state_set:
                for symbol, next_states in self.transitions[state].items():
                    if symbol != '':
                        min_transitions \
                            .setdefault(current_state, {}) \
                            .setdefault(symbol, set()) \
                            .update(next_states)
                if state in self.final_states:
                    min_final_states.add(current_state)
                if state not in visited:
                    queue.append(state)
                    visited.add(state)

        self.transitions = min_transitions
        self.initial_state = min_init_state
        self.final_states = min_final_states
        self.__rehash(simplified)

    # todo make sure to use ref for dependencies
    def accepts(self, text: str):
        result = False
        try:
            for state, is_final in self.walk(text):
                result = is_final
        except RejectStateException:
            result = False
        return result

    def walk(self, text: str):
        current = self.initial_state
        last_symbol = None
        try:
            for symbol in text:
                last_symbol = symbol
                current = self.transitions[current][symbol]
                yield current, current in self.final_states
        except KeyError:
            raise RejectStateException(last_symbol)
