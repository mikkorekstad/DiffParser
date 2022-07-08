from diffparser.defects4jdiffparser import Defects4jDiffParser
import pytest
import json
from functools import reduce
from operator import and_


class TestDefects4jParser:
    """TestClass for Defects4jParser"""

    def test_fails_loading_empty_json(self):
        with pytest.raises(json.JSONDecodeError):
            Defects4jDiffParser('test_data/empty_file.json')

    # @pytest.mark.parametrize(['arg1', 'arg2'], [[1, 2], [1, 2]])
    # def test_loads_json(self, arg1, arg2):
    #    assert arg1 == 1
    #    assert arg2 != 2

    @pytest.mark.parametrize('file_name',
                             ['test_data/default_example.json', 'test_data/single_file_multiple_lines.json'])
    def test_loads_json(self, file_name):

        # Test that the parser is of right class
        parser = Defects4jDiffParser(file_name)
        assert isinstance(parser, Defects4jDiffParser)

        # Test that the data is a list of dictionaries
        assert isinstance(parser.data, list)
        # [assert isinstance(element, dict) for element in parser.data]
        assert reduce(and_, [isinstance(element, dict) for element in parser.data])


