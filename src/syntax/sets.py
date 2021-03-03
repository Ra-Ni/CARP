import os
import re
from pathlib import Path
import urllib.parse
import requests
import pandas as pd
from lex import scanner, token


class logger:
    def __init__(self):
        self.derivation = []
        self.restricted = ['id', 'intnum', 'floatnum', 'stringlit' ]
        self.line_num = 1

    def add(self, item: token):
        text = item.lexeme if len(item.lexeme) == 1 and item.type not in self.restricted  else item.type
        self.derivation.append(text)

    def store(self):
        text = ' '.join(self.derivation)

        with open('../_config/out', 'w') as fstream:
            fstream.write(text)


class analyzer:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame
        self.tokenizer = scanner.load(suppress_comments=1)

    def parse(self, target: str):
        stack = ['START']
        errors = False
        self.tokenizer.open(target)
        tokens = iter(self.tokenizer)
        a = next(tokens)
        log = logger()
        while stack and a:

            x = stack[-1]
            if x in self.frame.columns:
                if x == a.type:
                    stack.pop()
                    log.add(a)
                    a = next(tokens, None)

                else:
                    errors = True
                    break

            else:
                non_terminal = self.frame.at[x, a.type]

                if non_terminal:
                    non_terminal = non_terminal[::-1]
                    stack.pop()

                    if ['ε'] != non_terminal:
                        stack.extend(non_terminal)

                else:
                    errors = True
                    break
        log.store()
        if a or stack or errors:
            return False
        return True

    @classmethod
    def load(cls):
        backup = Path('../_config/syntax_table.bz2')
        config = Path('../_config/syntax')

        if not config.exists() or config.is_dir():
            raise FileNotFoundError(f'Configuration file "{config}" does not exist or is a directory.')

        if backup.is_dir() or backup.exists() and backup.stat().st_mtime < config.stat().st_mtime:
            os.remove(backup)

        if backup.exists():
            return cls(pd.read_pickle(backup))

        with open(config, 'r') as fstream:
            grammar = urllib.parse.quote_plus(fstream.read())

        query = 'https://smlweb.cpsc.ucalgary.ca/ll1-table.php?grammar=' + grammar + '&substs='
        response = requests.get(query)

        if not response.ok:
            raise ConnectionError("Connection to UCalgary's grammar tool is currently unavailable.")

        frame = pd.read_html(response.text)[1]

        old_cols = frame.columns[1:].to_list()
        new_cols = frame.xs(0, 0)[1:].to_list()
        col_map = dict(zip(old_cols, new_cols))

        old_index = frame.index[1:].to_list()
        new_index = frame.xs(0, 1)[1:].to_list()
        index_map = dict(zip(old_index, new_index))

        frame.rename(columns=col_map, index=index_map, inplace=True)
        frame.drop([0], 0, inplace=True)
        frame.drop([0], 1, inplace=True)

        for index, series in frame.iterrows():
            new_series = series.where(pd.notnull(series), None)
            new_series = new_series.replace([r'.*\s*→\s*', '&epsilon'], ['', 'ε'], regex=True)
            frame.loc[index] = new_series.str.split()

        frame.to_pickle(backup)

        return cls(frame)


if __name__ == '__main__':
    analysis = analyzer.load()
    resp = analysis.parse('../../examples/bubblesort.src')
    print(resp)
