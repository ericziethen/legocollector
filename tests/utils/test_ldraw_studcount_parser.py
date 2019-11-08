import pytest

from utils import ldraw_studcount_parser as ldraw_parser
from utils.ldraw_studcount_parser import LineType


def test_invalid_parts_line():
    line = 'Invalid Line'
    assert ldraw_parser.line_type(line) == LineType.UNKNOWN


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
    assert ldraw_parser.line_type(line) == line_type





# test getting dat file from line

# identify bottom level top stud files

# identify 

# ...

