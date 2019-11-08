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


def line_type(line):
    if line.startswith('0 '):
        return LineType.COMMENT
    elif line.startswith('1 '):
        return LineType.PART
    elif line.startswith('2 '):
        return LineType.LINE
    elif line.startswith('3 '):
        return LineType.TRIANGLE
    elif line.startswith('4 '):
        return LineType.QUAD
    elif line.startswith('5 '):
        return LineType.OPTIONAL

    return LineType.UNKNOWN
