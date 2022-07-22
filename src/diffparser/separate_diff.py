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
    separated_single_file_diff = separate_snippets.sep_by_snippets(diff.splitlines())
    return separated_single_file_diff


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


def separate_diff(diff, path_included=False):
    """
    This function calls one of the two functions for separating the diffs based on whether the path is included or not.

    Parameters
    ----------
    diff string
        String with the diff.
    path_included bool
        True if the path is included in the diff, otherwise False.
    Returns
    -------
    separated_diff dict
        Dictionary based on the diff created using either separate_multi_file_diff or separate_single_file_diff based
        on whether the path variable (bool) is True or False.
    """
    if path_included:
        separated_diff = separate_multi_file_diff(diff)
        return separated_diff
    else:
        separated_diff = separate_single_file_diff(diff)
        return separated_diff


def get_file_start_indices(diff):
    """

    Parameters
    ----------
    diff

    Returns
    -------

    """
    # Create a dict with filenames as entries.
    file_info = {}  # {file_name: {} for file_name in list_of_files}
    # Iterate over each line in the diff
    for i, line in enumerate(diff.splitlines()):
        # Check if the line is describing subtraction or addition in a file
        if '--- a' in line or '+++ b' in line:
            # Select the current file from the list_of_files, based on the characters of the line.
            current_file = line[6:]
            file_info[current_file] = {}

            # Store the information about where we found this line
            file_info[current_file]['firstDescribed'] = file_info[current_file].get('firstDescribed', i)

    separated_dict = separate_files.define_file_indices(file_info, diff)
    print(f'{separated_dict = }')
    return separated_dict


def separate_by_files(diff):
    """

    Parameters
    ----------
    diff

    Returns
    -------

    """
    # Get the information about where the files start and stop
    file_info = get_file_start_indices(diff)
    # Create empty dictionary
    sep_dict = {}
    # Iterate over the information in the file_info dict
    for key, value in file_info.items():
        # Describe the start and stop lines
        start = value['lastDescribed'] + 1
        stop = value['lastLine']
        # Add the split diff lines to the sep_dict dictionary
        sep_dict[key] = diff.splitlines()[start:stop]
    # Return the new sep_dict dictionary containing the separated diffs.
    print(f'{sep_dict = }')
    return sep_dict


if __name__ == '__main__':
    multi_file_diff = "--- a/source/org/jfree/data/DefaultKeyedValues.java\n+++ b/source/org/jfree/data/DefaultKeyedValues.java\n@@ -315,30 +315,29 @@ private void rebuildIndex () {\n     public void removeValue(int index) {\n         this.keys.remove(index);\n         this.values.remove(index);\n-        if (index < this.keys.size()) {\n         rebuildIndex();\n-        }\n     }\n \n     /**\n      * Removes a value from the collection.\n      *\n      * @param key  the item key (<code>null</code> not permitted).\n      * \n      * @throws IllegalArgumentException if <code>key</code> is \n      *     <code>null</code>.\n      * @throws UnknownKeyException if <code>key</code> is not recognised.\n      */\n     public void removeValue(Comparable key) {\n         int index = getIndex(key);\n         if (index < 0) {\n-\t\t\treturn;\n+            throw new UnknownKeyException(\"The key (\" + key \n+                    + \") is not recognised.\");\n         }\n         removeValue(index);\n     }\n     \n     /**\n      * Clears all values from the collection.\n      * \n      * @since 1.0.2\n      */\n--- a/source/org/jfree/data/DefaultKeyedValues2D.java\n+++ b/source/org/jfree/data/DefaultKeyedValues2D.java\n@@ -454,12 +454,21 @@ public void removeColumn(int columnIndex) {\n     public void removeColumn(Comparable columnKey) {\r\n+    \tif (columnKey == null) {\r\n+    \t\tthrow new IllegalArgumentException(\"Null 'columnKey' argument.\");\r\n+    \t}\r\n+    \tif (!this.columnKeys.contains(columnKey)) {\r\n+    \t\tthrow new UnknownKeyException(\"Unknown key: \" + columnKey);\r\n+    \t}\r\n         Iterator iterator = this.rows.iterator();\r\n         while (iterator.hasNext()) {\r\n             DefaultKeyedValues rowData = (DefaultKeyedValues) iterator.next();\r\n+            int index = rowData.getIndex(columnKey);\r\n+            if (index >= 0) {\r\n                 rowData.removeValue(columnKey);\r\n+            }\r\n         }\r\n         this.columnKeys.remove(columnKey);\r\n     }\r\n \r\n     /**\r\n      * Clears all the data and associated keys.\r\n      */\r\n"
    single_file_diff = "@@ -330,7 +330,7 @@ class DialsScaler(Scaler):\n           Debug.write('X1698: %s: %s' % (pointgroup, reindex_op))\n \n           if ntr:\n-            integrater.integrater_reset_reindex_operator()\n+            intgr.integrater_reset_reindex_operator()\n             need_to_return = True\n \n         if pt and not probably_twinned:\n"

    print(separate_diff(single_file_diff, False))