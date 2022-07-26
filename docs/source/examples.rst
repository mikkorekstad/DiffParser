========
Examples
========

The most useful features to the end-user is located in the parser.py module.

Parse single diff with changes in multiple files:
-------------------------------------------------

.. literalinclude:: ../../src/example_scripts/parse_multi_file_diff.py
   :language: python

Parse single diff with changes in a single file:
-------------------------------------------------

.. literalinclude:: ../../src/example_scripts/parse_single_file_diff.py
   :language: python

Parse list of diffs with changes in a single file:
--------------------------------------------------

.. literalinclude:: ../../src/example_scripts/parse_list_of_single_file_diffs.py
   :language: python

From Json to parsed txt-files:
------------------------------

This next example will show how to take a json file, parse it and then store the parsed code to two files.
In this example, with the output names set to '', we will get the output files src.txt and tgt.txt

.. literalinclude:: ../../src/example_scripts/parse_from_json.py
   :language: python