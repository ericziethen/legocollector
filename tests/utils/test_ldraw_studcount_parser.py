import pytest

from utils import ldraw_studcount_parser as ldraw_parser
from utils.ldraw_studcount_parser import LineType


def test_invalid_parts_line():
    line = 'Invalid Line'
    assert ldraw_parser.line_type_from_line(line) == LineType.UNKNOWN


INVALID_PART_LINES = [
    (LineType.COMMENT, '0 ~Plate  1 x  3 without Front Face'),
    (LineType.PART, '1 16 0 0 0 1 0 0 0 1 0 0 0 1 10a.dat'),
    (LineType.LINE, '2 24 1 0 0 0.9239 0 0.3827'),
    (LineType.TRIANGLE, '3 5 0 -0.25 -32.37 11.6 -0.25 -14.15 -11.6 -0.25 -14.15'),
    (LineType.QUAD, '4 5 0 -0.25 -32.37 -11.6 -0.25 -14.15 -14.93 -0.25 -15.68 -8.76 -0.25 -24.57'),
    (LineType.OPTIONAL, '5 24 100.05 -.25 -16.79 100.05 0 -16.79 99.79 -.25 -19.84 100.95 -.25 -14.08')
]
@pytest.mark.parametrize('line_type, line', INVALID_PART_LINES)
def test_identify_line_type(line_type, line):
    assert ldraw_parser.line_type_from_line(line) == line_type


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
    ('stud17a.da'),
    ('stud9.dat'),
    ('stud6.dat'),
    ('stud6a.dat'),
    ('stud3.dat'),
]
@pytest.mark.parametrize('file_name', TOP_STAT_FILES)
def test_file_is_top_stud_file(file_name):
    assert ldraw_parser.is_top_stud_file(file_name)


'''
UNDERSIDE_STAT_FILES = [

stud3a.dat
studx.dat
stud12.dat
stud4.dat
stud4a.dat
stud4s.dat
stud4s2.dat
stud4o.dat
stud4od.dat
stud4h.dat
stud4fns.dat
stud16.dat
stud21a.dat
stud22a.dat


]
'''

#def test_file_is_not_top_stud_file():
# identify bottom level top stud files

# identify 

# ...

# Identify Stud Count !!! 
#TODO - At least 1 file including each top stud file to test against visual confirmation
#At least 1 file including each Underside stud