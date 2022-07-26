from diffparser.parser import read_json, parse_list_of_commits, parsed_to_txt

data_set = '../../data/sample.json'
unparsed_list = read_json(data_set)

parsed = parse_list_of_commits(unparsed_list, path_included=True)
parsed_to_txt(parsed, '', changed_key='changedFiles')
