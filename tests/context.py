from unittest import TestCase, main
from django.template import Template
from django.conf import settings

from template_parser import context

# Configure django to be able to use the templates outside a django project
settings.configure()


class ContextTest(TestCase):

    def test_simple_vars(self):
        t = Template("{{ var1 }}Some text{{ var2 }}")
        vars = context.get_context(t)
        self.assertEqual(vars, ["var1", "var2"])

if __name__ == '__main__':
    main()
