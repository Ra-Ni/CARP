from syntax import analyzer


def panic(parser: analyzer):
    top = parser.ast.peek()
    lookahead = parser.lookahead

    if top.label in parser.terminals:
        parser.errors.append("[{}] SyntaxError: invalid syntax expectation '{}'".format(lookahead.location, top.label))
        parser.ast.pop()
        return

    follow = parser.follow.loc[top.label] or []
    series = parser.ll1.loc[top.label].dropna().index

    parser.errors.append("[%s] SyntaxError: invalid syntax '%s' ∉ %s" % (lookahead.location, lookahead.type, set(series)))

    if lookahead and lookahead.type in follow:
        parser.ast.pop()
    else:
        # lookahead and not (lookahead.type in first or 'ε' in first and lookahead.type in follow)
        while lookahead and lookahead.type not in series:
            lookahead = parser.lookahead = next(parser.tokens, None)

