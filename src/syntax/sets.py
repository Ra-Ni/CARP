from typing import Union

import requests
from bs4 import BeautifulSoup
import pandas as pd


# x-axis = 0
# y-axis = 1
def fix_table(frame: pd.DataFrame, row: int = 0, col: int = 0) -> pd.DataFrame:
    if not 0 <= row <= 1 or not 0 <= col <= 1:
        raise ValueError("row/column value may only be in {0, 1}")

    rows, cols = frame.shape
    alias = {}
    transformation = frame

    if col:
        alias = dict(zip(list(range(row, cols)), transformation.iloc[0, row:].values.tolist()))
        transformation = transformation.drop([0], 0)
        transformation = transformation.rename(columns=alias)

    if row:
        alias = dict(zip(list(range(col, rows)), transformation.iloc[col:, 0].values.tolist()))
        transformation = transformation.drop([0], 1)
        transformation = transformation.rename(index=alias)

    # if alias:
    #     transformation = transformation.rename(**alias)

    return transformation

# pandas, lxml, requests
def first_second_sets():
    url = "https://smlweb.cpsc.ucalgary.ca/vital-stats.php?grammar=START+-%3E+Prog+.%0D%0AProg+-%3E+ClassDecl+FuncDef+main+FuncBody.%0D%0AClassDecl+-%3E+class+id+Inherit+opencubr+ClassDeclBody+closecubr+semi+ClassDecl%0D%0A%09%7C+.%0D%0AFuncDef+-%3E+Function+FuncDef+%0D%0A%09%7C+.%0D%0AFunction+-%3E+FuncHead+FuncBody.%0D%0AInherit+-%3E+inherits+id+NestedId+%0D%0A%09%7C+.%0D%0ANestedId+-%3E+comma+id+NestedId+%0D%0A%09%7C+.%0D%0AVisibility+-%3E+public+%0D%0A%09%7C+private+%0D%0A%09%7C+.%0D%0AMemberDecl+-%3E+FuncDecl+%0D%0A%09%7C+VarDecl+.%0D%0AClassDeclBody+-%3E+Visibility+MemberDecl+ClassDeclBody+%0D%0A%09%7C+.%0D%0AFuncDecl+-%3E+func+id+openpar+FParams+closepar+colon+FuncDeclTail+semi.%0D%0AFuncDeclTail+-%3E+Type+%0D%0A%09%7C+void+.%0D%0AVarDeclRep%09-%3E+VarDecl+VarDeclRep+%0D%0A%09%7C+.%0D%0AVarDecl+-%3E+Type+id+ArraysizeTail+semi+.%0D%0AFParams+-%3E+Type+id+ArraysizeTail+FParamsTail+%0D%0A%09%7C+.%0D%0AType+-%3E+integer+%0D%0A%09%7C+float+%0D%0A%09%7C+string+%0D%0A%09%7C+id+.%0D%0AFParamsTail+-%3E+comma+Type+id+ArraysizeTail+FParamsTail%0D%0A%09%7C+.%0D%0AArraysize+-%3E+opensqbr+IntNum+closesqbr+.%0D%0AArraysizeTail+-%3E+Arraysize+ArraysizeTail+%0D%0A%09%7C+.%0D%0AIntNum+-%3E+intnum+%0D%0A%09%7C+.%0D%0AFuncHead+-%3E+func+id+ClassMethod+openpar+FParams+closepar+colon+FuncDeclTail.%0D%0AFuncBody+-%3E+opencubr+MethodBody+StatementTail+closecubr.%0D%0AClassMethod+-%3E+coloncolon+id+%0D%0A%09%7C+.%0D%0AMethodBody+-%3E+var+opencubr+VarDeclRep+closecubr+%0D%0A%09%7C+.%0D%0AStatementTail+-%3E+Statement+StatementTail+%0D%0A%09%7C+.%0D%0AStatement+-%3E+FuncVarStartCaveat+semi+%0D%0A%09%7C+if+openpar+ArithExpr+closepar+then+StatBlock+else+StatBlock+semi+%0D%0A+%09%7C+while+openpar+ArithExpr+closepar+StatBlock+semi+%0D%0A+%09%7C+read+openpar+IdnestStart+closepar+semi+%0D%0A+%09%7C+write+openpar+Expr+closepar+semi+%0D%0A+%09%7C+return+openpar+Expr+closepar+semi+%0D%0A+%09%7C+break+semi+%0D%0A+%09%7C+continue+semi+.%0D%0AAssignStat+-%3E++AssignOp+Expr.%0D%0AAssignOp+-%3E+assign+.%0D%0AExpr+-%3E+ArithExpr+.%0D%0AArithExpr+-%3E+Term+ArithExprTail+.%0D%0AArithExprTail+-%3E+AddOp+ArithExpr+%0D%0A%09%7C+RelOp+ArithExpr+%0D%0A%09%7C+.%0D%0AStatBlock+-%3E+opencubr+StatementTail+closecubr%0D%0A%09%7C+Statement%0D%0A%09%7C+.%0D%0ARelOp+-%3E+eq+%0D%0A%09%7C+noteq+%0D%0A%09%7C+lt+%0D%0A%09%7C+gt+%0D%0A%09%7C+leq+%0D%0A%09%7C+geq+.%0D%0AAddOp+-%3E+plus+%0D%0A%09%7C+minus+%0D%0A%09%7C+or.%0D%0AMultOp+-%3E+mult+%0D%0A%09%7C+div+%0D%0A%09%7C+and+.%0D%0ATerm+-%3E+Factor+TermTail+.%0D%0ATermTail+-%3E+MultOp+Factor+TermTail+%0D%0A%09%7C+.%0D%0AFactor+-%3E+FuncVarStart+%0D%0A%09%7C+intnum+%0D%0A%09%7C+floatnum+%0D%0A%09%7C+stringlit+%0D%0A%09%7C+openpar+ArithExpr+closepar+%0D%0A%09%7C+not+Factor+%0D%0A%09%7C+Sign+Factor+%0D%0A%09%7C+qmark+opensqbr+Expr+colon+Expr+colon+Expr+closesqbr+.%0D%0ASign+-%3E+plus+%0D%0A%09%7C+minus+.%0D%0AAParams+-%3E+Expr+AParamsTail+%0D%0A%09%7C+.%0D%0AAParamsTail+-%3E+comma+Expr+AParamsTail+%0D%0A%09%7C+.%0D%0AIdnestStart+-%3E+id+IdnestVarBody+.%0D%0AIdnestVarBody+-%3E+IndiceRep+IdnestVarBodyTail+%0D%0A%09%7C+openpar+AParams+closepar+dot+id+IdnestVarBody+.%0D%0AIdnestVarBodyTail+-%3E+dot+id+IdnestVarBody+%0D%0A%09%7C+.%0D%0AFuncVarStart+-%3E+id+IdnestBody.%0D%0AIdnestBody+-%3E+IndiceRep+IdnestBodyTail%0D%0A%09%7C+openpar+AParams+closepar+IdnestBodyTail+.%0D%0AIdnestBodyTail+-%3E+dot+id+IdnestBody+%0D%0A%09%7C+.%0D%0AFuncVarStartCaveat+-%3E+id+IdnestCaveatBody.%0D%0AIdnestCaveatBody+-%3E+IndiceRep+IdnestCaveatBodyTail%0D%0A%09%7C+openpar+AParams+closepar+IdnestCaveatBodyTailTwo+.%0D%0AIdnestCaveatBodyTail+-%3E+dot+id+IdnestCaveatBody+%0D%0A%09%7C+AssignStat+.%0D%0AIdnestCaveatBodyTailTwo+-%3E+dot+id+IdnestCaveatBody+%0D%0A%09%7C+.%0D%0AIndiceRep+-%3E+opensqbr+ArithExpr+closesqbr+IndiceRep+%0D%0A%09%7C+."
    r = requests.get(url)
    df_list = pd.read_html(r.text)
    df = df_list[2]
    print(df.to_string())


