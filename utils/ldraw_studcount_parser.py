import enum

@enum.unique
class LineType(enum.Enum):

    # pylint: disable=invalid-name
    UNKNOWN = 'Unknown'
    PARTS = 'Parts'


def line_type(line):
    if line.startswith('1 '):
        return LineType.PARTS
    else:
        return LineType.UNKNOWN
