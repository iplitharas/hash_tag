import unittest
from unittest.mock import MagicMock
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hash_tag.core.common_words import WordCounterDict, CalculateCommonWords
from hash_tag.core.data_loader import DataLoader, FileLine


class TestDataLoader(unittest.TestCase):
    def setUp(self):
        os.path.dirname = MagicMock(return_value=os.path.dirname(os.path.abspath(__file__)))
        self.data_loader = DataLoader(input_files_path="data",
                                      saves_folder_name="saves_from_unittest",
                                      results_folder_name="results_from_unittest")

        self.maxDiff = None

    def test_word_counter_dict(self):
        print("##########################################################################")
        print("#################### test word counter dict ##############################")
        print("##########################################################################")
        # In the word counter dict we add each word from FileLine object
        # FileLine.words(list) and as value:
        # 1) the counter= len(different lines)
        # 2)the corresponding line and
        # 3)file
        # as an WordOccurrence object
        word_counter = WordCounterDict()
        self.assertTrue(isinstance(word_counter, dict))
        test_data = self.data_loader.data[0]
        self.assertTrue(isinstance(test_data, FileLine))
        self.assertEqual(test_data.words, ['Let', 'me', 'begin', 'by', 'saying', 'thanks', 'to',
                                           'all', 'you', 'who', "'ve", 'traveled', ',', 'from',
                                           'far', 'and', 'wide', ',', 'to', 'brave', 'the',
                                           'cold', 'today', '$'])
        self.assertEqual(test_data.line,
                         "Let me begin by saying thanks to all you who've traveled, "
                         "from far and wide, to brave the cold today$")
        self.assertEqual(test_data.file_name, 'doc1.txt')

        for word_tokens in test_data.words:
            word_counter[word_tokens] = test_data

        self.assertIn("Let", word_counter)
        self.assertEqual(word_counter["Let"].counter, 1)
        self.assertEqual(word_counter["Let"].lines, ["Let me begin by saying thanks to all "
                                                     "you who've traveled, from far "
                                                     "and wide, to brave the cold today$"])
        self.assertEqual(word_counter["Let"].file_names, ['doc1.txt'])

        # add again the Let word, same word same line and file we don't increase the counter
        test_data.words.append("Let")
        for word_tokens in test_data.words:
            word_counter[word_tokens] = test_data

        self.assertEqual(word_counter["Let"].counter, 1)
        self.assertEqual(word_counter["Let"].lines, ["Let me begin by saying thanks to all "
                                                     "you who've traveled, from far "
                                                     "and wide, to brave the cold today$"])
        self.assertEqual(word_counter["Let"].file_names, ['doc1.txt'])

        # add new file , again we don't increase the counter we append only the new file
        test_data.file_name = "test_file.txt"
        test_data.words.append("Let")
        for word_tokens in test_data.words:
            word_counter[word_tokens] = test_data

        self.assertEqual(word_counter["Let"].counter, 1)
        self.assertEqual(word_counter["Let"].lines, ["Let me begin by saying thanks to all "
                                                     "you who've traveled, from far "
                                                     "and wide, to brave the cold today$"])

        self.assertEqual(word_counter["Let"].file_names, ['doc1.txt', 'test_file.txt'])

        # add new line , we increase the counter = len(different lines)
        test_data.line = "Test line!"
        for word_tokens in test_data.words:
            word_counter[word_tokens] = test_data

        self.assertEqual(word_counter["Let"].counter, 2)
        self.assertEqual(word_counter["Let"].counter, len(word_counter['Let'].lines))
        self.assertEqual(word_counter['Let'].lines, ["Let me begin by saying thanks to all you w"
                                                     "ho've traveled, from far and wide, to"
                                                     " brave the cold today$",
                                                     'Test line!'])
        self.assertEqual(word_counter["Let"].file_names, ['doc1.txt', 'test_file.txt'])
