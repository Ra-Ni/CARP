import uuid
import pandas as pd
labels = ['name', 'kind', 'type', 'visibility', 'link']
class Table:
    def __init__(self):
        self.name = ''
        self.uuid = uuid.uuid4()
        self.annotations = {}
        self.table = pd.DataFrame(columns=labels)
        self.type = ''

    def as_entry(self):
        pass


class Label:
    def __init__(self):
        self.annotations = {}
        self.frame = pd.DataFrame()
        self.uid = uuid.uuid4()

    def __str__(self):
        return str(self.uid)

    def to_string(self):
        txt = ''
        for key, value in self.annotations.items():
            txt += key + ': ' + value + '\n'

        return self.frame.to_string() + '\n\n' + txt

