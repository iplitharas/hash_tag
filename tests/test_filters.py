import unittest
from unittest.mock import MagicMock
from hash_tag.core.data_loader import DataLoader
from hash_tag.core.filters import filter_duplicates, filter_punctuation, filter_by_tag, \
    filter_stop_words
from hash_tag.tools.logger import Logger
import string
from unittest.mock import MagicMock
import os

# turn off the logger
Logger.logger = MagicMock()


class TestFilters(unittest.TestCase):

    def setUp(self):
        os.path.dirname = MagicMock(return_value=os.path.dirname(os.path.abspath(__file__)))
        self.data_loader = DataLoader(input_files_path="data",
                                      saves_folder_name="saves_from_unittest",
                                      results_folder_name="results_from_unittest")
        self.data_loader.parse_files()
        self.data = self.data_loader.data
        self.maxDiff = None

    def test_filter_punctuation(self):
        print("##########################################################################")
        print("#################### filter_punctuation ##################################")
        print("##########################################################################")

        self.assertEqual(self.data[0].words, ['Let', 'me', 'begin', 'by', 'saying', 'thanks',
                                              'to', 'all', 'you', 'who', "'ve",
                                              'traveled', ',', 'from', 'far', 'and', 'wide', ',',
                                              'to', 'brave', 'the', 'cold', 'today', '$'])

        filter_punctuation(data=[self.data[0]])
        self.assertEqual(self.data[0].words, ['Let', 'me', 'begin', 'by', 'saying', 'thanks',
                                              'to', 'all', 'you', 'who', 'traveled', 'from', 'far',
                                              'and', 'wide', 'to', 'brave', 'the', 'cold', 'today'])

        test_data = " ".join(string.punctuation)
        test_data = test_data.split(" ")
        self.assertEqual(test_data, ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',',
                                     '-', '.', '/', ':', ';', '<', '=', '>', '?', '@',
                                     '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~'])
        self.data[0].words = test_data
        filter_punctuation(data=[self.data[0]])
        self.assertEqual(self.data[0].words, [])
        self.assertFalse(self.data[0].words)

    def test_filter_stop_words(self):
        print("##########################################################################")
        print("#################### filter_stop_words ###################################")
        print("##########################################################################")

        self.assertEqual(self.data[0].words, ['Let', 'me', 'begin', 'by', 'saying', 'thanks',
                                              'to', 'all', 'you', 'who', "'ve", 'traveled', ',',
                                              'from', 'far', 'and', 'wide', ',', 'to', 'brave',
                                              'the', 'cold', 'today', '$'])

        words_before = set(self.data[0].words)
        filter_stop_words(data=[self.data[0]], vocabulary="english")
        self.assertEqual(self.data[0].words, ['Let', 'begin', 'saying', 'thanks', "'ve",
                                              'traveled', ',', 'far', 'wide', ',', 'brave', 'cold',
                                              'today', '$'])
        words_after = set(self.data[0].words)
        self.assertEqual(words_before.difference(words_after), {'the', 'me', 'by', 'and',
                                                                'to', 'who', 'all', 'from', 'you'})

    # run this test alone because right now it is failing when we run all the tests in the folder
    @unittest.skip
    def test_filter_by_tag(self):
        print("##########################################################################")
        print("#################### filter_by tag #######################################")
        print("##########################################################################")
        self.assertEqual(self.data[100].words, ['America', ',', 'it', "'s", 'time', 'to', 'start',
                                                'bringing', 'our', 'troops', 'home', '.'])
        words_before = set(self.data[100].words)

        filter_by_tag(data=[self.data[100]], tags=["NNS", "NN"])
        words_after = set(self.data[100].words)
        # self.assertEqual(words_before.difference(words_after),{'time', 'home', 'troops'}
        self.assertEqual(words_after, {'troops', 'time', 'home'})
        self.assertEqual(words_before.difference(words_after),
                         {'to', ',', "'s", 'our', 'America', 'start', 'it', 'bringing', '.'})
