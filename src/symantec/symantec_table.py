from . import *
from syntax import AST


class SymantecTable:
    def __init__(self, error):
        self.error = error

    def parse(self, ast: AST):
        nodes = list(ast.bfs())
        nodes.reverse()

        for node in nodes:
            if node['kind'] in SYS:
                SYS[node['kind']](node)

        # nodes = list(ast.bfs())
        # nodes.reverse()
        #
        # for node in nodes:
        #     if node['kind'] in PHASE2:
        #         PHASE2[node['kind']](node)
