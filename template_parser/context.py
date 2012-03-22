from django.template.base import TextNode, VariableNode

def get_context(template):
    """
    Returns a list of context variables used in the template. Each variable is
    represented as a dotted string from the context root.

    The argument is a template object, not just a filename

    For example, passing the template {{ var }} {{ var.attribute }}
    Results in: ["var", "var.attribute"]

    And {% with local=var.attribute %}local.inner{% endwith %}
    Results in: ["var", "var.attribute", "var.attribute.inner"]

    Custom template tags may not be interpreted correctly, but any argument
    to a template tag that isn't quoted is used as a variable.
    """

    result = []
    for node in template.nodelist:
        if isinstance(node, TextNode):
            pass  # Text is ignored
        elif isinstance(node, VariableNode):
            result.append(node.filter_expression.var.var)
        else:
            print node
    return result
