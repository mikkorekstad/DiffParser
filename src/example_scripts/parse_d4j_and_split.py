from diffparser.parser import read_json, parse_list_of_commits, parsed_to_txt
# from sklearn.model_selection import train_test_split
from math import floor

data_set = '../../data/defects4j-bugs.json'
unparsed_list = read_json(data_set)

parsed = parse_list_of_commits(unparsed_list, path_included=True, multiple_files=False, multiple_snippets_per_file=False)
# parsed_to_txt(parsed, 'unsplit_d4j/', changed_key='changedFiles')

# Create filenames
filenames = ['train', 'val', 'test']

# Split training and test
train_size = 0.6
split_index = floor(len(parsed) * train_size)
training = parsed[:split_index]
testing = parsed[split_index:]

# Split test into half, so that test and val is same size
split_index = floor(len(testing) * 0.5)
testing = testing[split_index:]
validation = testing[:split_index]


print(f'{len(testing) = }')
print(f'{len(validation) = }')
print(f'{len(training) = }')

parsed_to_txt(training, 'defects4j/', output_name='-train', changed_key='changedFiles')
parsed_to_txt(validation, 'defects4j/', output_name='-val', changed_key='changedFiles')
parsed_to_txt(testing, 'defects4j/', output_name='-test', changed_key='changedFiles')