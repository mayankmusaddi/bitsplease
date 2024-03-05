from unittest import TestCase
from tools.web_search import web_search


class TestWebSearch(TestCase):
    def test_web_search(self):
        num_results = 2
        _results = web_search("who are c suite exectuives for dell?", num_results)
        assert len(_results) == num_results
        assert "title" in _results[0]
        print(_results)
