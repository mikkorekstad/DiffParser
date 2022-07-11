"""
Defects4j-bugs parser.
"""

import json
import logging
import re
import numpy as np


class Defects4jDiffParser(object):
    """Class for parsing defects4j bugs."""

    re_sep_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n'
    re_sep_loc = r'@@ -*(\d+,\d* \+\d+,\d* @@) '
    re_sep_snippets = r'@@ -*(\d+,\d* \+\d+,\d* @@) '

    def __init__(self, file_name, remove_multiple_diffs=True):
        """
        Construct a Defects4J JSON file parser. This is an object that will be able to extract information about the
        diffs in the Defects4J dataset into a structured output of the before / after code snippets.
        Parameters
        ----------
        file_name str path/name of JSON-file to be parsed
        remove_multiple_diffs boolean value which indicated how to deal with multiple diff commits.
        """

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
            self.statistics[commit['revisionId']][key] = stats

    @staticmethod
    def sep_by_snippets(un_separated):
        """
        Takes in an unfiltered list of code-lines like this: [@@ -10,5 +10,7@@ line1, line2, ...].
        Will filter out the less interesting part of the first line of the code snippet, and separate the code from
        before the commit and after, based on the prefix in the beginning of each line.

        This function use the @@ -10,5 +10,7@@ part to distinguish between different code-snippets.
        We have information about what lines the alterations occur on: -digit indicated at which line the removal
        starts, and +digit indicates where the adding starts. The number after the comma indicates how many lines is
        described in the diff. Because this structure occurs between each code-snippet, we use a regex to find these and
        split the lines between them, before separating the code as explained above.

        Parameters
        ----------
        un_separated list containing lines of code

        Returns
        -------
        sep_dict Dictionary containing separated code in this format: {buggyCode: [buggyLine1, buggyLine2],
                                                                       patchedCode: [patchedLine1, patchedLine2]}
        """
        # Define some variables:
        buggy = []
        patched = []
        current_snippet = -1
        sep_dict = {'buggyCode': buggy, 'patchedCode': patched}

        # Iterate over each line
        for i, line in enumerate(un_separated):
            # Check if the line is the beginning of a new code snippet
            if re.search(r'(@@ -*\d+,\d* \+\d+,\d* @@)', line):
                # Split the line
                line_split = re.split(r'(@@ -*\d+,\d* \+\d+,\d* @@)', line)
                # Store the last value of the split, that's where we find the code snippet.
                line = [element for element in line_split if element][-1]
                # Increase the snippet counter
                current_snippet += 1
                # Create new lists for the current iteration
                buggy.append([])
                patched.append([])

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

    def sep_by_files(self, diff, list_of_files):
        """

        This function finds the lines that includes the filenames, and saves the information about their locations
        in the diff.

        Parameters
        ----------
        diff str formatted like this: '--- a/path/filename1 +++ b/path/filename1 @@ -1,10 +1,12 @@ func1 ---a/path2...'
        list_of_files: list of filenames

        Returns
        -------
        sep_dict: dict with format: {'path/filename': ['@@ -int,int +int,int @@ codeLine1', 'codeLine2']}
        """
        # Get the information about where the files start and stop
        file_info = self.get_file_start_indices(diff, list_of_files)
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

    @staticmethod
    def get_file_start_indices(diff, list_of_files):
        """
        In the Defects4J dataset we get diffs that contain a lot of information:
        first information about whether lines have been added or subtracted to a certain file:
        --- a/path/filenameThatHasRemovedLines or +++ b/path/filenameThatHasAddedLines

        This function creates a dictionary with filenames as keys, and the information about where each file starts,
        and stops as the values (in a nested dictionary). This information will later be used to separate the diff
        between the files.

        Parameters
        ----------
        diff: string, the diff is a str with all info about the changes between the previous and next state after commit
        list_of_files: list of filenames

        Returns
        -------
        file_info dict with format: {'path/filename': {'firstDescribed': int, 'lastDescribed': int, 'lastLine': int}}
        """
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

    def print_statistics(self):
        num_files = []
        num_snippets = {}
        n_files_dict = {}
        # num_files.append(stats)
        for revisionID, dct in self.statistics.items():
            n_files = len(dct)
            num_files.append(n_files)
            _hash = f'{n_files} files'
            old_count = n_files_dict.get(_hash, 0)
            n_files_dict[_hash] = old_count + 1
            for file_name, stats in dct.items():
                # Save values for the snippet counts
                num_buggy_snippets = stats['numBuggySnippets']
                num_patched_snippets = stats['numPatchedSnippets']

                # Append value to the num_snippets dictionary
                snippet_dict = num_snippets.get(_hash, {})
                _hash2 = f'{num_buggy_snippets} snippets'
                old_count = snippet_dict.get(_hash2, 0)
                snippet_dict[_hash2] = old_count + 1
                num_snippets[_hash] = snippet_dict

                # Do a quick check that we don't have dis-proportioned amount of snippets
                if num_buggy_snippets != num_patched_snippets:
                    raise ValueError("We should always have the same amount of src snippets as targets!")

        # Print out the statistics
        print(f"We have {len(num_files)} bugs.")
        print(f"Average number of files per bug: {np.average(num_files)}.")
        print(f"Overview of file counts: {n_files_dict}")
        print(f"Overview of snippet counts: {num_snippets}")


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    data_set = '../../data/defects4j-bugs.json'
    data_set1 = '../../data/sample.json'
    data_set2 = '../../data/sample2.json'
    parser = Defects4jDiffParser(data_set, remove_multiple_diffs=False)
    parser.parse_all_commits()
    parser.save_to_json('../../output/testExperimental.json')
    # print(f"{parser.statistics = }")
    parser.print_statistics()
