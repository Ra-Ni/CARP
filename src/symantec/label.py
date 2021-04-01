import uuid
import pandas as pd

labels = ['name', 'kind', 'type', 'visibility', 'link']
nlabels = ['kind', 'type', 'visibility', 'link']

class Table:
    def __init__(self):
        self.name = ''
        self.uuid = uuid.uuid4()
        self.annotations = {}
        self.table = pd.DataFrame(columns=['kind', 'type', 'visibility', 'link'])
        self.type = ''

    def as_entry(self):
        pass


class Entry:
    def __init__(self, name=None, kind=None, type=None, visibility=None):
        self.name = name
        self.kind = kind
        self.type = type
        self.visibility = visibility
        self.uid = uuid.uuid4()

    def like(self, other):
        return isinstance(other, Entry) and \
               other.kind == self.kind and \
               other.type == self.type and \
               self.visibility == other.visibility

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, str) and self.name == other

    def __lt__(self, other):
        return isinstance(other, Entry) and self.name < other.name

    def __le__(self, other):
        return isinstance(other, Entry) and self.name <= other.name

    def __hash__(self):
        return int(self.uid)
