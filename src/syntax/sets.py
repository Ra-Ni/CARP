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
        self.restricted = ['id', 'intnum', 'floatnum', 'stringlit']
        self.line_num = 1

    def add(self, item: token):
        text = item.lexeme if len(item.lexeme) == 1 and item.type not in self.restricted else item.type
        self.derivation.append(text)

    def store(self):
        text = ' '.join(self.derivation)

        with open('../_config/out', 'w') as fstream:
            fstream.write(text)


class analyzer:
    def __init__(self, ll1: pd.DataFrame, vitals: pd.DataFrame):
        self.ll1 = ll1
        self.terminals = self.ll1.columns
        self.non_terminals = self.ll1.index
        self.first = vitals['first set']
        self.follow = vitals['follow set']
        self.tokenizer = scanner.load(suppress_comments=1)
        self.stack = []
        self.errors = False
        self.tokens = None
        self.lookahead = None
        self.safe_mode = panic

    def parse(self, target: str):
        self.tokenizer.open(target)
        self.tokens = iter(self.tokenizer)
        self.lookahead = next(self.tokens)
        self.stack.clear()
        self.stack.append('START')
        self.errors = False
        log = logger()

        while self.stack and self.lookahead:

            x = self.stack[-1]
            if x in self.terminals:
                if x == self.lookahead.type:
                    self.stack.pop()
                    log.add(self.lookahead)
                    self.lookahead = next(self.tokens, None)

                else:
                    self.safe_mode(self)

            else:
                non_terminal = self.ll1.at[x, self.lookahead.type]

                if non_terminal:
                    non_terminal = non_terminal[::-1]
                    self.stack.pop()

                    if ['ε'] != non_terminal:
                        self.stack.extend(non_terminal)

                else:
                    self.safe_mode(self)

        log.store()

        if self.lookahead or self.stack or self.errors:
            return False
        return True

    @classmethod
    def load(cls):
        backup_ll1 = Path('../_config/ll1.bak.xz')
        backup_vitals = Path('../_config/vitals.bak.xz')
        config = Path('../_config/syntax')
        backups = [backup_ll1, backup_vitals]

        if not config.exists() or config.is_dir():
            raise FileNotFoundError(f'Configuration file "{config}" does not exist or is a directory.')

        for backup in backups:
            if backup.is_dir() or backup.exists() and backup.stat().st_mtime < config.stat().st_mtime:
                os.remove(backup)

        if all(map(os.path.exists, backups)):
            return cls(*list(map(pd.read_pickle, backups)))

        with open(config, 'r') as fstream:
            grammar = urllib.parse.quote_plus(fstream.read())

        uri = 'https://smlweb.cpsc.ucalgary.ca/'
        response_ll1 = requests.get(uri + 'll1-table.php?grammar=' + grammar + '&substs=')
        response_vitals = requests.get(uri + 'vital-stats.php?grammar=' + grammar)

        if not (response_ll1.ok and response_vitals.ok):
            raise ConnectionError("Connection to UCalgary's grammar tool is currently unavailable.")

        ll1 = pd.read_html(response_ll1.text)[1]
        vitals = pd.read_html(response_vitals.text)[2]

        ll1.rename(columns=dict(zip(ll1.columns[1:].to_list(), ll1.xs(0, 0)[1:].to_list())),
                   index=dict(zip(ll1.index[1:].to_list(), ll1.xs(0, 1)[1:].to_list())),
                   inplace=True)

        vitals.rename(index=dict(zip(vitals.index.to_list(), vitals.xs('nonterminal', 1).to_list())),
                      inplace=True)

        ll1.drop([0], 0, inplace=True)
        ll1.drop([0], 1, inplace=True)
        vitals.drop(['nonterminal'], 1, inplace=True)

        for index, series in ll1.iterrows():
            new_series = series.where(pd.notnull(series), None)
            new_series = new_series.replace([r'.*\s*→\s*', '&epsilon'], ['', 'ε'], regex=True)
            ll1.loc[index] = new_series.str.split()

        for dst, src, value in [(vitals['first set'], vitals['nullable'], ' ε'),
                                (vitals['follow set'], vitals['endable'], ' $')]:
            src.replace(['yes', 'no'], [value, ''], inplace=True)
            dst.mask(dst == '∅', None, inplace=True)
            dst += src
            dst.where(pd.isnull(dst), dst.str.split(), inplace=True)

        ll1.to_pickle(backup_ll1, compression='xz')
        vitals.to_pickle(backup_vitals, compression='xz')

        return cls(ll1, vitals)


