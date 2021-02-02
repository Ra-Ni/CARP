import json
import re
from collections import deque, OrderedDict

from lexer import nfa, dfa


class generator:
    def __init__(self):
        self.machines = {}
        self.regex = {'*': 0, '?': 1, '.': 2, '|': 3, '\\': 4, ']': 5, ')': 5, '[': 6, '(': 6}

    def load(self, file):
        crlf = re.compile(r'[\r\n]+')
        assign = re.compile(r'\s*(::=)\s*')

        with open(file) as reader:
            data = reader.read()
            data = re.split(crlf, data)
            for datum in data:
                expr = re.split(assign, datum)
                self.machines[expr[0]] = expr[-1]

    def exec(self):
        for key in list(self.machines.keys()):
            if type(self.machines[key]) is not nfa:
                self._exec(key, self.machines[key])


    def _exec(self, label, start):
        queue = deque(start)
        operations = []
        output = deque()
        prev_is_seg = False


        def update_operations(val='.', rep=1):
            while operations and rep:
                val2 = operations.pop()
                if self.regex[val2] < self.regex[val]:
                    output.append(val2)
                else:
                    operations.append(val2)
                    break
            operations.extend([segment] * rep)

        while queue:
            next_is_seg = False
            segment = queue.popleft()

            while segment not in self.regex \
                    and queue \
                    and queue[0] not in self.regex \
                    and segment not in self.machines:
                segment += queue.popleft()

            if segment in self.machines:
                if type(self.machines[segment]) is not nfa:
                    self._exec(segment, self.machines[segment])
                output.append(self.machines[segment].copy())
                next_is_seg = True

            elif segment not in self.regex:
                output.append(nfa(segment))
                update_operations(rep=len(segment)-1)
                next_is_seg = True

            else:
                update_operations(val=segment)
                if segment == ']' or segment == ')':
                    y, x = operations.pop(), operations.pop()
                    if x == '[' and y == ']':
                        update_operations('?')
                    elif x != '(' or y != ')':
                        raise Exception("Wrong input")
                if segment == '*' or segment == '?':
                    next_is_seg = True

                prev_is_seg = False

            if prev_is_seg:
                update_operations()

            prev_is_seg = next_is_seg

        while operations:
            output.append(operations.pop())

        stack = []
        while output:
            result = output.popleft()
            if result == '*':
                result = nfa.kleene(stack.pop())
            elif result == '|':
                result = nfa.union(stack.pop(), stack.pop())
            elif result == '.':
                y, x = stack.pop(), stack.pop()
                result = nfa.concat(x, y)
            elif result == '?':
                result = nfa.optional(stack.pop())
            else:
                stack.append(result)
                continue

            result = dfa.from_nfa(result)
            result.rehash()
            result = nfa.from_dfa(result)
            stack.append(result)
        fa = stack.pop()
        fa = dfa.from_nfa(fa)
        fa.rehash(True)
        fa = nfa.from_dfa(fa)
        fa.show(f'img/{label}.png')
        self.machines[label] = fa

    # def _shunting(self, raw: str):
    #     raw = re.sub(r'\s*(::=)\s*', r'\1', raw)
    #
    #     self.regex = OrderedDict({
    #         None: """while temp != sym:\n\texec('regex[temp]')\n\ttemp = operations.pop()""",
    #         '*':"""output.append(output.pop().kleene())""",
    #         '?': """x = output.pop().optional()\noutput.append(x)""",
    #         '|':"""y, x = output.pop(), output.pop()\noutput.append(x.union(y))""",
    #         ']': """sym = '['\nexec('regex[None]')\nexec('regex["?"]')""",
    #         ')': """sym = '('\nexec('regex[None]')""",
    #         '(': '',
    #         '[': '',
    #         '': """y, x = output.pop(), output.pop()\noutput.append(x.concat(y))""",
    #         '::=':"""y, x = output.pop(), output.pop()\ny.label = x\noutput.append(y)"""
    #     })
    #
    #
    #     operations = []
    #     output = deque()
    #     queue = deque()
    #
    #     while queue:
    #
    #         segment = queue.popleft()
    #
    #         while segment not in self.regex\
    #                 and queue\
    #                 and queue[0] not in self.regex\
    #                 and segment not in self.machines:
    #             segment += queue.popleft()
    #
    #         if segment in self.machines and self.machines[segment]
    #         if segment not in operators and segment not in self.machines:
    #         while segment not in self.machines\
    #                 and queue\
    #                 and queue[0] not in operators \
    #                 and type(queue[0]) is not nfa:
    #             segment += queue.popleft()
    #
    #     data = None
    #     operations = []
    #     output = deque()
    #     tokens = deque()
    #
    #     with open(file) as json_file:
    #         data = json.load(json_file)
    #     tokens = data['LANGUAGE']
    #
    #     while tokens:
    #         token = tokens.popleft()
    #
    #         if token not in self.machines:
    #             if type(token) is nfa:
    #                 output.append(token)
    #             else:
    #
    #                 while tokens and tokens[0] not in self.machines and type(tokens[0]) is not nfa:
    #                     token += tokens.popleft()
    #                 if token in self.machines:
    #                     output.append(self.machines[token])
    #                 elif token in
    #
    #                     if type(self.machines[token]) is not nfa:
    #                         tokens.extendleft(reversed(list(data[token])))
    #                     else:
    #                         output.append(reference[token])
    #                 else:
    #                     output.append(token)
    #
    #         elif token == "\\" and tokens:
    #             token += tokens.popleft()
    #
    #             output.append(token)
    #
    #         elif token == '(' or token == '[':
    #             operations.append(token)
    #
    #         elif token == ')' or token == ']':
    #             target_token = '(' if token == ')' else '['
    #             found = False
    #             while operations and not found:
    #                 operation = operations.pop()
    #                 if operation == target_token:
    #                     found = True
    #                 else:
    #                     output.append(operation)
    #             if token == ']':
    #                 output.append('?')
    #             # todo if found, if not found
    #
    #         else:
    #             token_priority = language[token]
    #             operation_complete = False
    #             while operations and not operation_complete:
    #                 operation_priority = language[operations[-1]]
    #                 if token_priority >= operation_priority:
    #                     output.append(operations.pop())
    #                 else:
    #                     operation_complete = True
    #             operations.append(token)
    #
    #     while operations:
    #         output.append(operations.pop())
    #
    #     return output
    #
    # def to_pNFA(result: deque):
    #
    #     stack = list()
    #
    #     while result:
    #         current = result.popleft()
    #         if current not in language:
    #             if type(current) is pNFA:
    #                 stack.append(current)
    #             else:
    #                 if current in escape_codes:
    #                     current = escape_codes[current]
    #                 stack.append(pNFA(current))
    #         elif current == '*':
    #             stack.append(pNFA.kleene_star(stack.pop()))
    #         elif current == ' ':
    #             second, first = stack.pop(), stack.pop()
    #
    #             stack.append(pNFA.concat(first, second))
    #         elif current == '|':
    #             stack.append(pNFA.union(stack.pop(), stack.pop()))
    #         elif current == '?':
    #             stack.append(pNFA.option(stack.pop()))
    #     if len(stack) != 1:
    #         print("Stack not eq to 1 in to_pNFA")
    #
    #     final = stack.pop()
    #
    #     return final
    #
