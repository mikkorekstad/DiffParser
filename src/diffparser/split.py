import json
from numpy import array
from sklearn.model_selection import train_test_split


class JsonSplitter(object):
    """Class for splitting Defects4J Json altered with the Defects4J parser into test, train and validation datasets."""

    def __init__(self, file_name, remove_multi_snippets_per_file=False, remove_multi_file=False):
        """INIT"""
        self.data = self.read_file(file_name)
        self.buggy_list, self.patched_list = self.prepare_data(remove_multi_snippets_per_file, remove_multi_file)

    def prepare_data(self, remove_multi_snippets_per_file=False, remove_multi_file=False):
        """

        Parameters
        ----------
        split_size tuple (train size, validation size, test size)
        output_name str path/name of output file without extension
        remove_multi_snippets_per_file bool
        remove_multi_file bool

        Returns
        -------

        """

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
                    buggy.append(buggySnippet)
                    patched.append(patchedSnippet)

            buggy_lst.append(buggy)
            patched_lst.append(patched)

        # Convert to numpy arrays

        buggy_lst = array(buggy_lst, dtype=object)
        patched_lst = array(patched_lst, dtype=object)
        return buggy_lst, patched_lst

    def test_train_val_split(self, split_size, output_name):
        """

        Parameters
        ----------
        split_size tuple (train size, validation size, test size)
        output_name str path/name of output file without extension
        remove_multi_snippets_per_file bool
        remove_multi_file bool

        Returns
        -------



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
                    buggy.append(buggySnippet)
                    patched.append(patchedSnippet)

            buggy_lst.append(buggy)
            patched_lst.append(patched)

        # Convert to numpy arrays
        buggy_lst = array(buggy_lst, dtype=object)
        patched_lst = array(patched_lst, dtype=object)
        """

        # Create filenames
        buggy_names = [f'{output_name}src-{extension}.txt' for extension in ['train', 'val', 'test']]
        patched_names = [f'{output_name}tgt-{extension}.txt' for extension in ['train', 'val', 'test']]

        # Create splits
        train_size, val_size, test_size = split_size
        src_train, src_test, tgt_train, tgt_test = train_test_split(self.buggy_lst, self.patched_lst, test_size=test_size,
                                                                      train_size=train_size + val_size)
        src_train, src_val, tgt_train, tgt_val = train_test_split(src_train, tgt_train, test_size=val_size,
                                                                    train_size=train_size)

        # Nest together the names for easier iteration
        buggy_list = [src_train, src_val, src_test]
        patched_list = [tgt_train, tgt_val, tgt_test]
        # Save the data to txt files
        [self.save_to_txt(split, name) for split, name in zip(buggy_list + patched_list, buggy_names + patched_names)]

    @staticmethod
    def save_to_txt(split, file_name):
        with open(file_name, 'w') as fp:
            for element in split:
                for line in element:
                    input_line = ''.join(pair for pair in line)
                    fp.writelines(input_line + '\n')

    def save_to_single_txt(self, file_name):
        code_lst = [self.buggy_list, self.patched_list]
        extension_lst = ['src', 'tgt']
        for code, extension in zip(code_lst, extension_lst):
            with open(file_name + extension + '.txt', 'w') as fp:
                for element in code:
                    for line in element:
                        input_line = ''.join(pair for pair in line)
                        fp.writelines(input_line + '\n')

    @staticmethod
    def read_file(file_name):
        """Read the file from json format"""
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    splitter = JsonSplitter('../../output/testExperimental.json', remove_multi_file=True, remove_multi_snippets_per_file=False)
    splitter.save_to_single_txt('../../output/no-split/')
    # splitter.test_train_val_split(split_size=(1, 0, 0), output_name='../../output/split/', remove_multi_file=True,
    #                               remove_multi_snippets_per_file=True)
