from collections import namedtuple

from django.template.base import TextNode, VariableNode
from django.template.defaulttags import (
    CycleNode, FirstOfNode, LoadNode, NowNode, SpacelessNode, URLNode, WidthRatioNode)

_NodeListWrapper = namedtuple("NodeListWrapper", "nodelist")


def _get_vars(filter_expression):
    """
    Return the list of vars used in a django filter expressions. That includes
    the main var and any filter arguments
    """
    if not hasattr(filter_expression.var, 'var'):
        # Probably a string literal or something like that
        result = []
    else:
        result = [filter_expression.var.var]
    for _, arglist in filter_expression.filters:
        result.extend(arg.var for lookup, arg in arglist if lookup)
    return result


def get_context(template):
    """
    Returns a list of context variables used in the template. Each variable is
    represented as a dotted string from the context root.

    The argument is a template object (or anything with a nodelist), not just a filename.
    Note that many nodes have a "nodelist" attribute, so those are accepted here too
    (fact which is used in the recursive implementation)

    For example, passing the template {{ var }} {{ var.attribute }}
    Results in: ["var", "var.attribute"]

    And {% with local=var.attribute %}local.inner{% endwith %}
    Results in: ["var", "var.attribute", "var.attribute.inner"]

    Custom template tags may not be interpreted correctly, but any argument
    to a template tag that isn't quoted is used as a variable.
    """

    result = []
    for node in template.nodelist:
        # Ignored nodes
        if isinstance(node, TextNode):
            # Text is ignored
            pass
        elif isinstance(node, NowNode):
            pass
        elif isinstance(node, LoadNode):
            pass
        # Simple variables
        elif isinstance(node, VariableNode):
            result += _get_vars(node.filter_expression)
        # Nodes with arguments, non-nested
        elif isinstance(node, CycleNode):
            for expr in node.cyclevars:
                result += _get_vars(expr)
        elif isinstance(node, FirstOfNode):
            for expr in node.vars:
                result += _get_vars(expr)
        elif isinstance(node, URLNode):
            if not node.legacy_view_name:  # Django 1.3 new url tag
                result += _get_vars(node.view_name)
            for arg in node.args:
                result += _get_vars(arg)
            for key, arg in node.kwargs.items():
                result += _get_vars(arg)
        elif isinstance(node, WidthRatioNode):
            result += _get_vars(node.val_expr)
            result += _get_vars(node.max_expr)
            result += _get_vars(node.max_width)
        # Nested nodes
        elif isinstance(node, SpacelessNode):
            result += get_context(node)
        # TODO: block (contents)
        # TODO: extends (hard, it's not just the argument but the template should be loaded too)
        # TODO: filter (the arguments, and the content)
        # TODO: for (hard, the iterable, but also the renamings; then the contents. Also, the forllop stuff)
        # TODO: if (the expression, and then the contents on each branch
        # TODO: ifequal, ifnotequal
        # TODO: include (the argument and the content. also the renamings)
        # TODO: regroup (the arg, and renamings)
        # TODO: with: renamings
        else:
            assert False, "Unrecognized node %s" % type(node)
    return result
