import pickle
import json
from hash_tag.tools.logger import Logger


def write(file_path: str, data) -> None:
    Logger.logger.debug(f"Creating checkpoint at: {file_path}")
    with open(f'{file_path}.pickle', 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def restore(file_path: str):
    Logger.logger.debug(f"Restoring checkpoint from:{file_path}")
    with open(f"{file_path}", 'rb') as f:
        data = pickle.load(f)
    return data


def write_json(file_path: str, data):
    Logger.logger.debug(f"Saving a json at:{file_path}")
    with open(f"{file_path}.json", "w") as f:
        try:
            Logger.logger.warning("Creating json from list with custom objects..")
            temp = {"data": [data.__dict__ for data in data]}
        except AttributeError as e:
            Logger.logger.warning(f"{e}\tCreating json from dict with custom objects..")
            temp = {"data": {key: values.__dict__ for key, values in data.items()}}
        finally:
            json.dump(temp, f)
