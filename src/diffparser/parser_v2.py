import separate_diff
import json

diff_kinds = {'pathed':None, 'unpathed':None}


def parse_diff(diff, kind):
    separated_diff = separate_diff.separate_diff(diff, kind)
    return separated_diff


def extract_diffs(commits=None, diff_key='diff', changed_key='changedFiles'):
    extracted_diffs = None
    return extracted_diffs


def parse_list_of_commits(commits, kind):
    parsed_commits = None
    return commits
