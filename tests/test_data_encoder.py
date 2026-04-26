import unittest
import pytest

from pymzm.data_encoder import encode_value, encode_scalar, encode_dict, infer_shape


pytestmark = [pytest.mark.unit]


class _EnumToken:
    def __init__(self, token):
        self._token = token

    def _to_mz_token(self):
        return self._token


class TestDataEncoder(unittest.TestCase):
    def test_scalar_encoding(self):
        self.assertEqual(encode_scalar(True), "true")
        self.assertEqual(encode_scalar(False), "false")
        self.assertEqual(encode_scalar(7), "7")
        self.assertEqual(encode_scalar(2.5), "2.5")
        self.assertEqual(encode_scalar('hello "mzn"'), '"hello \\\"mzn\\\""')

    def test_enum_and_optional_encoding(self):
        token = _EnumToken("GREEN")
        self.assertEqual(encode_scalar(token), "GREEN")
        self.assertEqual(encode_scalar("GREEN", is_enum_type=True), "GREEN")
        self.assertEqual(encode_scalar(None), "<>")

    def test_collection_encoding(self):
        self.assertEqual(encode_value({3, 1, 2}), "{1, 2, 3}")
        self.assertEqual(encode_value([1, 2, 3]), "[1, 2, 3]")
        self.assertEqual(encode_value((4, 5)), "[4, 5]")

    def test_nested_array_encoding(self):
        values_2d = [[1, 2], [3, 4]]
        values_3d = [[[1], [2]], [[3], [4]]]

        self.assertEqual(encode_value(values_2d), "[|1, 2|3, 4|]")
        self.assertEqual(
            encode_value(values_3d),
            "array3d(1..2, 1..2, 1..1, [1, 2, 3, 4])",
        )

    def test_dict_encoding(self):
        self.assertEqual(
            encode_dict({2: 20, 1: 10}),
            "[1: 10, 2: 20]",
        )

    def test_shape_inference(self):
        self.assertEqual(infer_shape(5), None)
        self.assertEqual(infer_shape([1, 2, 3]), (3,))
        self.assertEqual(infer_shape([[1, 2], [3, 4]]), (2, 2))


if __name__ == "__main__":
    unittest.main()
