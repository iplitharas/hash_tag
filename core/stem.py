from hash_tag.core.data_loader import FileLine
from hash_tag.tools.logger import Logger, logged
from hash_tag.tools.helpers import write_json, write
from typing import List
import os

try:
    import nltk

    from nltk.stem import PorterStemmer
    from nltk.stem import LancasterStemmer
except Exception as e:
    Logger.logger.error(e)


@logged
def stem_words(data: List[FileLine], vocabulary: str, stemmer: str, saves_dir: str,
               debug: bool = False) -> List[FileLine]:
    """
    Stem words using nltk PorterStemmer or LancasterStemmer for english language only
    """
    english_stemmer_driver = {"porter": PorterStemmer,
                              "lancaster": LancasterStemmer}

    if vocabulary.lower() == "english":
        try:
            stemmer_obj = english_stemmer_driver[stemmer.lower()]()
            for line in data:
                line.words = [stemmer_obj.stem(word) for word in line.words]

            if debug:
                write(os.path.join(saves_dir, f"{stemmer_obj.__class__.__name__}"), data)
                write_json(os.path.join(saves_dir, f"{stemmer_obj.__class__.__name__}"), data)
        except KeyError as error:
            Logger.logger.error(f"Key error: {error}")
    else:
        Logger.logger.info(f"There aren't any register stemmer's for the "
                           f"requested language:{vocabulary}")
    return data
