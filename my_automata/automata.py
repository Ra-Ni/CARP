import re
import uuid
from ast import literal_eval
from collections import deque
from copy import deepcopy
from enum import Enum
from typing import Union

from pydot import Dot, Node, Edge
from tabulate import tabulate

from sortedcontainers import SortedSet


class machine(Enum):
    invalid = -1
    automata = 0
    dfa = 1
    nfa = 2


class automata:
    def __init__(self,
                 start: str = None,
                 final: Union[set, list, SortedSet] = SortedSet(),
                 alphabets: Union[set, list, SortedSet] = SortedSet(),
                 states: Union[set, list, SortedSet] = SortedSet(),
                 transitions: dict = {}):

        self.start = start
        self.final = final if isinstance(final, SortedSet) else SortedSet(final)
        self.alphabets = alphabets if isinstance(alphabets, SortedSet) else SortedSet(alphabets)
        self.states = states if isinstance(states, SortedSet) else SortedSet(states)
        self.transitions = transitions
        self.machine_type = machine.automata

    def walk(self, word: str) -> str:
        return ''

    def accepts(self, word: str) -> str:
        return ''

    def __str__(self):
        result = []
        pattern = re.compile(r'.*?(\[.*]).*')

        print(f'Initial State: {self.start}')
        print('Final States: {}'.format(str(list(self.final))))
        print(f'States: {str(list(self.states))}')
        for state, transition in self.transitions.items():
            for symbol, next_states in transition.items():
                sym = symbol or 'λ'
                result.append([state, sym, re.sub(pattern, r'\g<1>', str(next_states))])

        return str(tabulate(result, headers=['FROM', 'INPUT', 'TO'], tablefmt='pretty'))

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo={}):
        new_start = str(uuid.uuid4())
        new_final = set()
        new_states = set()
        new_transitions = {}
        uuid_map = {self.start: new_start}

        for state in self.states:
            new_state = uuid_map.setdefault(state, str(uuid.uuid4()))
            if state in self.final:
                new_final.add(new_state)
            new_states.add(new_state)

        for state, symbol, next_state, _ in iter(self):
            new_transitions \
                .setdefault(uuid_map[state], {}) \
                .setdefault(symbol, SortedSet()) \
                .add(uuid_map[next_state])

        result = automata(start=new_start,
                          final=new_final,
                          alphabets=deepcopy(self.alphabets),
                          transitions=new_transitions,
                          states=new_states)
        result.machine_type = self.machine_type
        memo[id(result)] = result
        return result

    def __iter__(self):
        for state, transition in self.transitions.items():
            for symbol, next_states in transition.items():
                for next_state in next_states:
                    yield state, symbol, next_state, next_state in self.final


def union(x: automata, y: automata) -> automata:
    xx, yy = deepcopy(x), deepcopy(y)
    new_start = str(uuid.uuid4())
    new_final = str(uuid.uuid4())
    xx.alphabets.update(yy.alphabets)
    xx.states.update(yy.states)
    xx.states.update([new_start, new_final])
    xx.transitions.update(yy.transitions)
    xx.transitions[new_start] = {'': SortedSet([xx.start, yy.start])}

    for final in xx.final.union(yy.final):
        xx.transitions \
            .setdefault(final, {}) \
            .setdefault('', SortedSet()) \
            .add(new_final)

    xx.start = new_start
    xx.final = SortedSet([new_final])
    xx.machine_type = machine.nfa
    return xx


def concat(x: automata, y: automata) -> automata:
    xx, yy = deepcopy(x), deepcopy(y)
    xx.alphabets.update(yy.alphabets)
    xx.transitions.update(yy.transitions)
    xx.states.update(yy.states)

    for final in xx.final:
        xx.transitions \
            .setdefault(final, {}) \
            .setdefault('', SortedSet()) \
            .add(yy.start)

    xx.final = yy.final
    xx.machine_type = machine.nfa
    return xx


def kleene(x: automata) -> automata:
    xx = deepcopy(x)
    new_start = str(uuid.uuid4())
    new_final = str(uuid.uuid4())
    xx.transitions[new_start] = {'': SortedSet([xx.start, new_final])}
    xx.states.update([new_start, new_final])

    for final in xx.final:
        xx.transitions \
            .setdefault(final, {}) \
            .setdefault('', SortedSet()) \
            .update([xx.start, new_final])

    xx.start = new_start
    xx.final = SortedSet([new_final])
    xx.machine_type = machine.nfa
    return xx


def optional(x: automata) -> automata:
    xx = deepcopy(x)
    new_start = str(uuid.uuid4())
    new_final = str(uuid.uuid4())
    xx.transitions[new_start] = {'': SortedSet([xx.start, new_final])}
    xx.states.update([new_start, new_final])

    for final in xx.final:
        xx.transitions \
            .setdefault(final, {}) \
            .setdefault('', SortedSet()) \
            .add(new_final)

    xx.start = new_start
    xx.final = SortedSet([new_final])
    xx.machine_type = machine.nfa
    return xx


