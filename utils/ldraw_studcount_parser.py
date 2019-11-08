import enum
import os

from collections import defaultdict

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


class FileDic():

    def __init__(self, primitive_dir, parts_dir):

        self._files = defaultdict(str)

        self._parse_dir(primitive_dir)
        self._parse_dir(parts_dir)

    def _parse_dir(self, file_dir):
        for file_name in os.listdir(file_dir):
            if file_name in self:
                raise ValueError('Error: Cannot handle multiple Part Locations')
            self[file_name] = os.path.join(file_dir, file_name)

    @staticmethod
    def _keytransform(key) -> str:
        return str(key.lower())

    def __setitem__(self, key, value: str) -> None:
        self._files[self._keytransform(key)] = value

    def __getitem__(self, key) -> str:
        return self._files[self._keytransform(key)]

    def __iter__(self):
        return iter(self._files)

    def __len__(self) -> int:
        return len(self._files)

    def __str__(self) -> str:
        return str(self._files)

    def __delitem__(self, key) -> None:
        del self._files[self._keytransform(key)]


class LdrawFile():

    def __init__(self, file_path):
        self.file_path = file_path
        self.sup_part_files = []

        self._parse(self.file_path)

    def _parse(self, file_path):
        with open(file_path) as fp:
            for line in fp:
                if line_type_from_line(line) == LineType.PART:
                    self.sup_part_files.append(get_file_from_part_line(line))


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
        'stud15.dat', 'stud2.dat', 'stud2a.dat', 'stud2s.dat', 'stud17a.dat',
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


def get_top_stud_count_for_file(file_name):
    single_top_stud_file_types = [FileType.TOP_STUD]
    if get_ldraw_file_type(file_name) in single_top_stud_file_types:
        return 1

    return 0



'''

scan file(file)
     count = studs in file
     for each dat subfile in file
          if subfile in global list
              count += global_list[sub_file)
          else
              count += scan file(sub_file)
 

    global_list[file] = count (maybe have a dictionary, e.g. top_studs, bottom_studs…)

    return count

    '''






