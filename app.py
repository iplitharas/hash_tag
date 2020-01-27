import cmd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hash_tag.core.filters import filter_punctuation, filter_by_tag, \
    filter_stop_words, filter_duplicates
from hash_tag.core.filter_pipeline import FilterPipeLine
from hash_tag.core.stem import stem_words
from hash_tag.core.common_words import CalculateCommonWords
from hash_tag.core.data_loader import DataLoader


class HastTagApp(cmd.Cmd):
    intro = "*" * 100 + "\nWelcome to the #HashTag shell\n" \
                        "Type help or ? to list commands.\n"
    prompt = ">>> "

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.debug = True
        self.data = None
        self.filter_pipeline = None
        self.common_words = None
        self.data_loader = DataLoader(input_files_path="data")
        self.vocabulary = "english"
        self.common_criterion = 6
        self.top_k = 10
        self.results_file_name = "results"
        self.tags = ["NNS", "NN"]
        self.stemmer = "lancaster"

    def do_parse(self, _) -> None:
        """
        Parse all the input files,Entry point if there are no previous checkpoints.
        :param _: No parameters
        :return:
        """
        self.data = self.data_loader.data

    def do_print_settings(self, _) -> None:
        """
        Print's the current settings
        :param _: No parameters
        """
        print(f"Criterion is: {self.common_criterion}\n"
              f"Vocabulary is: {self.vocabulary}\n"
              f"Results file name is: {self.results_file_name}\n"
              f"Words tags to keep :{self.tags}\n"
              f"Stemmer is: {self.stemmer}\n"
              f"Showing result for top: {self.top_k}")

    def do_total_input_files(self, _) -> None:
        """
        Prints the total input files, it is also used check the maximum
        common_criterion
        :param _: No parameters
        """
        print(f"{self.data_loader}")

    def do_set_vocabulary(self, vocabulary) -> None:
        """
        Set the vocabulary language for for nltk method of step words
        default value: english
        :param vocabulary:
        """
        self.vocabulary = vocabulary
        print(f"Updating the vocabulary to: {self.vocabulary}")

    def do_set_stemmer(self, stemmer) -> None:
        """
        Change the default value of the stemmer:supporting are the porter and lancaster
        :param stemmer: an str
        :return:
        """
        self.stemmer = stemmer.lower()
        print(f"New stemmer is: {self.stemmer}")

    def do_stem(self, _) -> None:
        try:
            self.data = stem_words(self.data_loader.data, vocabulary=self.vocabulary,
                                   stemmer=self.stemmer,
                                   saves_dir=self.data_loader.saves_dir,
                                   debug=self.debug)
        except TypeError as e:
            print(f"Error trying top apply the stem: {e}")

    def do_set_tags(self, tags) -> None:
        """
        Update the tags where the filter by tag method will keep for the word tokens
        :param tags: space separated stings example NNS IN NN
        """
        self.tags = [tag.upper() for tag in tags.split(" ")]
        print(f"New tags are: {self.tags}")

    def do_add(self, _) -> None:
        """
        Add a specific filter one by one, useful to check the results per filter
        :param _: No parameters
        """
        if not self.filter_pipeline:
            self.filter_pipeline = FilterPipeLine(saves_dir=self.data_loader.saves_dir,
                                                  data=self.data_loader.data,
                                                  tags=self.tags,
                                                  vocabulary=self.vocabulary,
                                                  debug=self.debug)
        supported_filters = {
            "1": filter_punctuation,
            "2": filter_duplicates,
            "3": filter_stop_words,
            "4": filter_by_tag}
        while True:
            print(f"0:exit")
            for key, value in supported_filters.items():
                print(f"{key}:{value.__name__}")
            choice = input(">ADD? ")
            if choice in supported_filters:
                self.filter_pipeline.add_filter(supported_filters[choice])
            if choice == "0":
                return

    def do_add_all(self, _) -> None:
        """
        Add all the filters in the pipeline:
        It re-initialize the object
        Pipeline order is:(filter_punctuation, filter_stop_words, filter_by_tag)
        :param _: No parameters
        """
        self.filter_pipeline = FilterPipeLine(saves_dir=self.data_loader.saves_dir,
                                              data=self.data_loader.data,
                                              tags=self.tags,
                                              vocabulary=self.vocabulary,
                                              debug=self.debug)
        self.filter_pipeline.add_all_filters()
        self.data = self.filter_pipeline.data

    def do_apply(self, _) -> None:
        """
        Run the pipeline of filtering the data for the requested filters.
        :param _: No parameters
        """
        try:
            print(f"{self.filter_pipeline}")
            self.filter_pipeline.vocabulary = self.vocabulary
            self.filter_pipeline.apply_filters()
            # update the common data
            self.data = self.filter_pipeline.data
        except AttributeError as e:
            print(f"You need to add a filter first:{e}")

    def do_restore(self, _) -> None:
        """
        Restore the state from previous filtering checkpoint.
        :param _: No parameters
        """
        self.filter_pipeline = FilterPipeLine(saves_dir=self.data_loader.saves_dir,
                                              data=self.data_loader.data,
                                              tags=self.tags,
                                              vocabulary=self.vocabulary,
                                              debug=self.debug)
        if self.filter_pipeline.saves:
            checkpoints_dict = {str(key): value for
                                (key, value) in enumerate(self.filter_pipeline.saves)}
            print(f"Possible save points: {checkpoints_dict}")
            save_point = input("Restore from?: ")
            if save_point in checkpoints_dict:
                self.data = self.filter_pipeline.restore_after_filter(checkpoints_dict[save_point])
        else:
            print(f"No save points founded!")

    def do_set_criterion(self, criterion) -> None:
        """
        Set the criterion for the calculation of the common words.
        :param criterion: in needs to be an integer between 1 <> max_size of input data files
        """
        if int(criterion) > self.data_loader.total:
            print(f"Criterion must be at most {self.data_loader.total}")
        else:
            self.common_criterion = int(criterion)
            print(f"New common criterion is: {self.common_criterion}")

    def do_set_top(self, top_k) -> None:
        """
        Specify the number for the results to be calculated
        :param top_k: integer
        """
        self.top_k = int(top_k)
        print(f"New top_k is:{self.top_k}")

    def do_set_results_file_name(self, file_name) -> None:
        """
        Specify the the file name of the final result both for pdf with the bar chart and json.
        :param file_name: str
        """
        self.results_file_name = file_name
        print(f"New file name for results: {self.results_file_name}")

    def do_show(self, _) -> None:
        """
        Show the final results for common words for the requested parameters, criterion,top_k
        :param _: No parameters
        """
        try:
            self.common_words = CalculateCommonWords(results_dir=self.data_loader.results_dir,
                                                     data=self.data,
                                                     common_criterion=self.common_criterion,
                                                     debug=self.debug)
            self.common_words.show_common(top_k=self.top_k, file_name=self.results_file_name)
        except TypeError as e:
            print(f"You need to parse the data at least. "
                  f"optional apply some filters first "
                  f"or restore them from a checkpoint!\n{e}")
        except StopIteration:
            print(
                f"Request common words with top_k={self.top_k}\n"
                f"criterion={self.common_criterion}\n"
                f"Nothing found\n"
                f"All the common words are stored in results directory\n"
                f"Change the parameters of top_k and and the criterion and repeat")

    def do_exit(self, _) -> None:
        """
        Exit the program
        :return:
        """
        print("Thank you!\nbye")
        sys.exit()


def main() -> None:
    cli = HastTagApp()
    cli.cmdloop()


if __name__ == "__main__":
    main()
