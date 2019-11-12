import os

import pytest

from utils import ldraw_studcount_parser as ldraw_parser
from utils.ldraw_studcount_parser import FileListDic, FileType, LineType

REL_THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
LDRAW_TEST_FILE_DIR = os.path.join('tests', 'test_files', 'ldraw_files')
# TODO - TRY WITH RELATIVE PATH
LDRAW_PARTS_DIR = os.path.abspath(os.path.join(LDRAW_TEST_FILE_DIR, 'part_files'))
LDRAW_PRIMITIVES_DIR = os.path.abspath(os.path.join(LDRAW_TEST_FILE_DIR, 'primitives'))


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
    ('stud17a.dat'),
    ('stud9.dat'),
    ('stud6.dat'),
    ('stud6a.dat'),
]
@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_file_is_top_stud_file(file_name):
    assert ldraw_parser.get_ldraw_file_type(file_name) == FileType.TOP_STUD


UNKNOWN_FILES = [
    ('UnknownFile.dat'),
]
@pytest.mark.parametrize('file_name', UNKNOWN_FILES)
def test_unknown_file(file_name):
    assert ldraw_parser.get_ldraw_file_type(file_name) == FileType.UNKNOWN


@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_build_dir_finds_top_stud_primitives(file_name):
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert file_name in file_dic

    primitives_dir = os.path.join(LDRAW_TEST_FILE_DIR, 'primitives')
    # TODO - TRY WITH RELATIVE PATH
    assert os.path.abspath(os.path.join(primitives_dir, file_name)) == file_dic[file_name]


def test_get_sub_files_from_file():
    file_name = R's\3070bs01.dat'

    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert file_name in file_dic

    file_path = file_dic[file_name]
    ldraw_file = ldraw_parser.LdrawFile(file_path)

    sup_part_files = ldraw_file.sup_part_files

    assert len(sup_part_files) == 3
    assert sup_part_files.count('box4.dat') == 2
    assert sup_part_files.count('box5.dat') == 1


def test_get_stud_count_for_unknown_file():
    assert ldraw_parser.get_top_stud_count_for_file('UnknownFile.dat') == 0


@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_get_stud_count_for_stud_files(file_name):
    assert ldraw_parser.get_top_stud_count_for_file(file_name) == 1


# The aim is to test at least all (top) studs at least in 1 part for good coverage
STUD_COUNT_PARTS = [
    (0, '3070b'),
    (1, '3024'),
    (1, '60477'),
    (2, '30099'),
    (76, '912'),
    (6, '10201'),
    (4, '15469'),
    (764, '10p07'),
    (4, '6233'),
    (4, '92947'),
    (4, '11211'),
    (4, '13547'),
    (4, '6032'),
    (4, '30179'),
    (2, '38317'),
    (4, '44511'),
    (16, '71427c01'),
]
@pytest.mark.parametrize('stud_count, part_num', STUD_COUNT_PARTS)
def test_get_stud_count(stud_count, part_num):
    file_name = F'{part_num}.dat'
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert file_name in file_dic
    file_path = file_dic[file_name]
    assert stud_count == ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic)


def test_processed_files_dic_specified():
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    file_path = file_dic['3024.dat']
    processed_files_dic = {}

    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic)
    assert len(processed_files_dic.values()) == 3
    print(processed_files_dic)
    assert processed_files_dic[os.path.join(LDRAW_PARTS_DIR, '3024.dat').lower()]['top_stud_count'] == 1
    assert processed_files_dic[os.path.join(LDRAW_PRIMITIVES_DIR, 'box5.dat').lower()]['top_stud_count'] == 0
    assert processed_files_dic[os.path.join(LDRAW_PRIMITIVES_DIR, 'stud.dat').lower()]['top_stud_count'] == 1


def test_file_visited_count():
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    file_path = file_dic['3024.dat']
    file_visited_count = {}
    processed_files_dic = {}

    # Run 1st time
    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic, file_visited_count)
    assert len(file_visited_count.values()) == 3
    assert file_visited_count[os.path.join(LDRAW_PARTS_DIR, '3024.dat').lower()] == 1
    assert file_visited_count[os.path.join(LDRAW_PRIMITIVES_DIR, 'box5.dat').lower()] == 1
    assert file_visited_count[os.path.join(LDRAW_PRIMITIVES_DIR, 'stud.dat').lower()] == 1

    # Run 2nd time
    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic, file_visited_count)
    assert len(file_visited_count.values()) == 3
    assert file_visited_count[os.path.join(LDRAW_PARTS_DIR, '3024.dat').lower()] == 2
    assert file_visited_count[os.path.join(LDRAW_PRIMITIVES_DIR, 'box5.dat').lower()] == 1
    assert file_visited_count[os.path.join(LDRAW_PRIMITIVES_DIR, 'stud.dat').lower()] == 1


def test_calc_stud_count_for_part_list():
    part_list = ['3070b', '3024', '30099', '912']

    stud_count_dic = ldraw_parser.calc_stud_count_for_part_list(
        part_list, parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)

    assert len(stud_count_dic) == 4
    assert stud_count_dic['3070b']['stud_count'] == 0
    assert stud_count_dic['3024']['stud_count'] == 1
    assert stud_count_dic['30099']['stud_count'] == 2
    assert stud_count_dic['912']['stud_count'] == 76
