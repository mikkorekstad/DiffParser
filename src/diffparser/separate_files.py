

def sep_by_files(diff):
    # Get the information about where the files start and stop
    file_info = get_file_start_indices(diff)
    # Create empty dictionary
    sep_dict = {}
    # Iterate over the information in the file_info dict
    for key, value in file_info.items():
        # Describe the start and stop lines
        start = value['finalPathLine'] + 1
        stop = value['lastLine']
        # Add the split diff lines to the sep_dict dictionary
        sep_dict[key] = diff.splitlines()[start:stop]
    # Return the new sep_dict dictionary containing the separated diffs.
    return sep_dict


def get_file_start_indices(diff):
    # Create a dict with filenames as entries.
    file_info = {}  # {file_name: {} for file_name in list_of_files}

    # Iterate over each line in the diff
    for i, line in enumerate(diff.splitlines()):
        # Check if the line is describing subtraction or addition in a file
        if '--- a' in line or '+++ b' in line:

            # Select the current file from the list_of_files, based on the characters of the line.
            # current_file = [fn for fn in list_of_files if fn in line][0]
            current_file = line[6:]
            file_info[current_file] = {}

            # Store the information about where we found this line
            file_info[current_file]['firstPathLine'] = file_info[current_file].get('firstPathLine', i)
            file_info[current_file]['finalPathLine'] = i

    return define_file_indices(file_info, diff)


def define_file_indices(file_info, diff):
    # Iterate over all except the last entries in the file_info dict
    for i, key in enumerate(list(file_info.keys())[:-1]):
        # Store information about what the next file is
        proceeding = list(file_info.keys())[ i +1]
        file_info[key]['proceedingFile'] = proceeding
        # With information about the next line, we can save the index of this snippets final line.
        file_info[key]['lastLine'] = file_info[proceeding]['firstPathLine'] - 1
    # We can also save information about the index of the last line for the final snippet:
    file_info[list(file_info.keys())[-1]]['lastLine'] = len(diff.splitlines()) - 1

    # Return the information gathered
    return file_info
