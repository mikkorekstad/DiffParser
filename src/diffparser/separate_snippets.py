import re


def sep_by_snippets(un_separated):
    """
    Takes in an unfiltered list of code-lines like this: [@@ -10,5 +10,7@@ line1, line2, ...], and returns it in a
    dictionary formatted like this: {'oldCode': [oldLine1, oldLine2], 'newCode': [newLine1, newLine2]}.


    This function use the @@ -10,5 +10,7@@ part to distinguish between different code-snippets.
    We have information about what lines the alterations occur on: -digit indicated at which line the removal
    starts, and +digit indicates where the adding starts. The number after the comma indicates how many lines is
    described in the diff. Because this structure occurs between each code-snippet, we use a regex to find these and
    split the lines between them, before separating the code as explained above.

    Parameters
    ----------
    un_separated : list
        A list containing lines of code.

    Returns
    -------
    sep_dict : dict
        A dictionary containing separated code.
    """
    # Define some variables:
    old_code = []
    new_code = []
    current_snippet = -1
    sep_dict = {'oldCode': old_code, 'newCode': new_code}
    re_line_split = r'(@+ -*\d+,\d* \+\d+,\d* @+)'

    # Iterate over each line
    for i, line in enumerate(un_separated):
        # Check if the line is the beginning of a new code snippet
        if re.search(re_line_split, line):
            # Increase the snippet counter
            current_snippet += 1
            # Create new lists for the current iteration
            old_code.append([])
            new_code.append([])

            # Split the line
            line_split = re.split(re_line_split, line)
            # Store the last value of the split, that's where we find the code snippet.
            line = [element for element in line_split if element][-1]
            if re.search(re_line_split, line):
                continue

        # Add the code to the correct snippet
        if line[0] == '-':
            old_code[current_snippet].append(' ' + line[1:])
        elif line[0] == '+':
            new_code[current_snippet].append(' ' + line[1:])
        else:
            # If the code starts with neither + / -, the code belongs to both snippets
            old_code[current_snippet].append(line)
            new_code[current_snippet].append(line)

    # Return the separated code
    return sep_dict
