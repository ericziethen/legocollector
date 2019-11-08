import os

import pytest

from utils import ldraw_studcount_parser as ldraw_parser
from utils.ldraw_studcount_parser import LineType, FileType

REL_THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ABS_PARENT_DIR = os.path.abspath(os.path.join(REL_THIS_FILE_DIR, os.pardir))
LDRAW_TEST_FILE_DIR = os.path.join(ABS_PARENT_DIR, R'test_files\ldraw_files')

PRIMITIVED_LDRAW_FILE_DIR = os.path.join(LDRAW_TEST_FILE_DIR, 'primitives')
PARTS_LDRAW_FILE_DIR = os.path.join(LDRAW_TEST_FILE_DIR, 'parts')


KEY_FILE_NAMES = [
    ('lower.txt', 'lower.txt'),
    ('UPPER.TXT', 'upper.txt'),
    ('Mixed.TxT', 'mixed.txt'),
]
@pytest.mark.parametrize('file_name, key', KEY_FILE_NAMES)
def test_key_from_file_name(file_name, key):
    assert ldraw_parser.key_from_file_name(file_name) == key


def test_invalid_parts_line():
    line = 'Invalid Line'
    assert ldraw_parser.line_type_from_line(line) == LineType.UNKNOWN


LINE_TYPES = [
    (LineType.COMMENT, '0 ~Plate  1 x  3 without Front Face'),
    (LineType.PART, '1 16 0 0 0 1 0 0 0 1 0 0 0 1 10a.dat'),
    (LineType.LINE, '2 24 1 0 0 0.9239 0 0.3827'),
    (LineType.TRIANGLE, '3 5 0 -0.25 -32.37 11.6 -0.25 -14.15 -11.6 -0.25 -14.15'),
    (LineType.QUAD, '4 5 0 -0.25 -32.37 -11.6 -0.25 -14.15 -14.93 -0.25 -15.68 -8.76 -0.25 -24.57'),
    (LineType.OPTIONAL, '5 24 100.05 -.25 -16.79 100.05 0 -16.79 99.79 -.25 -19.84 100.95 -.25 -14.08')
]
@pytest.mark.parametrize('line_type, line', LINE_TYPES)
def test_identify_line_type(line_type, line):
    assert ldraw_parser.line_type_from_line(line) == line_type


UNKNOWN_PART_LINES = [
    ('Unknown Line'),
]
@pytest.mark.parametrize('line', UNKNOWN_PART_LINES)
def test_identify_unknown_line_type(line):
    assert ldraw_parser.line_type_from_line(line) == LineType.UNKNOWN


def test_get_part_file_from_part_line():
    part_line = '1 16 0 0 0 1 0 0 0 1 0 0 0 1 10a.dat'
    assert ldraw_parser.get_file_from_part_line(part_line) == '10a.dat'


TOP_STAT_FILES = [
    ('stud.dat'),
    ('studa.dat'),
    ('studp01.dat'),
    ('studel.dat'),
    ('stud10.dat'),
    ('stud15.dat'),
    ('stud2.dat'),
    ('stud2a.dat'),
    ('stud2s.dat'),
    ('stud17a.dat'),
    ('stud9.dat'),
    ('stud6.dat'),
    ('stud6a.dat'),
    ('stud3.dat'),
]
@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_file_is_top_stud_file(file_name):
    assert ldraw_parser.get_ldraw_file_type(file_name) == FileType.TOP_STUD


UNDERSIDE_STAT_FILES = [
    ('stud3a.dat'),
    ('studx.dat'),
    ('stud12.dat'),
    ('stud4.dat'),
    ('stud4a.dat'),
    ('stud4s.dat'),
    ('stud4s2.dat'),
    ('stud4o.dat'),
    ('stud4od.dat'),
    ('stud4h.dat'),
    ('stud4fns.dat'),
    ('stud16.dat'),
    ('stud21a.dat'),
    ('stud22a.dat'),
]
@pytest.mark.parametrize('file_name', UNDERSIDE_STAT_FILES)
def test_file_is_underside_stud_file(file_name):
    assert ldraw_parser.get_ldraw_file_type(file_name) == FileType.UNDERSIDE_STUD


UNKNOWN_FILES = [
    ('UnknownFile.dat'),
]
@pytest.mark.parametrize('file_name', UNKNOWN_FILES)
def test_unknown_file(file_name):
    assert ldraw_parser.get_ldraw_file_type(file_name) == FileType.UNKNOWN


def test_get_stud_count_for_unknown_file():
    assert ldraw_parser.get_top_stud_count_for_file('UnknownFile.dat') == 0


@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_get_stud_count_for_stud_files(file_name):
    assert ldraw_parser.get_top_stud_count_for_file(file_name) == 1


STUD_COUNT_PARTS = [
    (0, '3070b'),
    (1, '3024'),
]
'''
    (1, '60477'),
    (, ''),
    (, ''),
    (, ''),
    (, ''),
    (, ''),
    (, ''),
'''
@pytest.mark.parametrize('stud_count, part_num', STUD_COUNT_PARTS)
def test_get_stud_count(stud_count, part_num):
    assert stud_count == ldraw_parser.get_top_stud_count_for_file(F'{part_num}.dat')



''' 
files with top stud
    ('stud.dat'),
    ('studa.dat'),
    ('studp01.dat'),
    ('studel.dat'),
    ('stud10.dat'),
    ('stud15.dat'),
    ('stud2.dat'),
    ('stud2a.dat'),
    ('stud2s.dat'),
    ('stud17a.da'),
    ('stud9.dat'),
    ('stud6.dat'),
    ('stud6a.dat'),
    ('stud3.dat'),

files with top stud
    ('stud3a.dat'),
    ('studx.dat'),
    ('stud12.dat'),
    ('stud4.dat'),
    ('stud4a.dat'),
    ('stud4s.dat'),
    ('stud4s2.dat'),
    ('stud4o.dat'),
    ('stud4od.dat'),
    ('stud4h.dat'),
    ('stud4fns.dat'),
    ('stud16.dat'),
    ('stud21a.dat'),
    ('stud22a.dat'),
'''

@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_build_dir_finds_top_stud_files(file_name):
    file_key = ldraw_parser.key_from_file_name(file_name)
    file_dic = ldraw_parser.build_file_path_list(
        PRIMITIVED_LDRAW_FILE_DIR, PARTS_LDRAW_FILE_DIR)
    assert file_key in file_dic
    assert os.path.join(PRIMITIVED_LDRAW_FILE_DIR, file_name) == file_dic[file_key]



# TODO - Find files in part dir












# TODO - Test Build file dir with test files - keep files local for testing