def epsilon_closure(x: automata, start: Union[str, list, set, SortedSet]) -> list:
    if isinstance(start, str):
        stack = [start]
        seen = SortedSet([start])
    else:
        stack = list(start.copy())
        seen = SortedSet(stack.copy())

    while stack:
        current = stack.pop()
        if current in x.transitions and '' in x.transitions[current]:
            for next_state in x.transitions[current]['']:
                if next_state not in seen:
                    seen.add(next_state)
                    stack.append(next_state)

    return list(seen)


def dfa(x: automata):
    queue = deque([str(epsilon_closure(x, x.start))])
    y = automata(start=queue[0], alphabets=deepcopy(x.alphabets))

    while queue:
        current = queue.popleft()
        if current in y.states:
            continue

        y.states.add(current)
        states = SortedSet(literal_eval(current))
        if states & x.final:
            y.final.add(current)
        next_state = SortedSet()

        for alphabet in y.alphabets:
            for state in states:
                if state in x.transitions and alphabet in x.transitions[state]:
                    next_state.update(epsilon_closure(x, x.transitions[state][alphabet]))
            result = str(list(next_state))
            next_state.add(result)
            queue.append(result)
            y.transitions \
                .setdefault(current, {}) \
                .setdefault(alphabet, SortedSet()) \
                .add(result)

    y.machine_type = machine.dfa
    return deepcopy(y)


def remove_unreachable_states(x: automata):
    reach_states = {x.start}
    queue = deque([x.start])

    while queue:
        state = queue.pop()
        local_states = SortedSet()
        if state in x.transitions:
            for states in x.transitions[state].values():
                local_states.update(states)
        local_states.difference_update(local_states & reach_states)
        queue.extend(local_states)
        reach_states.update(local_states)

    unreachable = x.states.difference(reach_states)
    x.states = SortedSet(reach_states)
    x.final.difference_update(unreachable)

    for state in unreachable:
        x.transitions.pop(state)

        if state in x.transitions:
            for symbol in x.transitions[state].keys():
                x.transitions[state][symbol].difference_update(unreachable)


def minimize(x: automata):
    remove_unreachable_states(x)
    nF = SortedSet(x.states.difference(x.final))
    F = SortedSet(x.final)
    P = SortedSet([str(nF), str(F)])
    W = deque([nF, F])

    while W:
        A = W.popleft()

        for c in x.alphabets:
            X = set()
            for start, transition in x.transitions.items():
                if c in transition and A & transition[c]:
                    X.add(start)

            _P = deepcopy(P)
            for Y in _P:
                _Y = eval(Y)
                y = X & _Y
                yy = _Y.difference(X)
                if y and yy:
                    P.remove(Y)
                    P.update([str(y), str(yy)])
                    if _Y in W:
                        W.remove(_Y)
                        W.extend([y, yy])
                    else:
                        if len(y) <= len(yy):
                            W.append(y)
                        else:
                            W.append(yy)

    uid = {}
    while P:
        indistinct = list(eval(P.pop()))
        state = str(indistinct)
        uid.update(dict(zip(indistinct, [state] * len(indistinct))))

    new_transitions = {}
    new_final = SortedSet()
    for state, symbol, final, is_accept in iter(x):
        new_transitions\
            .setdefault(uid[state], {})\
            .setdefault(symbol, SortedSet())\
            .add(uid[final])
        if is_accept:
            new_final.add(uid[final])
    x.final = new_final
    x.transitions = new_transitions
    x.states = SortedSet(uid.values())
    x.start = uid[x.start]



def simplify(x: automata) -> None:
    uid = dict(zip(x.states, {f'S{c}' for c in range(len(x.states))}))
    new_transitions = {}
    new_finals = SortedSet()

    for start, symbol, final, is_accept in iter(x):
        new_transitions \
            .setdefault(uid[start], {}) \
            .setdefault(symbol, SortedSet()) \
            .add(uid[final])
        if is_accept:
            new_finals.add(uid[final])
    x.final = new_finals
    x.start = uid[x.start]
    x.transitions = new_transitions
    x.states = SortedSet(uid.values())


def render(x: automata, path: str):
    graph = Dot(graph_type='digraph', rankdir='LR')
    nodes = {}
    for start in x.states:
        arguments = {'shape': 'circle', 'style': 'solid'}

        if start == x.start:
            arguments['style'] = 'filled'
            arguments['fillcolor'] = 'green'
        if start in x.final:
            arguments['shape'] = 'doublecircle'

        state_node = Node(start, **arguments)
        nodes[start] = state_node
        graph.add_node(state_node)

    for start, symbol, final, _ in iter(x):
        edge = graph.get_edge(start, final)
        if edge:
            label = edge[0].__get_attribute__('label')
            label += ', {}'.format(repr(symbol))
            graph.del_edge(start, final)
            graph.add_edge(Edge(nodes[start], nodes[final], label=label))
        else:
            graph.add_edge(Edge(
                nodes[start],
                nodes[final],
                label=repr(symbol)
            ))

    if path:
        graph.write_png(path)
    return graph
