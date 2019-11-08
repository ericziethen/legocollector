import pytest

from utils import ldraw_studcount_parser as ldraw_parser


# test identify valid parts line
def test_valid_parts_line():
    line = '1 16 0 0 0 1 0 0 0 1 0 0 0 1 10a.dat'
    assert ldraw_parser.line_type(line) == ldraw_parser.LineType.PARTS


# test identify invalid parts line




# test getting dat file from line

# identify bottom level top stud files

# identify 

# ...

