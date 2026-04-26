import unittest
from pathlib import Path

import pytest

import pymzm


pytestmark = [pytest.mark.unit]


class TestModuleBoundaries(unittest.TestCase):
    def test_misc_module_does_not_import_expression_directly(self):
        misc_path = Path(__file__).resolve().parents[1] / "src" / "pymzm" / "misc.py"
        content = misc_path.read_text(encoding="utf-8")

        self.assertNotIn("from .expression import", content)

    def test_variable_iterable_to_string_works_without_expression_instance(self):
        class Named:
            def __init__(self, name):
                self.name = name

        values = [Named("a"), "b", 3]
        rendered = pymzm.variableIterable2Str(values)

        self.assertEqual(rendered, "[a, b, 3]")


if __name__ == "__main__":
    unittest.main()
