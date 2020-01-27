from hash_tag.core.data_loader import FileLine
from hash_tag.tools.helpers import write_json
from hash_tag.tools.logger import logged
from typing import List, Generator
import os
import dataclasses
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclasses.dataclass
class WordOccurrence:
    """
    Helper class for handling the data in a more structured way, It is used mainly at
    WordCounterDict.
    counter: integer where we track the number of word occurrences
    line: the corresponding line
    file_name: the corresponding file name
    """
    counter: int
    lines: list
    file_names: list


class WordCounterDict(dict):
    """
    A custom dict to be able to count all the words in all lines in all input files
    The format of the dict it will be like {"word_token" : WordOccurrence)
    """

    def __init__(self):
        super(WordCounterDict, self).__init__()

    def __setitem__(self, key: str, file_line: FileLine):
        if key not in self:
            dict.__setitem__(self, key, WordOccurrence(counter=1,
                                                       lines=[file_line.line],
                                                       file_names=[file_line.file_name]))
        else:
            # case where we have already seen this words we increase the counter only in
            # different lines
            word_occurrence = self.__getitem__(key)
            if file_line.file_name not in word_occurrence.file_names:
                # same word different file
                word_occurrence.file_names.append(file_line.file_name)
            if file_line.line not in word_occurrence.lines:
                # same word different line
                # update the counter
                word_occurrence.lines.append(file_line.line)
                word_occurrence.counter += 1

            dict.__setitem__(self, key, word_occurrence)


class CalculateCommonWords:
    def __init__(self, results_dir: str, data: List[FileLine], common_criterion: int = 5,
                 debug: bool = False):
        self._results_dir = results_dir
        self.word_dict = WordCounterDict()
        self.debug = debug
        self.criterion = common_criterion
        self._count_words(data=data)

    @logged
    def _count_words(self, data: List[FileLine]) -> None:
        """
        This method will build the word_counter dictionary where we
        count for each unique word in the "data" the number of the occurrence's
        and also we keep track the corresponding lines and files.
        """
        for line in data:
            for word_tokens in line.words:
                self.word_dict[word_tokens] = line
        self._find_common()

    @logged
    def _find_common(self) -> dict:
        """
        This method "filter" the dictionary with words, where one word is consider as common
        if it is appeared in more than 1 file
        """
        self.word_dict = {word: occurrences for word, occurrences
                          in self.word_dict.items() if
                          len(occurrences.file_names) >= self.criterion}
        if self.debug:
            write_json(file_path=os.path.join(self._results_dir, "common_words"),
                       data=self.word_dict)
        return self.word_dict

    @logged
    def show_common(self, top_k: int = 2, file_name: str = "results") -> None:
        """
        Show a bor plat and save as pdf the results after the pipeline
        :param top_k: request number of the results
        :param file_name:
        :raise StopIteration: In case top_k or the criterion is to high.
        """
        common_gen = self._get_common()
        results = []
        for i in range(top_k):
            results.append(next(common_gen))
        # create for each data a list
        words = [word[0] for word in results]
        occurrences = [word[1].counter for word in results]
        lines = [word[1].lines for word in results]
        documents = [word[1].file_names for word in results]
        # Create a figure for the bar plot
        f = plt.figure()
        ax = f.add_subplot()
        ax.bar(words, occurrences, align='center')
        x = np.arange(len(words))
        ax.set_xticks(x)
        ax.tick_params(axis='both', which='major', labelsize=7)
        ax.set_xticklabels(words)
        title = f"top {top_k} #hashtags for #{self.criterion} input files"
        plt.title(title)

        # create a data frame for the csv
        df = pd.DataFrame(list(zip(words, occurrences, lines, documents)),
                          columns=["Words", "#counter", "line/s", "document/s"])

        # create the final file_name
        file_name = f"{file_name}-topk={top_k}-criterion={self.criterion}"

        plt.savefig(os.path.join(self._results_dir, f"{file_name}.pdf"),
                    format='pdf', dpi=1200)

        df.to_csv(os.path.join(self._results_dir, f"{file_name}.csv"),
                  index=None, header=True)
        plt.show()

    @logged
    def _get_common(self) -> Generator:
        """
        Return a generator for common words in a sorted way based on the number of lines = counter
        as a criterion for sorting, yields a tuple where each element is:
        (word,WordOccurrence object)
        """
        words_gen = ((word, values) for word, values in
                     sorted(self.word_dict.items(), key=lambda x: x[1].counter,
                            reverse=True))
        yield from words_gen
