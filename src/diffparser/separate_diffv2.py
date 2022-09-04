

def sep_single_file(diff=None):
    # separated_single_file_diff = separate_snippets.sep_by_snippets(diff.splitlines())
    # return separated_single_file_diff
    print('separating_single_file')
    pass


def sep_multi_file(diff=None, ):
    pass


path_included = {'no': sep_single_file, 'yes': sep_multi_file}


def separate_diff(kwargs):
    path = kwargs['path']
    return path_included[path](kwargs)
