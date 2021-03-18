import uuid


class Node:
    def __init__(self, label: str, parent=None):
        self.label = label
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
        return self.label
