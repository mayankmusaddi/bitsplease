from unittest import TestCase
from tools.summarize import summarize


class TestSummarize(TestCase):
    def test_summarize(self):
        num_results = 2
        _results = summarize("what is nyse cxm price today", words=2)
        self.assertEqual(len(_results.split(" ")), num_results)
        print(_results)
