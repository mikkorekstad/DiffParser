import separate_diff
import json


def diff_to_parsed(diff, path):
    return separate_diff.separate_diff(diff, path)


def list_of_commits_to_parsed(commits, path):
    for commit in commits:
        parsed_commit = separate_diff.separate_diff(commit['diff'], path)
        commit['oldCode'] = parsed_commit['oldCode']
        commit['newCode'] = parsed_commit['newCode']
    return commits


def parse_jsonl(file_name, path):
    list_of_diffs = read_jsonl(file_name)
    return list_of_commits_to_parsed(list_of_diffs, path)


def read_json(file_name):
    pass


def read_jsonl(file_name):
    data = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data


def to_txt(parsed_lst, output_path):
    old_codes = [commit['oldCode'] for commit in parsed_lst]
    new_codes = [commit['newCode'] for commit in parsed_lst]
    code_lst = [old_codes, new_codes]
    # extension_lst = ['src', 'tgt']
    for code, extension in zip(code_lst, ['src', 'tgt']):
        with open(output_path + extension + '.txt', 'w') as fp:
            for element in code:
                for line in element:
                    input_line = ''.join(pair for pair in line)
                    fp.writelines(input_line + '\n')


if __name__ == '__main__':
    """Example parser."""
    data_set = '../../data/pypi-bugs/pypi-bugs.jsonl'
    parsed_list = parse_jsonl(data_set, path=False)
    to_txt(parsed_list, output_path='../../data/pypi-bugs/outputTest/')
    # save_to_single_txt(old_, new_, '../../data/pypi-bugs/output/')
