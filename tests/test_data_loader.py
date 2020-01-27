import unittest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from hash_tag.core.data_loader import DataLoader, FileLine
from hash_tag.tools.logger import Logger
from typing import Generator

# turn off the logger
Logger.logger = MagicMock()


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        os.path.dirname = MagicMock(return_value=os.path.dirname(os.path.abspath(__file__)))
        self.data_loader = DataLoader(input_files_path="data",
                                      saves_folder_name="saves_from_unittest",
                                      results_folder_name="results_from_unittest")
        self.maxDiff = None

    def test_property_methods(self):
        print("##########################################################################")
        print("#################### test property methods ###############################")
        print("##########################################################################")
        os.path.exists = MagicMock(return_value=True)
        self.assertTrue(self.data_loader.saves_dir)
        self.assertTrue(os.path.exists(self.data_loader.saves_dir))
        self.assertTrue(self.data_loader.results_dir)
        self.assertTrue(os.path.exists(self.data_loader.results_dir))
        self.assertEqual(self.data_loader.total, 6)
        with self.assertRaises(Exception) as exception:
            self.data_loader = DataLoader(input_files_path="data123",
                                          saves_folder_name="saves_from_unittest",
                                          results_folder_name="results_from_unittest")
        self.assertTrue(exception.exception)

    def test_file_generator(self):
        print("##########################################################################")
        print("#################### test file generator   ###############################")
        print("##########################################################################")

        self.assertTrue(len(self.data_loader._files_to_parse), 6)
        file_generator = self.data_loader._file_generator(self.data_loader._files_to_parse)
        self.assertTrue(isinstance(file_generator, Generator))
        # get first line of first document
        line, file = next(file_generator)
        self.assertEqual(line, "Let me begin by saying thanks to all you who've traveled, "
                               "from far and wide, to brave the cold today$")
        self.assertIn("doc1.txt", file)
        # get second line of second document
        for i in range(46):
            line, file = next(file_generator)

        self.assertEqual(line, "To Chairman Dean and my great friend Dick Durbin; and to all my "
                               "fellow citizens of this great nation;")
        self.assertIn("doc2.txt", file)

        # get first line of third document
        for i in range(88):
            line, file = next(file_generator)

        self.assertEqual(line, "Thank you. Thank you Roger Hickey and Bob Borosage for bringing us "
                               "all together today and thank you for your leadership in the "
                               "cause of a more progressive America.")
        self.assertIn("doc3.txt", file)

        # get first line of 4th document
        for i in range(77):
            line, file = next(file_generator)
        self.assertEqual(line, "The first time I came to Kenya was in 1987. I had just finished "
                               "three years of work as a community organizer in low-income "
                               "neighborhoods of Chicago, and was about to enroll in law school."
                               " My sister, Auma, was teaching that year at this university, "
                               "and so I came to stay with her for a month.")
        self.assertIn("doc4.txt", file)

        # first line 5th document
        for i in range(53):
            line, file = next(file_generator)
        self.assertEqual(line,
                         "Throughout American history, there have been moments that call on us"
                         " to meet the challenges of an uncertain world, and pay whatever "
                         "price"
                         " is required to secure our freedom. They are the soul-trying times "
                         "our forbearers spoke of, when the ease of complacency and self-interest"
                         " must give way to the more difficult task of rendering judgment on "
                         "what is best for the nation and for posterity, and then acting on "
                         "that judgment ? making the hard choices and sacrifices necessary "
                         "to uphold our most deeply held values and ideals.")
        self.assertIn("doc5.txt", file)
        # first line 6th document
        for i in range(56):
            line, file = next(file_generator)

        self.assertEqual(line, "Good morning. As some of you know, Senator Lugar and I recently "
                               "traveled to Russia, Ukraine, and Azerbaijan to witness firsthand"
                               " both the progress we're making in securing the world's most "
                               "dangerous weapons, as well as the serious challenges that lie ahead.")
        self.assertIn("doc6.txt", file)

    def test_restore_file_name(self):
        print("##########################################################################")
        print("#################### test restore_file_name ##############################")
        print("##########################################################################")
        self.assertEqual("doc6.txt", self.data_loader.restore_file_name("\data\doc6.txt"))
        sys.platform = MagicMock()
        sys.platform = "linux"
        self.assertEqual("doc6.txt", self.data_loader.restore_file_name("/data/doc6.txt"))

    def test_tokenize_line(self):
        print("##########################################################################")
        print("#################### test tokenize line ##################################")
        print("##########################################################################")
        line = "Let me begin by saying thanks to all you who've traveled, from far and wide," \
               " to brave the cold today$"
        tokenizer = self.data_loader._tokenize_line(line)
        words, line = next(tokenizer)
        self.assertTrue(words)
        self.assertEqual(len(words), 24)
        self.assertTrue(isinstance(words, list))
        with self.assertRaises(StopIteration):
            next(tokenizer)

        line = "The first time I came to Kenya was in 1987. I had just finished"
        "three years of work as a community organizer in low-income "
        "neighborhoods of Chicago, and was about to enroll in law school."
        " My sister, Auma, was teaching that year at this university, "
        "and so I came to stay with her for a month."
        tokenizer = self.data_loader._tokenize_line(line)
        words, line = next(tokenizer)
        self.assertTrue(words)
        self.assertEqual(len(words), 11)
        self.assertEqual(line, "The first time I came to Kenya was in 1987.")
        words, line = next(tokenizer)
        self.assertTrue(words)
        self.assertEqual(len(words), 4)
        self.assertEqual(line, "I had just finished")
        # we read line by line so the next raise stopIteration
        with self.assertRaises(StopIteration):
            next(tokenizer)

    def test_file_line_object(self):
        print("##########################################################################")
        print("#################### fileLine_object #####################################")
        print("##########################################################################")
        with self.assertRaises(TypeError):
            file_line = FileLine()

        line = "The first time I came to Kenya was in 1987. I had just finished"
        "three years of work as a community organizer in low-income "
        "neighborhoods of Chicago, and was about to enroll in law school."
        " My sister, Auma, was teaching that year at this university, "
        "and so I came to stay with her for a month."

        tokenizer = self.data_loader._tokenize_line(line)
        for tokens in tokenizer:
            file_line = FileLine(*tokens, file_name="test_file_name")
        self.assertTrue(file_line)
        self.assertTrue(file_line.words)
        self.assertEqual(file_line.words, ['I', 'had', 'just', 'finished'])
        self.assertTrue(file_line.line)
        self.assertEqual(file_line.line, 'I had just finished')
        self.assertTrue(file_line.file_name, "test_file_name")
