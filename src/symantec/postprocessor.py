import logging
from syntax import Node


def _search(node: Node, item: str = None):
    parent = node.parent

    query = node['name']
    if item:
        query = item

    while True:
        if not parent:
            node.parent.children.remove(node)
            return None
        if 'table' not in parent or query not in parent['table'].index:
            parent = parent.parent
            continue
        break

    return parent['table'].loc[query]


def _variable(node: Node):
    if 'type' in node:
        return

    table = _search(node, node['name'])
    node['type'] = None if table is None else table['type']

    if 'index' in node:
        node['type'] = node['type'].replace('[]', '', len(node['index']))


def _binop(node: Node, type: str):
    if len(node.children) != 2:
        # PHASE2['log'].error(f'ERROR::{type}::Unresolved object {node.children[0]["name"]}')
        return

    first, second = node.children
    if 'type' in first and 'type' in second:
        first, second = first['type'], second['type']
        if first != second:
            PHASE2['log'].error(f'ERROR::{type.upper()}::Type mismatch {first} and {second}')
        else:
            node['type'] = first


def _sign(node: Node):
    child = node.children.pop()
    if node['name'] == '-':
        child['name'] = node['name'] + child['name']

    node.update(child)


def _args(node: Node):
    node.parent['parameters'] = [x['type'] for x in node.children]


def _function(node: Node):
    if 'table' in node:
        return

    if node.parent['kind'] != 'dot':
        series = _search(node, node['name'])
        if series is not None:
            param, out = series['type'].split(' : ')
            param = param.split(', ')

            if 'parameters' not in node:
                node['parameters'] = []

            if param == node['parameters']:
                node['type'] = out

            else:
                PHASE2['log'].error(
                    f'ERROR::FUNCTION::Parameters {param} for function {node["name"]} do not match {node["parameters"]}')
            node.drop('parameters')
        else:
            PHASE2['log'].error(f'ERROR::FUNCTION::Function {node["name"]} not found')


def dot(node: Node):
    if len(node.children) != 2:
        # PHASE2['log'].error(f'ERROR::DOT::Unresolved object {node.children[0]["name"]}')
        return

    first, second = node.children
    reference = _search(first, first['type'])

    if reference is None:
        PHASE2['log'].error(
            f'ERROR::DOT::Function/Variable call made on object {first["name"]} of type {first["type"]}')
        return

    if second['name'] not in reference['link']['table'].index:
        PHASE2['log'].error(f'ERROR::DOT::object {second["name"]} does not exist in {first["name"]}')
        return

    reference = reference['link']
    reference = reference['table'].loc[second['name']]

    if second['kind'] != reference['kind']:
        PHASE2['log'].error(f'ERROR::DOT::object kind {second["name"]} conflicts in {first["name"]}')
        return
    # if reference['visibility'] == 'private':
    #     PHASE2['log'].error(f'ERROR::DOT::object {second["name"]} in {first["name"]} is private')
    #     return

    if second['kind'] == 'variable':
        node['type'] = second['type']
    else:
        parameters, returns = reference['type'].split(' : ')
        if parameters.split(', ') != second['parameters']:
            node_params = '' if 'parameters' not in node else node['parameters']
            PHASE2['log'].error(
                f'ERROR::FUNCTION::Parameters {parameters} for function {node["name"]} do not match {node_params}')
            return

        node['type'] = returns


def _returns(node: Node):
    if len(node.children) != 1:
       #PHASE2['log'].error(f'ERROR::RETURN::Unresolved object {node.children[0]["name"]}')
        return

    node['type'] = node.children[0]['type']

    current = node
    while 'table' not in current:
        current = current.parent

    _, return_type = current['type'].split(' : ')
    if return_type != node.children[0]['type']:
        PHASE2['log'].error(
            f'ERROR::RETURN::function {current["name"]} returns {return_type}, but given {node.children[0]["type"]}')


PHASE2 = {
    'log': logging.getLogger('phase2'),
    'variable': _variable,
    'multop': lambda x: _binop(x, 'multop'),
    'sign': _sign,
    'args': _args,
    'function': _function,
    'dot': dot,
    'addop': lambda x: _binop(x, 'addop'),
    'assign': lambda x: _binop(x, 'assign'),
    'relop': lambda x: _binop(x, 'relop'),
    'return': _returns,

}
