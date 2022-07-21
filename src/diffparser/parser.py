import separate_diff
import json


def parse_diff(diff, path_included):
    return separate_diff.separate_diff(diff, path_included)


def parse_list_of_commits(commits, path_included, diff_key='diff', changed_key='changedFiles'):  # TODO: Specify in docs what commit is

    if not path_included:
        for commit in commits:
            parsed_commit = separate_diff.separate_diff(commit[diff_key], path_included)
            commit['oldCode'] = parsed_commit['oldCode']
            commit['newCode'] = parsed_commit['newCode']

    if path_included:
        for commit in commits:
            parsed_commit = separate_diff.separate_diff(commit[diff_key], path_included)
            changed_files = list(commit[changed_key].keys())
            for key, value in parsed_commit.items():
                commit_key = [file_name for file_name in changed_files if file_name in key][0]
                commit[changed_key][commit_key]['oldCode'] = value['oldCode']
                commit[changed_key][commit_key]['newCode'] = value['newCode']
    return commits


def read_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def read_jsonl(file_name):
    data = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data


def parsed_to_txt(parsed_lst, output_path):
    old_codes = [commit['oldCode'] for commit in parsed_lst]
    new_codes = [commit['newCode'] for commit in parsed_lst]
    code_lst = [old_codes, new_codes]
    for code, extension in zip(code_lst, ['src', 'tgt']):
        with open(output_path + extension + '.txt', 'w') as fp:
            for element in code:
                for line in element:
                    input_line = ''.join(pair for pair in line)
                    fp.writelines(input_line + '\n')


if __name__ == '__main__':
    """Example parser."""
    # data_set = '../../data/pypi-bugs/pypi-bugs.jsonl'
    data_set = '../../data/sample.json'
    unparsed_list = read_json(data_set)
    parsed_list = parse_list_of_commits(unparsed_list, path_included=True)
    print(f'{parsed_list = }')

    # to_txt(parsed_list, output_path='../../data/pypi-bugs/outputTest/')
    # save_to_single_txt(old_, new_, '../../data/pypi-bugs/output/')
    # multi_file_diff = "--- a/source/org/jfree/data/DefaultKeyedValues.java\n+++ b/source/org/jfree/data/DefaultKeyedValues.java\n@@ -315,30 +315,29 @@ private void rebuildIndex () {\n     public void removeValue(int index) {\n         this.keys.remove(index);\n         this.values.remove(index);\n-        if (index < this.keys.size()) {\n         rebuildIndex();\n-        }\n     }\n \n     /**\n      * Removes a value from the collection.\n      *\n      * @param key  the item key (<code>null</code> not permitted).\n      * \n      * @throws IllegalArgumentException if <code>key</code> is \n      *     <code>null</code>.\n      * @throws UnknownKeyException if <code>key</code> is not recognised.\n      */\n     public void removeValue(Comparable key) {\n         int index = getIndex(key);\n         if (index < 0) {\n-\t\t\treturn;\n+            throw new UnknownKeyException(\"The key (\" + key \n+                    + \") is not recognised.\");\n         }\n         removeValue(index);\n     }\n     \n     /**\n      * Clears all values from the collection.\n      * \n      * @since 1.0.2\n      */\n--- a/source/org/jfree/data/DefaultKeyedValues2D.java\n+++ b/source/org/jfree/data/DefaultKeyedValues2D.java\n@@ -454,12 +454,21 @@ public void removeColumn(int columnIndex) {\n     public void removeColumn(Comparable columnKey) {\r\n+    \tif (columnKey == null) {\r\n+    \t\tthrow new IllegalArgumentException(\"Null 'columnKey' argument.\");\r\n+    \t}\r\n+    \tif (!this.columnKeys.contains(columnKey)) {\r\n+    \t\tthrow new UnknownKeyException(\"Unknown key: \" + columnKey);\r\n+    \t}\r\n         Iterator iterator = this.rows.iterator();\r\n         while (iterator.hasNext()) {\r\n             DefaultKeyedValues rowData = (DefaultKeyedValues) iterator.next();\r\n+            int index = rowData.getIndex(columnKey);\r\n+            if (index >= 0) {\r\n                 rowData.removeValue(columnKey);\r\n+            }\r\n         }\r\n         this.columnKeys.remove(columnKey);\r\n     }\r\n \r\n     /**\r\n      * Clears all the data and associated keys.\r\n      */\r\n"
    # single_file_diff = "@@ -330,7 +330,7 @@ class DialsScaler(Scaler):\n           Debug.write('X1698: %s: %s' % (pointgroup, reindex_op))\n \n           if ntr:\n-            integrater.integrater_reset_reindex_operator()\n+            intgr.integrater_reset_reindex_operator()\n             need_to_return = True\n \n         if pt and not probably_twinned:\n"
    # print(parse_diff(multi_file_diff, path=True))
    # print(diff_to_parsed(single_file_diff, path=False))
