"""
Defects4j-bugs parser.
"""

import json
import logging
import re


class Defects4jDiffParser(object):
    """Class for parsing defects4j bugs."""

    re_sep_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n'
    re_sep_loc = r'@@ -*(\d+,\d* \+\d+,\d* @@) '
    re_sep_snippets = r'@@ -*(\d+,\d* \+\d+,\d* @@) '

    def __init__(self, file_name, remove_multiple_diffs=True):
        """Constructor."""

        # Initial values
        self.file_name = file_name
        self.remove_multiple_diffs = remove_multiple_diffs
        self.data = self.read_file(self.file_name)
        self.n_bugs = len(self.data)
        self.last_line = False
        self.code_started = False
        self.statistics = {}
        # Log some info
        logging.info(f"The data contains {self.n_bugs} bugs!")

    def parse_all_commits(self):
        """Parse all commits"""
        [self.parse_commit(commit) for commit in self.data]

    def parse_commit(self, commit):
        """
        Retrieve a list of filenames, and use the filenames as keys to store the code that belongs to each file:
        list_of_files = ['path/filename1', 'path/filename2]
        sep_dict_files = {'path/filename1':['1st line of code in file 1', 2nd line of code in file 1]}
        
        for each file in the sep_dict_files list, we create a dict with with the buggy code and patched code
        formatted like this:
        sep_dict_snippets = {'buggyCode': [['firstLineBuggyCodeSnippet1', 'secondLineBuggyCodeSnippet1],
                                            ['firstLineBuggyCodeSnippet2', 'secondLineBuggyCodeSnippet2]],
                             'patchedCode': [['firstLineBuggyPatchedSnippet1', 'secondLinePatchedCodeSnippet1],
                                            ['firstLinePatchedCodeSnippet2', 'secondLinePatchedCodeSnippet2]]
                                            
        With this dictionary, we can add the information to the following location:
        commit['changedFiles]['fileName']['buggyCode or patchedCode']
        
        Parameters
        ----------
        commit dict symbolizing a single commit.

        Returns
        -------   
        None                                 
        """
        # Create list of filenames
        list_of_files = list(commit['changedFiles'].keys())
        print(f"Got a list of {len(list_of_files)} filenames: {list_of_files}")
        # Add entry in statistics dict
        self.statistics[commit['revisionId']] = {}

        # Create dict with code mapped to filenames
        sep_dict_files = self.sep_by_files(commit['diff'], list_of_files)

        # Iterate through sep_dict_files: key = 'filename', value = ['lines of code']
        for key, value in sep_dict_files.items():
            # Separate the lines into buggy or patched snippets
            sep_dict_snippets = self.sep_by_snippets(value)
            # Add the parsed code to correct location, as described above in docstring.
            commit['changedFiles'][key]['buggyCode'] = sep_dict_snippets['buggyCode']
            commit['changedFiles'][key]['patchedCode'] = sep_dict_snippets['patchedCode']

            # Add some stats

            stats = {'numBuggySnippets': len(sep_dict_snippets['buggyCode']),
                     'numPatchedSnippets': len(sep_dict_snippets['patchedCode'])}

            self.statistics[commit['revisionId']][key] = stats  # specific_stats

    def sep_by_snippets(self, un_separated):
        """

        Parameters
        ----------
        un_separated

        Returns
        -------

        """
        buggy = []
        patched = []
        current_snippet = -1
        sep_dict = {'buggyCode': buggy, 'patchedCode': patched}
        for i, line in enumerate(un_separated):
            if re.search(r'(@@ -*\d+,\d* \+\d+,\d* @@)', line):
                line_split = re.split(r'(@@ -*\d+,\d* \+\d+,\d* @@)', line)
                print(f'{[element for element in line_split if element] =}')
                line = [element for element in line_split if element][-1]
                current_snippet += 1
                buggy.append([])
                patched.append([])

            if line[0] == '-':
                buggy[current_snippet].append(" " + line[1:])
            elif line[0] == '+':
                patched[current_snippet].append(" " + line[1:])
            else:
                buggy[current_snippet].append(" " + line[1:])
                patched[current_snippet].append(" " + line[1:])
        return sep_dict

    def sep_by_files(self, diff, list_of_files):
        file_info = self.get_file_start_indices(diff, list_of_files)
        print(f'{file_info = }')

        sep_dict = {}
        for key, value in file_info.items():
            start = value['lastDescribed'] + 1
            stop = value['lastLine']
            sep_dict[key] = diff.splitlines()[start:stop]
        print(f'{sep_dict = }')
        return sep_dict

    def get_file_start_indices(self, diff, list_of_files):

        # Create a dict with filenames as entries.
        file_info = {file_name: {} for file_name in list_of_files}

        # Iterate over each line in the diff
        for i, line in enumerate(diff.splitlines()):
            # Check if the line is describing subtraction or addition in a file
            if '--- a' in line or '+++ b' in line:
                # Select the current file from the list_of_files, based on the characters of the line.
                current_file = [fn for fn in list_of_files if fn in line][0]

                # Store the information about where we found this line
                file_info[current_file]['firstDescribed'] = file_info[current_file].get('firstDescribed', i)
                file_info[current_file]['lastDescribed'] = i

        # Iterate over all except the last entries in the file_info dict
        for i, key in enumerate(list(file_info.keys())[:-1]):
            # Store information about what the next file is
            proceeding = list(file_info.keys())[i+1]
            file_info[key]['proceedingFile'] = proceeding
            # With information about the next line, we can save the index of this snippets final line.
            file_info[key]['lastLine'] = file_info[proceeding]['firstDescribed'] - 1
        # We can also save information about the index of the last line for the final snippet:
        file_info[list(file_info.keys())[-1]]['lastLine'] = len(diff.splitlines()) - 1

        # Return the information gathered
        return file_info

    def save_to_json(self, file_name):
        """Save file to json format."""
        with open(file_name, 'w') as f:
            json.dump(self.data, f, indent=4)

    @staticmethod
    def read_file(file_name):
        """Read the file from json format"""
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    data_set = '../../data/defects4j-bugs.json'
    data_set1 = '../../data/sample.json'
    data_set2 = '../../data/sample2.json'
    parser = Defects4jDiffParser(data_set2, remove_multiple_diffs=False)
    parser.parse_all_commits()
    parser.save_to_json('../../output/testExperimental3.json')
