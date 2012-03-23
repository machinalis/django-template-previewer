from unittest import TestCase, main
import os.path

from django.template import Template
from django.conf import settings

from template_parser import context

# Configure django to be able to use the templates outside a django project
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
settings.configure(TEMPLATE_DIRS=(os.path.join(BASE_PATH, 'templates'),))


class ContextTest(TestCase):

    def test_simple_vars(self):
        t = Template("{{ var1 }}Some text{{ var2 }}")
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

    def test_chained_vars(self):
        t = Template("{{ var1.attribute1.inner_attribute2 }}")
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1.attribute1.inner_attribute2"])

    def test_filtered_vars(self):
        t = Template('{{ var1|default:"Nothing" }}Some text{{ var2|add:"3" }}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

    def test_filtered_constants(self):
        t = Template('{{ "constant"|default:var1 }}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1"])

    def test_filter_arguments(self):
        t = Template('{{ var1|default:var3 }}Some text{{ var2|add:var4 }}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var3", "var2", "var4"])

    def test_simple_tag(self):
        t = Template('{% cycle var1 "text" var2 %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

    def test_block_tag(self):
        t = Template("""
            {% spaceless %}
                This text contains a {{ var }} inside
            {% endspaceless %}
        """)
        vars = context.get_context(t)
        self.assertEqual(vars, ["var"])

    # Tests for specific tags, not covered above
    def test_extends(self):
        t = Template('{% extends "base.html" %}{{ var2 }}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

    def test_filter(self):
        t = Template('{% filter lower|default:x %}{{ y }}{% endfilter %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["x", "y"])

    def test_firstof(self):
        t = Template('{% firstof var1 "text" var2 %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

    def test_if(self):
        t = Template("""
            {% if not var1 and var2 in var3 %}
                {{ then_var }}
            {% else %}
                {{ else_var }}
            {% endif %}
        """)
        vars = context.get_context(t)
        self.assertEqual(
            vars,
            ["var1", "var2", "var3", "then_var", "else_var"]
        )

    def test_ifequal(self):
        t = Template("""
            {% ifequal var1 var2 %}
                {{ then_var }}
            {% else %}
                {{ else_var }}
            {% endifequal %}
        """)
        vars = context.get_context(t)
        self.assertEqual(
            vars,
            ["var1", "var2", "then_var", "else_var"]
        )

    def test_ifchanged(self):
        t = Template("""
            {% ifchanged var1 var2 %}
                {{ then_var }}
            {% else %}
                {{ else_var }}
            {% endifchanged %}
        """)
        vars = context.get_context(t)
        self.assertEqual(
            vars,
            ["var1", "var2", "then_var", "else_var"]
        )

    def test_url(self):
        t = Template('{% url view var1 arg=var2 %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])
        # Django 1.5 format:
        t = Template('{% load url from future %}{% url view var1 arg=var2 %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["view", "var1", "var2"])

    def test_widthratio(self):
        t = Template('{% widthratio var1 var2 var3 %}')
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2", "var3"])

if __name__ == '__main__':
    main()
