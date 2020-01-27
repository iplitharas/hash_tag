from hash_tag.core.data_loader import FileLine
from hash_tag.core.filters import filter_stop_words, filter_by_tag, \
    filter_punctuation
from hash_tag.tools.helpers import write, restore, write_json
from hash_tag.tools.logger import Logger, logged
import os
from typing import List, Callable


class FilterPipeLine:
    def __init__(self, saves_dir: str, data: List[FileLine], tags: List[str],
                 vocabulary: str, debug: bool = False):
        self._saves_dir = saves_dir
        self._data = data
        self._vocabulary = vocabulary
        self._filters = []
        self._tags = tags
        self._saves = []
        self._debug = debug

    @property
    def data(self):
        return self._data

    @property
    def vocabulary(self):
        return self._vocabulary

    @vocabulary.setter
    def vocabulary(self, new_vocab: str):
        self._vocabulary = new_vocab

    @property
    def saves(self) -> List[str]:
        """
        Returns a list with all the checkpoints founded in saves dir after the filter pipeline
        """
        self._saves = [filter_file for filter_file in os.listdir(self._saves_dir) if
                       filter_file.startswith("filter") and filter_file.endswith(".pickle")]
        return self._saves

    def restore_after_filter(self, filter_name: str) -> List[FileLine]:
        """
        Restore the state from the given checkpoint
        :raise: FileNotFound exception in case it is called with random name outside the app
        """
        self._data = restore(os.path.join(self._saves_dir, filter_name))
        return self._data

    def add_all_filters(self) -> None:
        """
        Appends all possible filters.
        """
        all_filters = (filter_punctuation, filter_stop_words, filter_by_tag)
        for filter_ in all_filters:
            self.add_filter(filter_)

    def add_filter(self, n_filter: Callable) -> None:
        """
        Adds a specific filter
        """
        if callable(n_filter):
            self._filters.append(n_filter)
            Logger.logger.info(f"Successfully added the filter > {n_filter.__name__}")

    @logged
    def apply_filters(self) -> List[FileLine]:
        """
        Run the pipeline of the filters in the extracted data from files.
        """
        pipeline = self._data
        Logger.logger.debug(f"Pipeline is > {self._filters}")
        for n_filter in self._filters:
            pipeline = n_filter(pipeline, vocabulary=self._vocabulary,
                                tags=self._tags)
            if self._debug:
                write(os.path.join(self._saves_dir, f"{n_filter.__name__}"), self._data)
                write_json(os.path.join(self._saves_dir, f"{n_filter.__name__}"), self._data)
        return pipeline

    def __str__(self):
        print(f"{self.__class__.__name__}\n"
              f"saves dir: {self._saves_dir}\n"
              f"vocabulary: {self._vocabulary}\n"
              f"Filters: {self._filters}\n"
              f"Saves: {self.saves}")
        return ""