def table():
    url = "https://smlweb.cpsc.ucalgary.ca/ll1-table.php?grammar=START+-%3E+Prog+.%0AProg+-%3E+ClassDecl+FuncDef+main+FuncBody.%0AClassDecl+-%3E+class+id+Inherit+opencubr+ClassDeclBody+closecubr+semi+ClassDecl%0A%09%7C+.%0AFuncDef+-%3E+Function+FuncDef+%0A%09%7C+.%0AFunction+-%3E+FuncHead+FuncBody.%0AInherit+-%3E+inherits+id+NestedId+%0A%09%7C+.%0ANestedId+-%3E+comma+id+NestedId+%0A%09%7C+.%0AVisibility+-%3E+public+%0A%09%7C+private+%0A%09%7C+.%0AMemberDecl+-%3E+FuncDecl+%0A%09%7C+VarDecl+.%0AClassDeclBody+-%3E+Visibility+MemberDecl+ClassDeclBody+%0A%09%7C+.%0AFuncDecl+-%3E+func+id+openpar+FParams+closepar+colon+FuncDeclTail+semi.%0AFuncDeclTail+-%3E+Type+%0A%09%7C+void+.%0AVarDeclRep%09-%3E+VarDecl+VarDeclRep+%0A%09%7C+.%0AVarDecl+-%3E+Type+id+ArraysizeTail+semi+.%0AFParams+-%3E+Type+id+ArraysizeTail+FParamsTail+%0A%09%7C+.%0AType+-%3E+integer+%0A%09%7C+float+%0A%09%7C+string+%0A%09%7C+id+.%0AFParamsTail+-%3E+comma+Type+id+ArraysizeTail+FParamsTail%0A%09%7C+.%0AArraysize+-%3E+opensqbr+IntNum+closesqbr+.%0AArraysizeTail+-%3E+Arraysize+ArraysizeTail+%0A%09%7C+.%0AIntNum+-%3E+intnum+%0A%09%7C+.%0AFuncHead+-%3E+func+id+ClassMethod+openpar+FParams+closepar+colon+FuncDeclTail.%0AFuncBody+-%3E+opencubr+MethodBody+StatementTail+closecubr.%0AClassMethod+-%3E+coloncolon+id+%0A%09%7C+.%0AMethodBody+-%3E+var+opencubr+VarDeclRep+closecubr+%0A%09%7C+.%0AStatementTail+-%3E+Statement+StatementTail+%0A%09%7C+.%0AStatement+-%3E+FuncVarStartCaveat+semi+%0A%09%7C+if+openpar+ArithExpr+closepar+then+StatBlock+else+StatBlock+semi+%0A+%09%7C+while+openpar+ArithExpr+closepar+StatBlock+semi+%0A+%09%7C+read+openpar+IdnestStart+closepar+semi+%0A+%09%7C+write+openpar+Expr+closepar+semi+%0A+%09%7C+return+openpar+Expr+closepar+semi+%0A+%09%7C+break+semi+%0A+%09%7C+continue+semi+.%0AAssignStat+-%3E++AssignOp+Expr.%0AAssignOp+-%3E+assign+.%0AExpr+-%3E+ArithExpr+.%0AArithExpr+-%3E+Term+ArithExprTail+.%0AArithExprTail+-%3E+AddOp+ArithExpr+%0A%09%7C+RelOp+ArithExpr+%0A%09%7C+.%0AStatBlock+-%3E+opencubr+StatementTail+closecubr%0A%09%7C+Statement%0A%09%7C+.%0ARelOp+-%3E+eq+%0A%09%7C+noteq+%0A%09%7C+lt+%0A%09%7C+gt+%0A%09%7C+leq+%0A%09%7C+geq+.%0AAddOp+-%3E+plus+%0A%09%7C+minus+%0A%09%7C+or.%0AMultOp+-%3E+mult+%0A%09%7C+div+%0A%09%7C+and+.%0ATerm+-%3E+Factor+TermTail+.%0ATermTail+-%3E+MultOp+Factor+TermTail+%0A%09%7C+.%0AFactor+-%3E+FuncVarStart+%0A%09%7C+intnum+%0A%09%7C+floatnum+%0A%09%7C+stringlit+%0A%09%7C+openpar+ArithExpr+closepar+%0A%09%7C+not+Factor+%0A%09%7C+Sign+Factor+%0A%09%7C+qmark+opensqbr+Expr+colon+Expr+colon+Expr+closesqbr+.%0ASign+-%3E+plus+%0A%09%7C+minus+.%0AAParams+-%3E+Expr+AParamsTail+%0A%09%7C+.%0AAParamsTail+-%3E+comma+Expr+AParamsTail+%0A%09%7C+.%0AIdnestStart+-%3E+id+IdnestVarBody+.%0AIdnestVarBody+-%3E+IndiceRep+IdnestVarBodyTail+%0A%09%7C+openpar+AParams+closepar+dot+id+IdnestVarBody+.%0AIdnestVarBodyTail+-%3E+dot+id+IdnestVarBody+%0A%09%7C+.%0AFuncVarStart+-%3E+id+IdnestBody.%0AIdnestBody+-%3E+IndiceRep+IdnestBodyTail%0A%09%7C+openpar+AParams+closepar+IdnestBodyTail+.%0AIdnestBodyTail+-%3E+dot+id+IdnestBody+%0A%09%7C+.%0AFuncVarStartCaveat+-%3E+id+IdnestCaveatBody.%0AIdnestCaveatBody+-%3E+IndiceRep+IdnestCaveatBodyTail%0A%09%7C+openpar+AParams+closepar+IdnestCaveatBodyTailTwo+.%0AIdnestCaveatBodyTail+-%3E+dot+id+IdnestCaveatBody+%0A%09%7C+AssignStat+.%0AIdnestCaveatBodyTailTwo+-%3E+dot+id+IdnestCaveatBody+%0A%09%7C+.%0AIndiceRep+-%3E+opensqbr+ArithExpr+closesqbr+IndiceRep+%0A%09%7C+.&substs="
    r = requests.get(url)
    df_list = pd.read_html(r.text)
    df = df_list[1]
    return df


if __name__ == '__main__':
    df = table()
    # print(df.to_string())
    # print(type(df))
    # print(df.get(51))
    print(df.to_string())
    # print(type(df.iloc[[0]]))
    print(df.iloc[1:, 0].values.tolist())
    print(df.iloc[0, 1:].values.tolist())
    print(df.drop([0]))
    ddf = df.drop([0], 0)
    ddf = ddf.drop([0], 1)
    print(ddf.to_string())
    print(df.columns.rename())
    # print(df.to_string())
    ddf = fix_table(df, 1, 1)
    print(ddf.to_string())