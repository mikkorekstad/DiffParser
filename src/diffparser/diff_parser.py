import json


def main(file_name):

    with open(file_name, 'r') as f:
        data = json.load(f)

    data = remove_multiple_file_bugs(data)
    check_multiple_line_bugs(data)
    #print(f"Total number of bugs with more than one file: {n}, out of: {n_tot}")


def remove_multiple_file_bugs(original_data):
    """Remove all bugs that from more than one file."""
    return [bug for bug in original_data if (len(bug['changedFiles']) == 1)]


def check_multiple_line_bugs(lst):
    """Check for all bugs that belogns to more than one file."""
    [print(f"bugId {bug['bugId']} has {files} files.") for bug in lst if (files := len(bug['changedFiles'])) > 1]


if __name__ == '__main__':
    # data_set = '../../data/sample.json'
    data_set = '../../data/defects4j-bugs.json'
    main(data_set)
