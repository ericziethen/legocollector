import enum

@enum.unique
class LineType(enum.Enum):

    # pylint: disable=invalid-name
    UNKNOWN = 'Unknown'
    COMMENT = 'Comments'
    PART = 'Parts'
    LINE = 'Lines'
    TRIANGLE = 'Triangles'
    QUAD = 'Quads'
    OPTIONAL = 'Optional'

@enum.unique
class FileType(enum.Enum):

    # pylint: disable=invalid-name
    UNKNOWN = 'Unknown'
    TOP_STUD = 'Top Stud'
    UNDERSIDE_STUD = 'Underside Stud'


def line_type_from_line(line):
    line_type = LineType.UNKNOWN

    if line.startswith('0 '):
        line_type = LineType.COMMENT
    elif line.startswith('1 '):
        line_type = LineType.PART
    elif line.startswith('2 '):
        line_type = LineType.LINE
    elif line.startswith('3 '):
        line_type = LineType.TRIANGLE
    elif line.startswith('4 '):
        line_type = LineType.QUAD
    elif line.startswith('5 '):
        line_type = LineType.OPTIONAL

    return line_type


def get_file_from_part_line(line):
    return line.split()[-1]


def get_ldraw_file_type(file_name):
    file_type = FileType.UNKNOWN
    top_stud_file_names = [
        'stud.dat', 'studa.dat', 'studp01.dat', 'studel.dat', 'stud10.dat',
        'stud15.dat', 'stud2.dat', 'stud2a.dat', 'stud2s.dat', 'stud17a.da',
        'stud9.dat', 'stud6.dat', 'stud6a.dat', 'stud3.dat']
    underside_stud_file_names = [
        'stud3a.dat', 'studx.dat', 'stud12.dat', 'stud4.dat', 'stud4a.dat',
        'stud4s.dat', 'stud4s2.dat', 'stud4o.dat', 'stud4od.dat', 'stud4h.dat',
        'stud4fns.dat', 'stud16.dat', 'stud21a.dat', 'stud22a.dat']

    check_name = file_name.lower()
    if check_name in top_stud_file_names:
        file_type = FileType.TOP_STUD
    elif check_name in underside_stud_file_names:
        file_type = FileType.UNDERSIDE_STUD

    return file_type


def get_stud_count_for_file(file_name):
    single_stud_file_types = [FileType.TOP_STUD, FileType.UNDERSIDE_STUD]
    if get_ldraw_file_type(file_name) in single_stud_file_types:
        return 1

    return 0
