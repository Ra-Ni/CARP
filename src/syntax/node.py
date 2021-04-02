import uuid


class Node:
    def __init__(self, label, parent=None):
        self.label = label
        self.data = None
        self.children = []
        self.parent = parent
        self._uid = uuid.uuid4()

        if isinstance(parent, Node):
            self.parent.children.append(self)

    @property
    def uid(self):
        return str(self._uid)

    def adopt(self, *children) -> None:
        for child in children:
            node = child
            if isinstance(child, str):
                node = Node(child)
            self.children.append(node)
            node.parent = self

    def __hash__(self):
        return self._uid

    def __eq__(self, other):
        return isinstance(other, Node) and self._uid == other._uid

    def __lt__(self, other):
        return isinstance(other, Node) and self._uid < other._uid

    def __str__(self):

        if isinstance(self.label, str):
            return self.label
        else:
            return self.uid

    def __del__(self):
        self.children = None
        self.parent = None
        del self.label
        del self.data
        del self._uid