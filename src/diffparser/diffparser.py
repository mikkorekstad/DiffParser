"""
Defects4j-bugs parser.
"""

import json
import logging
import re

class DiffParser(object):
    """Class for parsing defects4j bugs."""

    re_sep_files = r'-{3} a\/.*?\.[\w:]+\n\+{3} b\/.*?\.[\w:]+\n'
    re_sep_loc = r'@@ -*(\d+,\d* \+\d+,\d* @@) '

    def __init__(self, file_name, remove_multiple_diffs=True):
        """Constructor."""

        # Initial values
        self.file_name = file_name
        self.remove_multiple_diffs = remove_multiple_diffs
        self.data = self.read_file(self.file_name)

        # TODO: Remove multiple diffs

    @staticmethod
    def read_file(file_name):
        """Read the file from json format"""
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data

    def parse_all_commits(self):
        """Parse all commits"""
        # self.data = [entry for commit in self.data if (entry := self.parse_commit(commit))]
        for commit in self.data:
            entry = self.parse_commit(commit)

    def parse_commit(self, commit):
        """Work through the commit and and the changes to each file."""
        # Quickly check for multiple files
        n_files = len(commit['changedFiles'])
        logging.info(f"Working with bugId: {commit['bugId']} which have changes in {n_files} files.")
        if (n_files > 1) and self.remove_multiple_diffs:
            logging.info("Removed commit due to multiple files.")
            return False

        # Split the from each file:
        file_splits = re.split(self.re_sep_files, commit['diff'])
        file_names = re.findall('(?<=\-{3} a\/src\/main\/java\/)(.*)', commit['diff'])
        print(f'{file_names = }')

        # Remove empty strings from list of file splits.
        file_splits = [file for file in file_splits if file]

        # Now we have one element in the list for each file.
        logging.info(f"{file_splits = }")

        for file_split, file_name in zip(file_splits, file_names):
            buggy, patched = self.separate_buggy_and_patched(file_split)
            commit['changedFiles'][file_name]['buggyCode'] = buggy
            commit['changedFiles'][file_name]['patchedCode'] = patched


    def separate_buggy_and_patched(self, file_split):
        # Define empty strings for the code-snippets
        buggy_code = ''
        patched_code = ''

        buggy_count = 0
        patched_count = 0

        # Iterate through each line of the diff, and assign the lines to the correct variable
        for line in file_split.splitlines():
            if line[0] == "-":
                buggy_code += (line[1:] + "\n")
                buggy_count += 1
            elif line[0] == "+":
                patched_code += (line[1:] + "\n")
                patched_count += 1
            else:
                buggy_code += (line + "\n")
                patched_code += (line + "\n")
        return buggy_code, patched_code


        #for unstructured_diff in file_splits:
        #    change_loc, buggy, patched = separate_bug(unstructured_diff)



if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    data_set = '../../data/defects4j-bugs.json'
    data_set1 = '../../data/sample.json'
    data_set2 = '../../data/sample2.json'
    parser = DiffParser(data_set2, remove_multiple_diffs=False)
    parser.parse_all_commits()
    print(f'{parser.data = }')