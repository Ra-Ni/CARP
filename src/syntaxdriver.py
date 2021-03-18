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

    out_ast = Path(out_dir + target.stem + '.outast.png')
    out_derivations = Path(out_dir + target.stem + '.outderivations.log')
    out_errors = Path(out_dir + target.stem + '.outerrors.log')
    target = Path(out_dir + str(target))

    fh = logging.FileHandler(out_errors, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)


    s = scanner(suppress_comments=1)
    s.open(target)

    f = Test.load(fh)
    resp = f.parse(s)



    print(resp)

    #tree.apply('all')

    f.ast.render(out_ast)

