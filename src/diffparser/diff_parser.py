"""
Defects4j-bugs parser.
"""

import json

re_separate_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n@@ '


def parse(file_name, remove_multi_line=True):
    """Parsing function"""

    # Read the data file from json format
    with open(file_name, 'r') as f:
        data = json.load(f)

    # Get the original length of the data
    original_data_length = len(data)
    print(f"Original data length: {original_data_length}")

    # Remove bugs covering multiple files, if needed
    if remove_multi_line:
        data = remove_multiple_file_bugs(data)
        print(f"Removed {original_data_length - len(data)} bugs, because they covered multiple files.")

        # Print out any remaining bugs covering multiple files, to make sure that they are not there!
        check_multiple_line_bugs(data)

    parse_all_diffs(data)


def parse_all_diffs(data):
    for bug in data:
        print(f"Working with bugId: {bug['bugId']}")
        diff = bug['diff']
        parse_diff(diff)


def parse_diff(diff):
    pass


def remove_multiple_file_bugs(original_data):
    """Remove all bugs that from more than one file."""
    return [bug for bug in original_data if (len(bug['changedFiles']) == 1)]


def check_multiple_line_bugs(lst):
    """Check for all bugs that belogns to more than one file."""
    [print(f"bugId {bug['bugId']} has {files} files.") for bug in lst if (files := len(bug['changedFiles'])) > 1]


if __name__ == '__main__':
    # data_set = '../../data/sample.json'
    data_set = '../../data/defects4j-bugs.json'
    parse(data_set, remove_multi_line=True)
