"""
Defects4j-bugs parser.
"""

import json
import logging
import re

re_separate_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n@@ '


def parse(file_name, remove_multi_line=True):
    """Parsing function"""

    # Read the data file from json format
    with open(file_name, 'r') as f:
        data = json.load(f)

    # Get the original length of the data
    original_data_length = len(data)
    print(f"Original amount of bugs: {original_data_length}")

    # Remove bugs covering multiple files, if needed
    if remove_multi_line:
        data = remove_multiple_file_bugs(data)
        print(f"Removed {original_data_length - len(data)} bugs, because they covered multiple files.")

        # Print out any remaining bugs covering multiple files, to make sure that they are not there!
        check_multiple_line_bugs(data)

    # Parse the diffs to make them interpretable
    [parse_bug(bug) for bug in data]


def parse_bug(bug):
    """Function to parse a single bug"""

    # Get some initial information
    n_files = len(bug['changedFiles'])
    logging.info(f"Working with bugId: {bug['bugId']} which have changes in {n_files} files.")

    # Split the diffs from each file:
    list_of_diffs = re.split(re_separate_files, bug['diff'])

    loc = re.("(?<=\@@ )(.*?)(?=\ @@)", bug['diff'])

    for line in loc:
        print("New file")
        print(line)


def remove_multiple_file_bugs(original_data):
    """Remove all bugs that from more than one file."""
    return [bug for bug in original_data if (len(bug['changedFiles']) == 1)]


def check_multiple_line_bugs(lst):
    """Check for all bugs that belogns to more than one file."""
    [print(f"bugId {bug['bugId']} has {files} files.") for bug in lst if (files := len(bug['changedFiles'])) > 1]


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    data_set = '../../data/sample.json'
    # data_set = '../../data/defects4j-bugs.json'
    parse(data_set, remove_multi_line=False)
