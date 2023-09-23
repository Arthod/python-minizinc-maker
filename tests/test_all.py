import unittest

from test_expression import TestExpression
from test_examples import TestExamples
from test_misc import TestMisc
    

if __name__ == "__main__":
    suite = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=1).run(suite)