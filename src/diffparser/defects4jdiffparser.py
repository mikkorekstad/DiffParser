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
        # Log some info
        logging.info(f"The data contains {self.n_bugs} bugs!")

    def parse_all_commits(self):
        """Parse all commits"""
        [self.parse_commit(commit) for commit in self.data]

    def parse_commit(self, commit):

        # For each commit I want to separate what happens in each file first.
        list_of_files = list(commit['changedFiles'].keys())
        print(f"Got a list of {len(list_of_files)} filenames: {list_of_files}")
        sep_dict_files = self.sep_by_files(commit['diff'], list_of_files)

        for key, value in sep_dict_files.items():
            sep_dict_snippets = self.sep_by_snippets(value)
            commit['changedFiles'][key]['buggyCode'] = sep_dict_snippets['buggyCode']
            commit['changedFiles'][key]['patchedCode'] = sep_dict_snippets['patchedCode']

            #for line in value:
            #     print(line)

    def sep_by_snippets(self, un_separated):
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
        file_info = {file_name: {} for file_name in list_of_files}
        current_file = None

        for i, line in enumerate(diff.splitlines()):
            if '--- a' in line or '+++ b' in line:
                current_file = [fn for fn in list_of_files if fn in line][0]
                file_info[current_file]['firstDescribed'] = file_info[current_file].get('firstDescribed', i)
                file_info[current_file]['lastDescribed'] = i
            # elif re.search(r'(@@ -*\d+,\d* \+\d+,\d* @@)', line):
            #     file_info[current_file]['firstLine'] = i

        for i, key in enumerate(list(file_info.keys())[:-1]):
            proceeding = list(file_info.keys())[i+1]
            file_info[key]['proceedingFile'] = proceeding
            file_info[key]['lastLine'] = file_info[proceeding]['firstDescribed'] - 1

        file_info[list(file_info.keys())[-1]]['lastLine'] = len(diff.splitlines()) - 1

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
    parser = Defects4jDiffParser(data_set, remove_multiple_diffs=False)
    parser.parse_all_commits()
    parser.save_to_json('../../output/testExperimental2.json')
