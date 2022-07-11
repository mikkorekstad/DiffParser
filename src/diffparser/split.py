
import json
from numpy import cumsum


class JsonSplitter(object):
    """Class for splitting Defects4J Json altered with the Defects4J parser into test, train and validation datasets."""

    def __init__(self, file_name):
        """INIT"""
        self.data = self.read_file(file_name)

    def test_train_val_split(self, split_size, output_name, remove_multi_snippets_per_file=False, remove_multi_file=False):

        buggy_lst = []
        patched_lst = []

        for commit in self.data:
            # If specified, remove commits with multi-file changes
            num_files = len(commit['changedFiles'])
            if num_files > 1 and remove_multi_file:
                continue
            # If specified, remove commits with multiple snippets in a file
            multiple_snippets = False
            for file in commit['changedFiles'].values():
                num_snippets = len(file['buggyCode'])
                if num_snippets > 1:
                    multiple_snippets = True
            if multiple_snippets and remove_multi_snippets_per_file:
                continue

            # Create lists to store output data
            buggy = []
            patched = []
            # Iterate over the files and then snippets of code
            for file in commit['changedFiles'].values():
                for buggySnippet, patchedSnippet in zip(file['buggyCode'], file['patchedCode']):
                    print(f'{buggySnippet = }')
                    buggy.append(buggySnippet)
                    patched.append(patchedSnippet)

            buggy_lst.append(buggy)
            patched_lst.append(patched)

        # Separate data
        # buggy_splits = self.percentage_split(buggy_lst, split_size)
        # patched_splits = self.percentage_split(patched, split_size)

        # Create filenames
        buggy_names = [f'{output_name}_src_{extension}.txt' for extension in ['train', 'val', 'test']]
        patched_names = [f'{output_name}_trgt_{extension}.txt' for extension in ['train', 'val', 'test']]

        # Save to text file
        # [self.save_to_txt(split, file_name) for split, file_name in zip(buggy_splits, buggy_names)]
        # print(buggy)
        self.save_to_txt(buggy_lst, buggy_names[0])

    @staticmethod
    def percentage_split(seq, percentages):
        # cdf = cumsum(percentages)
        # assert cdf[-1] == 1.0
        # n = len(seq)
        # return [seq[a:b] for a, b in ]
        pass

    @staticmethod
    def save_to_txt(split, file_name):
        with open(file_name, 'w') as fp:
            for element in split:
                for line in element:
                    input_line = ''.join(f'{pair}' for pair in line)
                    fp.writelines(input_line + '\n')


    @staticmethod
    def read_file(file_name):
        """Read the file from json format"""
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    splitter = JsonSplitter('../../output/testExperimental.json')
    splitter.test_train_val_split(split_size=(0.8, 0.1, 0.1), output_name='../../output/MYTEST')
