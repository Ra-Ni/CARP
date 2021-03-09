import uuid


class Node:
    def __init__(self, label: str = None, parent = None, token = None):
        self.label = label
        self.token = token
        self.children = []
        self.parent = parent
        self._uid = uuid.uuid4()

        if parent and isinstance(parent, Node):
            if self.label == parent.label:



                self.parent = self.parent.parent

            self.parent.children.append(self)

    @property
    def uid(self):
        return str(self._uid)

    def __hash__(self):
        return hash(self._uid)

    def __eq__(self, other):
        return self._uid == other._uid

    def __lt__(self, other):
        return self._uid < other._uid

    def __str__(self):
        if not self.token or self.token.lexeme == self.label:
            return self.label
        return self.label + '\n' + self.token.lexeme
