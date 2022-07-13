import re


def sep_by_snippets(un_separated):
    # Define some variables:
    buggy = []
    patched = []
    current_snippet = -1
    sep_dict = {'buggyCode': buggy, 'patchedCode': patched}
    re_line_split = r'(@+ -*\d+,\d* \+\d+,\d* @+)'

    # Iterate over each line
    for i, line in enumerate(un_separated):
        # Check if the line is the beginning of a new code snippet
        if re.search(re_line_split, line):
            # Increase the snippet counter
            current_snippet += 1
            # Create new lists for the current iteration
            buggy.append([])
            patched.append([])

            # Split the line
            line_split = re.split(re_line_split, line)
            # Store the last value of the split, that's where we find the code snippet.
            line = [element for element in line_split if element][-1]
            if re.search(re_line_split, line):
                print(f'Skipping this one: {line = }')
                print(f'Line split was: {line_split}')
                continue

        # Add the code to the correct snippet
        if line[0] == '-':
            buggy[current_snippet].append(" " + line[1:])
        elif line[0] == '+':
            patched[current_snippet].append(" " + line[1:])
        else:
            # If the code starts with neither + / -, the code belongs to both snippets
            buggy[current_snippet].append(" " + line[1:])
            patched[current_snippet].append(" " + line[1:])

    # Return the separated code
    return sep_dict


def sep_by_files(diff):
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
    return sep_dict


def get_file_start_indices(diff):
    # Create a dict with filenames as entries.
    file_info = {} # {file_name: {} for file_name in list_of_files}

    # Iterate over each line in the diff
    for i, line in enumerate(diff.splitlines()):
        # Check if the line is describing subtraction or addition in a file
        if '--- a' in line or '+++ b' in line:

            # Select the current file from the list_of_files, based on the characters of the line.
            # current_file = [fn for fn in list_of_files if fn in line][0]
            current_file = line[6:]
            file_info[current_file] = {}

            # Store the information about where we found this line
            file_info[current_file]['firstDescribed'] = file_info[current_file].get('firstDescribed', i)
            file_info[current_file]['lastDescribed'] = i

    # Iterate over all except the last entries in the file_info dict
    for i, key in enumerate(list(file_info.keys())[:-1]):
        # Store information about what the next file is
        proceeding = list(file_info.keys())[ i +1]
        file_info[key]['proceedingFile'] = proceeding
        # With information about the next line, we can save the index of this snippets final line.
        file_info[key]['lastLine'] = file_info[proceeding]['firstDescribed'] - 1
    # We can also save information about the index of the last line for the final snippet:
    file_info[list(file_info.keys())[-1]]['lastLine'] = len(diff.splitlines()) - 1

    # Return the information gathered
    return file_info


def parse_diff(diff):
    # Create dict with code mapped to filenames
    sep_dict_files = sep_by_files(diff)
    parsed_dict = {key: {} for key in sep_dict_files}

    # Iterate through sep_dict_files: key = 'filename', value = ['lines of code']
    for key, value in sep_dict_files.items():
        # Separate the lines into buggy or patched snippets
        sep_dict_snippets = sep_by_snippets(value)
        # Add the parsed code to correct location, as described above in docstring.
        parsed_dict[key]['buggyCode'] = sep_dict_snippets['buggyCode']
        parsed_dict[key]['patchedCode'] = sep_dict_snippets['patchedCode']

    #for key, val in parsed_dict.items():
    #    print(f'filename: {key} with code: {val}')

    return parsed_dict


def join_diff(parsed_diff):
    for file_name, file_dict in parsed_diff.items():
        for description, nested_list in file_dict.items():
            nested_list = ['\n'.join(snippet) for snippet in nested_list]
            parsed_diff[file_name][description] = nested_list
    return parsed_diff


if __name__ == '__main__':
    """Example parser."""
    my_diff = "--- a/source/org/jfree/data/DefaultKeyedValues.java\n+++ b/source/org/jfree/data/DefaultKeyedValues.java\n@@ -315,30 +315,29 @@ private void rebuildIndex () {\n     public void removeValue(int index) {\n         this.keys.remove(index);\n         this.values.remove(index);\n-        if (index < this.keys.size()) {\n         rebuildIndex();\n-        }\n     }\n \n     /**\n      * Removes a value from the collection.\n      *\n      * @param key  the item key (<code>null</code> not permitted).\n      * \n      * @throws IllegalArgumentException if <code>key</code> is \n      *     <code>null</code>.\n      * @throws UnknownKeyException if <code>key</code> is not recognised.\n      */\n     public void removeValue(Comparable key) {\n         int index = getIndex(key);\n         if (index < 0) {\n-\t\t\treturn;\n+            throw new UnknownKeyException(\"The key (\" + key \n+                    + \") is not recognised.\");\n         }\n         removeValue(index);\n     }\n     \n     /**\n      * Clears all values from the collection.\n      * \n      * @since 1.0.2\n      */\n--- a/source/org/jfree/data/DefaultKeyedValues2D.java\n+++ b/source/org/jfree/data/DefaultKeyedValues2D.java\n@@ -454,12 +454,21 @@ public void removeColumn(int columnIndex) {\n     public void removeColumn(Comparable columnKey) {\r\n+    \tif (columnKey == null) {\r\n+    \t\tthrow new IllegalArgumentException(\"Null 'columnKey' argument.\");\r\n+    \t}\r\n+    \tif (!this.columnKeys.contains(columnKey)) {\r\n+    \t\tthrow new UnknownKeyException(\"Unknown key: \" + columnKey);\r\n+    \t}\r\n         Iterator iterator = this.rows.iterator();\r\n         while (iterator.hasNext()) {\r\n             DefaultKeyedValues rowData = (DefaultKeyedValues) iterator.next();\r\n+            int index = rowData.getIndex(columnKey);\r\n+            if (index >= 0) {\r\n                 rowData.removeValue(columnKey);\r\n+            }\r\n         }\r\n         this.columnKeys.remove(columnKey);\r\n     }\r\n \r\n     /**\r\n      * Clears all the data and associated keys.\r\n      */\r\n"
    parse_diff(my_diff)
    print(join_diff(parse_diff(my_diff)))
