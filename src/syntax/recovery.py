from syntax import analyzer


def panic(parser: analyzer):
    top = parser._stack[-1]
    lookahead = parser._lookahead

    if top in parser._terminals:
        parser.errors.append("[{}] SyntaxError: invalid syntax expectation '{}'".format(lookahead.location, top))
        parser._stack.pop()
        return

    follow = parser._follow.loc[top] or []
    series = parser.ll1.loc[top].dropna().index

    parser.errors.append("[%s] SyntaxError: invalid syntax '%s' ∉ %s" % (lookahead.location, lookahead.type, set(series)))

    if lookahead and lookahead.type in follow:
        parser._stack.pop()
    else:
        # lookahead and not (lookahead.type in first or 'ε' in first and lookahead.type in follow)
        while lookahead and lookahead.type not in series:
            lookahead = parser._lookahead = next(parser.tokens, None)

