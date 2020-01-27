from nltk.tokenize import word_tokenize, sent_tokenize
import dataclasses
import os
import sys
from hash_tag.tools.helpers import restore, write
from hash_tag.tools.logger import Logger, logged
from typing import Iterable, List, Generator

try:
    import nltk

    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
except LookupError as e:
    Logger.logger.error(f"Cannot continue: {e}")
    sys.exit()


@dataclasses.dataclass
class FileLine:
    """
    a struct like class
    words: a list with all the extracted words from nltk word_tokenize
    line: the corresponding line
    file_name: the corresponding file name
    """
    words: list
    line: str
    file_name: str


class DataLoader:
    def __init__(self, input_files_path: str, saves_folder_name: str = "saves",
                 results_folder_name: str = "results"):
        self._saves_dir = None
        self._result_dir = None
        self._data = None
        self._files_to_parse = []
        self._total_data = 0
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_path = os.path.dirname(self.current_dir)
        self._validate_input_files(files_path=input_files_path)
        self._make_directories(saves_folder_name=saves_folder_name,
                               results_folder_name=results_folder_name)

    @property
    def saves_dir(self):
        return self._saves_dir

    @property
    def results_dir(self):
        return self._result_dir

    @property
    def total(self):
        return len(self._files_to_parse)

    @property
    def data(self):
        try:
            self._data = restore(os.path.join(self._saves_dir, "extracted_tokens.pickle"))
        except FileNotFoundError as e:
            Logger.logger.debug(f"{e}\nParsing input files..")
            self._data = self.parse_files()
            write(os.path.join(self._saves_dir, "extracted_tokens"), self._data)
        finally:
            self._total_data = len(self._data)
        return self._data

    def _make_directories(self, saves_folder_name: str, results_folder_name: str) -> None:
        """
        Creates the directory for, the saves(pickle and json files after applying the filters)
        and for the final results)
        """
        saves_dir = None
        results_dir = None
        try:
            saves_dir = os.path.join(self.parent_path, saves_folder_name)
            results_dir = os.path.join(self.parent_path, results_folder_name)
            os.mkdir(saves_dir)
            os.mkdir(results_dir)
        except FileExistsError:
            Logger.logger.debug(f"Folder name: {saves_folder_name} for saves already exists.")
            Logger.logger.debug(f"Folder name: {results_folder_name} for results already exists.")
        else:
            Logger.logger.debug(f"Successfully created the folder: {saves_folder_name}")
            Logger.logger.debug(f"Successfully created the folder: {results_folder_name}")
        finally:
            self._saves_dir = saves_dir
            self._result_dir = results_dir

    def _validate_input_files(self, files_path: str) -> None:
        """
        This method validates if the path for input files to parse exists and
        then add all text files in a list.
        """
        files_path = os.path.join(self.parent_path, files_path)
        if not os.path.exists(files_path):
            raise Exception(f"Path for input files folder:{files_path} does not exist")
        else:
            # @TODO right now parse only .txt files
            files = [file for file in os.listdir(files_path) if
                     file.endswith(".txt")]
            self._files_to_parse = [os.path.join(files_path, file) for file in files]

    @logged
    def parse_files(self) -> List[FileLine]:
        """
        This method will parse all the input files and returns a list of FileLine objects
        we follow this approach because for each sentence in file we need the extracted word
        tokens and also a "reference" of the corresponding line and file.
        """
        results = []
        for line, file_path in self._file_generator(files=self._files_to_parse):
            file_name = self.restore_file_name(file_path)
            for tokens in self._tokenize_line(line=line):
                file_line = FileLine(*tokens, file_name=file_name)
                results.append(file_line)
        return results

    @staticmethod
    def _file_generator(files: Iterable) -> Generator:
        for file in files:
            with open(file, encoding="utf8") as file_reader:
                for line in file_reader:
                    yield line.strip(), file

    @staticmethod
    def _tokenize_line(line: str) -> Generator:
        """
        This method use the nltk methods sent_tokenize and word_tokenize to extract all of the words
        of the given sentence it's useful because no matter what kind of punctuation we have in
        the sentence,it is able to split them and extract the word tokens.
        """
        tokens = ((word_tokenize(token), token) for token in sent_tokenize(line))
        yield from tokens

    @staticmethod
    def restore_file_name(file_path: str) -> str:
        if sys.platform == "win32":
            file_path = file_path[file_path.rfind("\\") + 1:]
        else:
            file_path = file_path[file_path.rfind("/") + 1:]
        return file_path

    def __str__(self):
        print(f"Current directory:{self.current_dir}\n"
              f"Successfully loaded files to parse: {self._files_to_parse}\n"
              f"Save dir(contains the pickled saves): {self._saves_dir}\n"
              f"Total number of documents: #{self.total}")
        return ""
