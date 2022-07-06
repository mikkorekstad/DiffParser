"""
Defects4j-bugs parser.
"""

import json
import logging
import re


class DiffParser(object):
    """Class for parsing defects4j bugs."""

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
        self.data = [entry for commit in self.data if (entry := self.parse_commit(commit))]

    def parse_commit(self, bug):
        """Work through the commit and and the changes to each file."""
        # Quickly check for multiple files
        n_files = len(bug['changedFiles'])
        logging.info(f"Working with bugId: {bug['bugId']} which have changes in {n_files} files.")
        if (n_files > 1) and self.remove_multiple_diffs:
            logging.info("Removed commit due to multiple files.")
            return False

        #



if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    data_set = '../../data/sample.json'
    # data_set = '../../data/defects4j-bugs.json'
    parser = DiffParser(data_set, remove_multiple_diffs=True)
    parser.parse_all_commits()
