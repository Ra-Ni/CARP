import logging
import uuid

from syntax import *
from .preprocessor import *
from .postprocessor import *


class SymantecTable(AST):
    def __init__(self, root: Node):
        super().__init__(root)

    @classmethod
    def from_ast(cls, ast: AST, error_handler: logging.FileHandler = None):
        logger = logging.getLogger(str(uuid.uuid4()))
        if error_handler:
            logger.addHandler(error_handler)
            logger.setLevel(error_handler.level)
        else:
            logger.setLevel(logging.CRITICAL)

        SYS['log'] = PHASE2['log'] = logger

        nodes = list(ast.bfs())
        nodes.reverse()

        for node in nodes:
            if node['kind'] in SYS:
                SYS[node['kind']](node)

        nodes = list(ast.bfs())
        nodes.reverse()

        for node in nodes:
            if node['kind'] in PHASE2:
                PHASE2[node['kind']](node)

        return cls(ast.root)
