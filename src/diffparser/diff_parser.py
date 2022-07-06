"""
Defects4j-bugs parser.
"""

import json
import logging
import re

re_sep_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n@@ '
re_sep_loc = r'-(\d+,\d* \+\d+,\d* @@ )'


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
    list_of_diffs = re.split(re_sep_files, bug['diff'])

    parsed_bug = {}
    for unstructured_diff in list_of_diffs:
        change_loc, buggy, patched = separate_bug(unstructured_diff)


def separate_bug(unstructured_diff):
    """Separate bug into location, buggy part and patched part."""
    change_loc, buggy, patched = 0, 0, 0
    diff_split = re.split(re_sep_loc, unstructured_diff)

    if unstructured_diff:  # TODO: Change to a function for validation of diff later
        logging.debug("New file")
        change_loc = get_loc(diff_split[1])
        buggy, patched = filter_diff(diff_split[2])
        # TODO: Check that the output code is of the length described in the diff
        print("Here comes the buggy code: ")
        print(buggy)
        print("Here comes the patched code: ")
        print(patched)
        #print(f'{buggy =}')
    return change_loc, buggy, patched


def filter_diff(diff):
    """Function to actually parse the diff."""
    buggy_code = ''
    patched_code = ''
    for line in diff.splitlines():
        if line[0] == "-":
            buggy_code += (" " + line[1:] + "\n")
        elif line[0] == "+":
            patched_code += (" " + line[1:] + "\n")
        else:
            buggy_code += (" " + line + "\n")
            patched_code += (" " + line + "\n")
    return buggy_code, patched_code


def get_loc(un_interpretable_loc):
    """Function that turns a weird expression into a nice dict."""

    loc_dict = {}
    split = re.split(r'\+', un_interpretable_loc)
    buggy_loc = re.split(r',', split[0])
    patched_loc = re.split(r',', split[1])
    loc_dict['buggy_start'] = buggy_loc[0]
    loc_dict['buggy_n_lines'] = buggy_loc[1].strip(' ')
    loc_dict['patched_start'] = patched_loc[0]
    loc_dict['patched_n_lines'] = patched_loc[1].strip(' @')

    logging.debug(f'{loc_dict = }')
    return loc_dict


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
