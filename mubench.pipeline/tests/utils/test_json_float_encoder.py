import json

from nose.tools import assert_equals

from utils.json_float_encoder import JSONFloatEncoder


class TestJSONFloatEncoder:
    def test_encodes_nan_as_string(self):
        result = json.dumps(float('NaN'), cls=JSONFloatEncoder)

        assert_equals('NaN', result)

    def test_encodes_infinity_as_string(self):
        result = json.dumps(float('inf'), cls=JSONFloatEncoder)

        assert_equals('Infinity', result)

    def test_encodes_negative_infinity_as_string(self):
        result = json.dumps(float('-inf'), cls=JSONFloatEncoder)

        assert_equals('-Infinity', result)

    def test_encodes_float_as_string(self):
        result = json.dumps(42.1337, cls=JSONFloatEncoder)

        assert_equals('42.1337', result)
