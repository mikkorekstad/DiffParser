import separate_files
import separate_snippets


def separate_single_file_diff(diff):
    """
    Takes a diff in the format like this: "@@ -10,7 +10,7 @@ class ClassName(ParentClass):\n  ", and separates it into
    the format like this: {'oldCode': [], 'newCode': []}.

    Parameters
    ----------
    diff string
        The diff to be parsed.
    Returns
    -------
    separated_single_file_diff dict
        Dictionary with entries for the old and new code.
    """
    return separate_snippets.sep_by_snippets(diff.splitlines())


def separate_multi_file_diff(diff):
    """
    Takes a string with this format: '--- a/path/filename \n+++ b/path/filename\n@@ -10,7 +10,7 @@ code'
    The output of this function looks like this: {'fileName': {'oldCode':[], 'newCode':[]}}

    Parameters
    ----------
    diff : string
        A string with information about the path as well as the code of the changes.

    Returns
    -------
    parsed_dict : dict
        A dict with a key for each filename and the value as a nested list. Each list in the nested list is a code-
        snippet appropriately parsed.
    """
    # Create dict with code mapped to filenames: {filename1: {}, filename2: {}}
    sep_dict_files = separate_files.sep_by_files(diff)
    parsed_dict = {key: {} for key in sep_dict_files}

    # Iterate through sep_dict_files:
    # key = 'filename'
    # value = ['@@ -int, int +int, int @@ 1st line', '2nd line', ..., 'final line of code']
    for key, value in sep_dict_files.items():
        # Separate the lines into sep_dict_snippets = {'oldCode': nested list, 'newCode': nested list}
        sep_dict_snippets = separate_snippets.sep_by_snippets(value)
        # Add the parsed code to correct location, as described above in docstring.
        parsed_dict[key]['oldCode'] = sep_dict_snippets['oldCode']
        parsed_dict[key]['newCode'] = sep_dict_snippets['newCode']
    return parsed_dict

