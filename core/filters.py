from hash_tag.core.data_loader import FileLine
from typing import List
from hash_tag.tools.logger import Logger

try:
    import nltk

    nltk.download('stopwords')
    from nltk.corpus import stopwords
except Exception as e:
    Logger.logger.error(e)


# ##############################################################################################
# ################## filters must be added also in the app.py ##################################
# ##############################################################################################

def filter_punctuation(data: List[FileLine], *args, **kwargs) -> List[FileLine]:
    """
    Removes all the !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~ chars.
    """
    for line in data:
        line.words = [word for word in line.words if word.isalpha()]
    return data


def filter_by_tag(data: List[FileLine], *args, **kwargs) -> List[FileLine]:
    """
    filter all the words for the requested tags based on  the nltk pos tag
    """
    for line in data:
        line.words = [tokens[0] for tokens in nltk.pos_tag(line.words) if
                      tokens[1] in kwargs["tags"]]
    return data


def filter_duplicates(data: List[FileLine], *args, **kwargs) -> List[FileLine]:
    """
    Removes the duplicates words in the same line only!
    """
    for line in data:
        line.words = [word for word in set(line.words)]
    return data


def filter_stop_words(data: List[FileLine], *args, **kwargs) -> List[FileLine]:
    """
    Filter the words based on the requested vocabulary and nltk stop words
    """
    try:
        stop_words = set(stopwords.words(kwargs["vocabulary"].lower()))
        Logger.logger.debug(f"Stop_words are {stop_words}")
        for line in data:
            line.words = [word for word in line.words if word.lower() not in stop_words]
        return data
    except IOError as error:
        Logger.logger.error(f"{error}\nSupporting stop words from corpus nltk:"
                            f"{stopwords.__dict__}")
    except KeyError as key_error:
        Logger.logger.error(f"Vocabulary keyword argument is missing: {key_error}")
