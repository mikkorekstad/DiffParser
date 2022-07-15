import json
import parse_diff_string


def read_jsonl(file_name):
    data = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data


def parse_jsonl(file_name):
    data = read_jsonl(file_name)
    old = []
    new = []
    for dct in data:
        diff = dct['diff']
        separated_dif = parse_diff_string.sep_by_snippets(diff.splitlines())
        old_list = ''.join(separated_dif['buggyCode'][0]) # ['\n'.join(snippet) for snippet in separated_dif['buggyCode'][0]]
        old.append(old_list)
        new.append(''.join(separated_dif['patchedCode'][0]))
    return old, new


def save_to_single_txt(old, new, file_name):
    code_lst = [old, new]
    extension_lst = ['src', 'tgt']
    for code, extension in zip(code_lst, extension_lst):
        with open(file_name + extension + '.txt', 'w') as fp:
            for line in code:
                input_line = ''.join(pair for pair in line)
                fp.writelines(input_line + '\n')


if __name__ == '__main__':
    """Example parser."""
    data_set = '../../data/pypi-bugs/pypi-bugs.jsonl'
    old_, new_ = parse_jsonl(data_set)
    save_to_single_txt(old_, new_, '../../data/pypi-bugs/output/')


