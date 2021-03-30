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


class Label:
    def __init__(self):
        self.data = pd.DataFrame()
        self.uid = uuid.uuid4()
        self.reference = pd.Series(index=['kind', 'type', 'visibility', 'link'], name=None, dtype='object')

    def __str__(self):
        return str(self.uid)

    def to_string(self):
        txt = str(self.uid)

        txt2 = '' if self.reference is None else self.reference.to_string()
        return self.data.to_string() + '\n\n' + txt + '\n\n' + txt2
