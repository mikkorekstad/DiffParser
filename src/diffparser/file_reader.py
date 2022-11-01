import json


def read_json(file_name):
    """
    Reads a Json file.

    Parameters
    ----------
    file_name str
        String representing the path/filename of the datafile.
    Returns
    -------
    data list
        In this program, we want the json to be a list of dictionaries, and therefore, the returned information should
        be a list of dicts as well.
    """
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def read_jsonl(file_name):
    """
    Reads a Jsonl file.

    Parameters
    ----------
    file_name str
        String representing the path/filename of the datafile.
    Returns
    -------
    data list
        In this program, we want the jsonl to be a list of dictionaries, and therefore, the returned information should
        be a list of dicts as well.
    """
    data = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data
