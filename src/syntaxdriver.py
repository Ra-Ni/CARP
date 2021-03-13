from pathlib import Path

# import syntax as syn
import lex as lx
from syntax.filter import Filter
from syntax.node import *
from syntax.node import _adopt
import syntax as syn
import pandas as pd


def update():

    analysis = syn.load()
    target = '../examples/bubblesort.src'
    path = Path(target)
    filename = str(path.parent) + '/' + str(path.stem) + '.out'
    errors = Path(filename + 'syntaxerrors')
    derivations = Path(filename + 'derivations')
    ast = Path(filename + 'ast')



if __name__ == '__main__':
    update()
    dir = '_config/'
    table_path = dir + 'll1.bak.xz'
    sets_path = dir + 'vitals.bak.xz'
    target = '../examples/polynomial.src'

    sets = pd.read_pickle(sets_path)
    table = pd.read_pickle(table_path)
    terminals = table.columns
    non_terminals = table.index
    first = sets['first set']
    follow = sets['follow set']

    fh = logging.FileHandler('ast.log', mode='w', encoding='utf-16')
    fh.setLevel(logging.DEBUG)
    logger = logging.getLogger(str(uuid.uuid4()))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)


    f = Filter(table, follow, terminals, logger)
    s = lx.load(lex_suppress_comments=1)
    s.open(target)

    resp, deriv = f.parse(s)
    # for d in deriv:
    #     print(d)
    # print(resp)
    # print(f.root)
    for node in bfs(f.root):
        print(node, node.parent)
    # remove_duds(f.root)
    # remove_dups(f.root)
    draw('test10.png', f.root)
