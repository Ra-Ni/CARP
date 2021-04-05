import uuid
import pandas as pd
from tabulate import tabulate


class Node:
    def __init__(self, parent=None, **kwargs):

        self.children = []
        self.parent = parent
        self._uid = uuid.uuid4()
        self.data = {}
        self.data.update(kwargs)
        self._blacklist = set()

        if isinstance(parent, Node):
            self.parent.children.append(self)

        self._func = {}

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
        if '__eq__' in self._func:
            return self._func['__eq__'](other)
        return isinstance(other, Node) and self._uid == other._uid

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return isinstance(other, Node) and self._uid < other._uid

    def __str__(self):
        return str(self.uid)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    def __del__(self):
        self.children = None
        self.parent = None
        del self.data
        del self._uid

    def drop(self, item):
        if item in self.data:
            self.data.pop(item)

    def to_series(self):
        data = self.data.copy()
        name = data.pop('name')

        invalidate = set(data.keys()).intersection(self._blacklist)
        for key in invalidate:
            data.pop(key)

        return pd.Series(data, index=list(data.keys()), name=name)

    def to_string(self):
        txt = [str(self._uid)]
        for key, item in self.data.items():
            if isinstance(item, pd.DataFrame):
                item = str(tabulate(item, headers='keys', tablefmt='github', numalign='left', floatfmt=',1.5f'))
            txt.append(f'{str(key)}: {str(item)}')
        txt = '\r\n'.join(txt)

        return txt

    def update(self, other):
        if isinstance(other, Node):
            self.data.update(other.data)

    def blacklist(self, *keys: str):
        self._blacklist.update(keys)

    def override(self, key, func):
        self._func[key] = func

    def apply(self, func):
        return func(self)
