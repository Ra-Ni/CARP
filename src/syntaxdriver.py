from pathlib import Path

import syntax as syn

def testhello():
    return 's'

if __name__ == '__main__':
    analysis = syn.load()
    target = '../examples/bubblesort.src'
    path = Path(target)
    filename = str(path.parent) + '/' + str(path.stem) + '.out'
    errors = Path(filename + 'syntaxerrors')
    derivations = Path(filename + 'derivations')
    ast = Path(filename + 'ast')

    response = analysis.parse(target)
    print(response)
    # derivations.write_text(analysis.derivations, encoding='UTF-16')
    print([str(x.type) for x in analysis.derivations])

    analysis.ll1.to_csv('_config/ll1.csv')
    print(analysis.ll1.to_string())
    print(analysis.logs)


    errors.write_text(analysis.errors, encoding='UTF-16')
    ast.write_text(analysis.ll1.to_string(), encoding='UTF-16')
