import unittest

from test_expression import TestExpression
from test_examples import TestExamples
from test_misc import TestMisc
    

if __name__ == "__main__":
    print("".join("\n" for _ in range(10)))

    suite = unittest.TestLoader().discover("tests", "test_*.py")

    unittest.TextTestRunner().run(suite)