def panic(parser: analyzer):
    top = parser.stack[-1]
    lookahead = parser.lookahead

    if top in parser.terminals:
        print("[{}] SyntaxError: invalid syntax expectation '{}'".format(lookahead.location, top))
        parser.stack.pop()
        return

    follow = parser.follow.loc[top] or []
    series = parser.ll1.loc[top].dropna().index

    print("[%s] SyntaxError: invalid syntax '%s' ∉ %s" % (lookahead.location, lookahead.type, set(series)))

    print(lookahead.type in parser.ll1.loc[top].dropna().index)
    if lookahead and lookahead in follow:
        parser.stack.pop()
    else:
        #lookahead and not (lookahead.type in first or 'ε' in first and lookahead.type in follow)
        while lookahead and lookahead.type not in series:
            lookahead = parser.lookahead = next(parser.tokens, None)

    parser.errors = True


if __name__ == '__main__':
    analysis = analyzer.load()

    analysis.parse('../../examples/bubblesort.src')
    analysis.parse('../../examples/polynomial.src')
    # print(analysis.follow.to_string())

    # uurl = 'https://smlweb.cpsc.ucalgary.ca/vital-stats.php?grammar=START+-%3E+Prog+.%0D%0AProg+-%3E+ClassDecl+FuncDef+main+FuncBody.%0D%0AClassDecl+-%3E+class+id+Inherit+opencubr+ClassDeclBody+closecubr+semi+ClassDecl%0D%0A%09%7C+.%0D%0AFuncDef+-%3E+Function+FuncDef+%0D%0A%09%7C+.%0D%0AFunction+-%3E+FuncHead+FuncBody.%0D%0AInherit+-%3E+inherits+id+NestedId+%0D%0A%09%7C+.%0D%0ANestedId+-%3E+comma+id+NestedId+%0D%0A%09%7C+.%0D%0AVisibility+-%3E+public+%0D%0A%09%7C+private+%0D%0A%09%7C+.%0D%0AMemberDecl+-%3E+FuncDecl+%0D%0A%09%7C+VarDecl+.%0D%0AClassDeclBody+-%3E+Visibility+MemberDecl+ClassDeclBody+%0D%0A%09%7C+.%0D%0AFuncDecl+-%3E+func+id+openpar+FParams+closepar+colon+FuncDeclTail+semi.%0D%0AFuncDeclTail+-%3E+Type+%0D%0A%09%7C+void+.%0D%0AVarDeclRep%09-%3E+VarDecl+VarDeclRep+%0D%0A%09%7C+.%0D%0AVarDecl+-%3E+Type+id+ArraysizeTail+semi+.%0D%0AFParams+-%3E+Type+id+ArraysizeTail+FParamsTail+%0D%0A%09%7C+.%0D%0AType+-%3E+integer+%0D%0A%09%7C+float+%0D%0A%09%7C+string+%0D%0A%09%7C+id+.%0D%0AFParamsTail+-%3E+comma+Type+id+ArraysizeTail+FParamsTail%0D%0A%09%7C+.%0D%0AArraysize+-%3E+opensqbr+IntNum+closesqbr+.%0D%0AArraysizeTail+-%3E+Arraysize+ArraysizeTail+%0D%0A%09%7C+.%0D%0AIntNum+-%3E+intnum+%0D%0A%09%7C+.%0D%0AFuncHead+-%3E+func+id+ClassMethod+openpar+FParams+closepar+colon+FuncDeclTail.%0D%0AFuncBody+-%3E+opencubr+MethodBody+StatementTail+closecubr.%0D%0AClassMethod+-%3E+coloncolon+id+%0D%0A%09%7C+.%0D%0AMethodBody+-%3E+var+opencubr+VarDeclRep+closecubr+%0D%0A%09%7C+.%0D%0AStatementTail+-%3E+Statement+StatementTail+%0D%0A%09%7C+.%0D%0AStatement+-%3E+FuncVarStartCaveat+semi+%0D%0A%09%7C+if+openpar+ArithExpr+closepar+then+StatBlock+else+StatBlock+semi+%0D%0A+%09%7C+while+openpar+ArithExpr+closepar+StatBlock+semi+%0D%0A+%09%7C+read+openpar+IdnestStart+closepar+semi+%0D%0A+%09%7C+write+openpar+Expr+closepar+semi+%0D%0A+%09%7C+return+openpar+Expr+closepar+semi+%0D%0A+%09%7C+break+semi+%0D%0A+%09%7C+continue+semi+.%0D%0AAssignStat+-%3E++AssignOp+Expr.%0D%0AAssignOp+-%3E+assign+.%0D%0AExpr+-%3E+ArithExpr+ExprTail.%0D%0AArithExpr+-%3E+Term+ArithExprTail+.%0D%0AArithExprTail+-%3E+AddOp+Term+ArithExprTail%0D%0A++++%7C+.%0D%0AExprTail+-%3E+RelOp+ArithExpr+%7C+.%0D%0AStatBlock+-%3E+opencubr+StatementTail+closecubr%0D%0A%09%7C+Statement%0D%0A%09%7C+.%0D%0ARelOp+-%3E+eq+%0D%0A%09%7C+noteq+%0D%0A%09%7C+lt+%0D%0A%09%7C+gt+%0D%0A%09%7C+leq+%0D%0A%09%7C+geq+.%0D%0AAddOp+-%3E+plus+%0D%0A%09%7C+minus+%0D%0A%09%7C+or.%0D%0AMultOp+-%3E+mult+%0D%0A%09%7C+div+%0D%0A%09%7C+and+.%0D%0ATerm+-%3E+Factor+TermTail+.%0D%0ATermTail+-%3E+MultOp+Factor+TermTail+%0D%0A%09%7C+.%0D%0AFactor+-%3E+FuncVarStart+%0D%0A%09%7C+intnum+%0D%0A%09%7C+floatnum+%0D%0A%09%7C+stringlit+%0D%0A%09%7C+openpar+ArithExpr+closepar+%0D%0A%09%7C+not+Factor+%0D%0A%09%7C+Sign+Factor+%0D%0A%09%7C+qmark+opensqbr+Expr+colon+Expr+colon+Expr+closesqbr+.%0D%0ASign+-%3E+plus+%0D%0A%09%7C+minus+.%0D%0AAParams+-%3E+Expr+AParamsTail+%0D%0A%09%7C+.%0D%0AAParamsTail+-%3E+comma+Expr+AParamsTail+%0D%0A%09%7C+.%0D%0AIdnestStart+-%3E+id+IdnestVarBody+.%0D%0AIdnestVarBody+-%3E+IndiceRep+IdnestVarBodyTail+%0D%0A%09%7C+openpar+AParams+closepar+dot+id+IdnestVarBody+.%0D%0AIdnestVarBodyTail+-%3E+dot+id+IdnestVarBody+%0D%0A%09%7C+.%0D%0AFuncVarStart+-%3E+id+IdnestBody.%0D%0AIdnestBody+-%3E+IndiceRep+IdnestBodyTail%0D%0A%09%7C+openpar+AParams+closepar+IdnestBodyTail+.%0D%0AIdnestBodyTail+-%3E+dot+id+IdnestBody+%0D%0A%09%7C+.%0D%0AFuncVarStartCaveat+-%3E+id+IdnestCaveatBody.%0D%0AIdnestCaveatBody+-%3E+IndiceRep+IdnestCaveatBodyTail%0D%0A%09%7C+openpar+AParams+closepar+IdnestCaveatBodyTailTwo+.%0D%0AIdnestCaveatBodyTail+-%3E+dot+id+IdnestCaveatBody+%0D%0A%09%7C+AssignStat+.%0D%0AIdnestCaveatBodyTailTwo+-%3E+dot+id+IdnestCaveatBody+%0D%0A%09%7C+.%0D%0AIndiceRep+-%3E+opensqbr+ArithExpr+closesqbr+IndiceRep+%0D%0A%09%7C+.'
    # r = requests.get(uurl)
    # frame = pd.read_html(r.text)[2]
    #
    # old_index = frame.index.to_list()
    # new_index = frame.xs('nonterminal', 1).to_list()
    # index_map = dict(zip(old_index, new_index))
    #
    # frame.rename(index=index_map, inplace=True)
    # frame.drop(['nonterminal'], 1, inplace=True)
    #
    #
    # sets = [frame['first set'], frame['follow set']]
    # for item in sets:
    #     item.mask(item == '∅', None, inplace=True)
    #     item.where(pd.isnull(item), item.str.split(), inplace=True)
    #
    # print(frame.to_string())
