import uuid

from pydot import Dot, Node, Edge
from sortedcontainers import SortedSet
from tabulate import tabulate


def generate_uid():
    return str(uuid.uuid4())


class RejectStateException(BaseException):
    def __init__(self, token):
        super(RejectStateException, self).__init__(token)
        self.msg = 'Input of "{}" not in automaton\'s language'.format(token)

    def __str__(self):
        return self.msg


class fa:
    def __init__(self, label: str = None):
        self.label = label
        self.initial_state = generate_uid()
        self.transitions = {}
        self.final_states = SortedSet()
        self.states = SortedSet()

    def __del__(self):
        del self.initial_state
        del self.final_states
        del self.transitions
        del self.states

    def __str__(self):
        tabulate_list = [['STATE', 'INPUT', 'NEXT STATE']]

        for state, transition in self.transitions.items():
            for symbol, next_state in transition.items():
                tabulate_list.append([state, symbol, next_state])

        return tabulate(tabulate_list, tablefmt='grid')

    def __copy__(self):
        other = fa()
        other.label = self.label
        other.initial_state = self.initial_state
        other.transitions = self.transitions.copy()
        other.final_states = self.final_states.copy()
        other.states = self.states.copy()
        return other

    def __iter__(self):
        for state, transition in self.transitions.items():
            for symbol, next_states in transition.items():
                if type(next_states) == str:
                    yield state, symbol, next_states
                else:
                    for next_state in next_states:
                        yield state, symbol, next_state

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

    def show(self, path=None):
        graph = Dot(graph_type='digraph', rankdir='LR')
        nodes = {}
        for state in self.states:
            arguments = {'shape': 'circle', 'style': 'solid'}

            if state == self.initial_state:
                arguments['style'] = 'filled'
                arguments['fillcolor'] = 'green'
            if state in self.final_states:
                arguments['shape'] = 'doublecircle'

            state_node = Node(state, **arguments)
            nodes[state] = state_node
            graph.add_node(state_node)

        for state, symbol, next_state in iter(self):
            edge = graph.get_edge(state, next_state)
            if edge:
                new_label = edge[0].__get_attribute__('label')
                new_label += ', {}'.format(repr(symbol))
                graph.del_edge(state, next_state)
                graph.add_edge(Edge(nodes[state], nodes[next_state], label=new_label))
            else:
                graph.add_edge(Edge(
                    nodes[state],
                    nodes[next_state],
                    label=repr(symbol)
                ))

        if path:
            graph.write_png(path)
        return graph
