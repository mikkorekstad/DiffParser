import separate_diff
import json


def parse_diff(diff, path_included):
    """
    This function will take a diff in the form of a string, parse it, and return it in the form of a dictionary in the
    following format: {'oldCode': [], 'newCode': []}

    If the diff contains a path with description of the filename for each change, the path_included parameter should be
    True, otherwise false.

    If the path is included, the returned dictionary will return one dictionary for each filename that is included, and
    the format would loke like this: {'filename': {'oldCode': [], 'newCode':[]}}

    Parameters
    ----------
    diff str
        String containing the diff to be parsed.
    path_included bool
        True if the diff contains the path to each file, otherwise False.
    Returns
    -------
    separated_diff dict
        dict containing the separated diff in format described above
    """
    separated_diff = separate_diff.separate_diff(diff, path_included)
    return separated_diff


def parse_list_of_commits(commits, path_included, diff_key='diff', changed_key='changedFiles'):
    """
    This function will take a list of commits as input and returns a parsed version of the same list.
    A commit in this case is a dictionary containing a string with the diff, among other things.

    Parameters
    ----------
    commits : list
        List of dicts, where each dict represents a commit, which in turn contains a diff.
    path_included : bool
        True if the diff contains the path to each file, otherwise False.
    diff_key : str
        String describing the entry of the commit that contains the diff. Default: 'diff'
    changed_key : str
        String describing the entry of the commit that contains the changed files. Default: 'changedFiles'
    Returns
    -------
    commits list
        Returns the same list as the input parameter, but with entries for oldCode and newCode.
    """
    if not path_included:
        for commit in commits:
            parsed_commit = separate_diff.separate_diff(commit[diff_key], path_included)
            commit['oldCode'] = parsed_commit['oldCode']
            commit['newCode'] = parsed_commit['newCode']

    if path_included:
        for commit in commits:
            parsed_commit = separate_diff.separate_diff(commit[diff_key], path_included)
            changed_files = list(commit[changed_key].keys())
            for key, value in parsed_commit.items():
                commit_key = [file_name for file_name in changed_files if file_name in key][0]
                commit[changed_key][commit_key]['oldCode'] = value['oldCode']
                commit[changed_key][commit_key]['newCode'] = value['newCode']
    return commits


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


def parsed_to_txt(parsed_lst, output_path):
    """
    Takes a list of parsed commits and writes the old code to the src file, and the new code to the tgt file.

    Parameters
    ----------
    parsed_lst list
        List of parsed commits.
    output_path string
        String which represents the path to the directory which the files would be written to.

    Returns
    -------
        None
    """
    old_codes = [commit['oldCode'] for commit in parsed_lst]
    new_codes = [commit['newCode'] for commit in parsed_lst]
    code_lst = [old_codes, new_codes]
    for code, extension in zip(code_lst, ['src', 'tgt']):
        with open(output_path + extension + '.txt', 'w') as fp:
            for element in code:
                for line in element:
                    input_line = ''.join(pair for pair in line)
                    fp.writelines(input_line + '\n')


if __name__ == '__main__':
    """Example parser."""
    # data_set = '../../data/pypi-bugs/pypi-bugs.jsonl'
    #data_set = '../../data/sample.json'
    #unparsed_list = read_json(data_set)
    #parsed_list = parse_list_of_commits(unparsed_list, path_included=True)
    # print(f'{parsed_list = }')

    # to_txt(parsed_list, output_path='../../data/pypi-bugs/outputTest/')
    # save_to_single_txt(old_, new_, '../../data/pypi-bugs/output/')
    print(parse_diff(multi_file_diff, path_included=True))
    # print(parse_diff(single_file_diff, path_included=False))
