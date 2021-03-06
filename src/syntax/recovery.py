from syntax import analyzer


def panic(parser: analyzer):
    top = parser.stack[-1]
    lookahead = parser.lookahead

    if top in parser.terminals:
        parser.errors.append("[{}] SyntaxError: invalid syntax expectation '{}'".format(lookahead.location, top))
        parser.stack.pop()
        return

    follow = parser.follow.loc[top] or []
    series = parser.ll1.loc[top].dropna().index

    parser.errors.append("[%s] SyntaxError: invalid syntax '%s' ∉ %s" % (lookahead.location, lookahead.type, set(series)))

    if lookahead and lookahead in follow:
        parser.stack.pop()
    else:
        # lookahead and not (lookahead.type in first or 'ε' in first and lookahead.type in follow)
        while lookahead and lookahead.type not in series:
            lookahead = parser.lookahead = next(parser.tokens, None)

