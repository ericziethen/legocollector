import os

from pathlib import Path

import pytest

from utils import ldraw_studcount_parser as ldraw_parser
from utils.ldraw_studcount_parser import FileListDic, FileType, LineType

REL_THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
LDRAW_TEST_FILE_DIR = Path('legocollector') / 'tests' / 'test_files' / 'ldraw_files'
LDRAW_PARTS_DIR = LDRAW_TEST_FILE_DIR / 'part_files'
LDRAW_PRIMITIVES_DIR = LDRAW_TEST_FILE_DIR / 'primitives'
LDRAW_PARTS_DIR_UNOFFICIAL = LDRAW_TEST_FILE_DIR / 'unofficial_part_files'
LDRAW_PRIMITIVES_DIR_UNOFFICIAL = LDRAW_TEST_FILE_DIR / 'unofficial_primitives'


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
    assert ldraw_parser.get_file_from_part_line(part_line) == Path('10a.dat')


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


def test_find_subdir_file():
    file_name = Path('s/10s01.dat')
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    key = Path(file_name)
    assert key in file_dic


@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_build_dir_finds_top_stud_primitives(file_name):
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    key = Path(file_name)
    assert key in file_dic

    primitives_dir = os.path.join(LDRAW_TEST_FILE_DIR, 'primitives')
    assert Path(primitives_dir) / file_name == file_dic[key]


def test_get_sub_files_from_file():
    file_name = os.path.join('s', '3070bs01.dat')
    key = Path(file_name)

    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert key in file_dic

    file_path = file_dic[key]
    ldraw_file = ldraw_parser.LdrawFile(file_path)

    sup_part_files = ldraw_file.sup_part_files

    assert len(sup_part_files) == 3
    assert sup_part_files.count(Path('box4.dat')) == 2
    assert sup_part_files.count(Path('box5.dat')) == 1


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
    key = Path(file_name)
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert key in file_dic
    file_path = file_dic[key]
    assert stud_count == ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic)


def test_processed_files_dic_specified():
    file_name = '3024.dat'
    key = Path(file_name)
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    file_path = file_dic[key]
    processed_files_dic = {}

    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic)
    assert len(processed_files_dic.values()) == 3

    assert processed_files_dic[LDRAW_PARTS_DIR / '3024.dat']['top_stud_count'] == 1
    assert processed_files_dic[LDRAW_PRIMITIVES_DIR / 'box5.dat']['top_stud_count'] == 0
    assert processed_files_dic[LDRAW_PRIMITIVES_DIR / 'stud.dat']['top_stud_count'] == 1


def test_file_visited_count():
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    file_path = file_dic['3024.dat']
    file_visited_count = {}
    processed_files_dic = {}

    # Run 1st time
    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic, file_visited_count)
    assert len(file_visited_count.values()) == 3
    assert file_visited_count[LDRAW_PARTS_DIR / '3024.dat'] == 1
    assert file_visited_count[LDRAW_PRIMITIVES_DIR / 'box5.dat'] == 1
    assert file_visited_count[LDRAW_PRIMITIVES_DIR / 'stud.dat'] == 1

    # Run 2nd time
    ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic, file_visited_count)
    assert len(file_visited_count.values()) == 3
    assert file_visited_count[LDRAW_PARTS_DIR / '3024.dat'] == 2
    assert file_visited_count[LDRAW_PRIMITIVES_DIR / 'box5.dat'] == 1
    assert file_visited_count[LDRAW_PRIMITIVES_DIR / 'stud.dat'] == 1


def test_calc_stud_count_for_part_list():
    part_list = ['3070b', '3024', '30099', '912']

    stud_count_dic = ldraw_parser.calc_stud_count_for_part_list(
        part_list, parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)

    assert len(stud_count_dic) == 4
    assert stud_count_dic['3070b']['stud_count'] == 0
    assert stud_count_dic['3024']['stud_count'] == 1
    assert stud_count_dic['30099']['stud_count'] == 2
    assert stud_count_dic['912']['stud_count'] == 76


UNOFFICIAL_FILES = [
    ('2048.dat'),       # in parts
    ('s/3587s01.dat'),    # in parts/s
    ('stud26.dat'),     # in primitives
    ('8/stud4hlf.dat'),   # in primitives/8
    ('48/1-4ring15.dat'),  # in primitives/48
]
@pytest.mark.parametrize('file_name', UNOFFICIAL_FILES)
def test_unofficial_missing_parts_included(file_name):
    key = Path(file_name)

    # Check file not found in official Parts
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert key not in file_dic

    # Check file found un Unofficial Parts
    file_dic = FileListDic(
        parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR,
        unofficial_parts_dir=LDRAW_PARTS_DIR_UNOFFICIAL,
        unofficial_primitives_dir=LDRAW_PRIMITIVES_DIR_UNOFFICIAL)
    assert key in file_dic


def test_can_handle_duplicate_unofficial_files():
    duplicate_part_file = '92947.dat'
    key = Path(duplicate_part_file)

    # Check file not found in official Parts
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert key in file_dic

    # Check file found un Unofficial Parts
    file_dic = FileListDic(
        parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR,
        unofficial_parts_dir=LDRAW_PARTS_DIR_UNOFFICIAL,
        unofficial_primitives_dir=LDRAW_PRIMITIVES_DIR_UNOFFICIAL)
    assert key in file_dic


STUD_COUNT_MISSING_UNOFFICIAL_PARTS = [
    (1+12, '2048.dat'),
    (1+6, '3587s01.dat'),
]
@pytest.mark.parametrize('stud_count, part_num', STUD_COUNT_MISSING_UNOFFICIAL_PARTS)
def test_unofficial_missing_part_stud_count(stud_count, part_num):
    file_name = F'{part_num}.dat'
    key = Path(file_name)
    file_dic = FileListDic(parts_dir=LDRAW_PARTS_DIR, primitives_dir=LDRAW_PRIMITIVES_DIR)
    assert key in file_dic
    file_path = file_dic[key]
    assert stud_count == ldraw_parser.calc_stud_count_for_part_file(file_path, file_dic)
