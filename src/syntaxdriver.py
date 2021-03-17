import logging
import uuid
from pathlib import Path

import tools.ucalgary as ucal
from syntax import *
from lex import *
from syntax.test import Test

if __name__ == '__main__':
    dir = '_config/'
    out_dir = '../examples/'
    target = Path('polynomial.src')
    target = Path('../tests/grammar/TEST_variable.src')
    out_ast = Path(out_dir + target.stem + '.outast.png')
    out_derivations = Path(out_dir + target.stem + '.outderivations.log')
    out_errors = Path(out_dir + target.stem + '.outerrors.log')
    target = Path(out_dir + str(target))

    ll1, vitals = ucal.load(online=False)
    first = vitals['first set']
    follow = vitals['follow set']
    terminals = ll1.columns
    non_terminals = ll1.index

    fh = logging.FileHandler(out_errors, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    logger = logging.getLogger(str(uuid.uuid4()))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    s = scanner(suppress_comments=1)
    s.open(target)

    f = Test(ll1, follow, terminals, logger)
    resp, derivations = f.parse(s)
    out_derivations.write_text(' '.join(x.type for x in derivations))

    tree = AST(f.node_stack[0])

    print(resp)

    #tree.apply('all')

    tree.render(out_ast)

