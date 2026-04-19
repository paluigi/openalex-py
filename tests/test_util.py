from __future__ import annotations

from openalexpy.util import invert_abstract


class TestInvertAbstract:
    def test_basic(self):
        result = invert_abstract({"Hello": [0], "world": [1]})
        assert result == "Hello world"

    def test_multi_position(self):
        idx = {"The": [0, 3], "quick": [1], "brown": [2], "fox": [4]}
        result = invert_abstract(idx)
        assert result == "The quick brown The fox"

    def test_none(self):
        assert invert_abstract(None) is None

    def test_empty(self):
        assert invert_abstract({}) == ""

    def test_complex_abstract(self):
        idx = {
            "Abstract": [0],
            "We": [1],
            "present": [2],
            "a": [3, 6],
            "novel": [4],
            "approach": [5],
            "to": [7],
            "solve": [8],
            "problem": [9],
        }
        result = invert_abstract(idx)
        assert result.startswith("Abstract We present")
        assert result.endswith("problem")
