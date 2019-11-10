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


class FileListDic():

    # TODO - We should only need the base dir and get folders to include ourselves,
    # TODO - Then the key should be the hols relative path
    # TODO - then remove from transform below
    def __init__(self, import_dir_list):

        #self._files = defaultdict(str)
        self._files = {}

        for import_dir in import_dir_list:
            self._parse_dir(import_dir)

    def _parse_dir(self, file_dir):
        file_list = [f for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f))]
        for file_name in file_list:
            if file_name in self:
                raise ValueError(F'Error: Cannot handle multiple Part Locations, Duplicate File: {file_name}')
            self[file_name] = os.path.join(file_dir, file_name)

    @staticmethod
    def _keytransform(key) -> str:
        # TODO - Check if we're fine with flattening the key, s\file.dat becomes file.dat
        return str(os.path.basename(key.lower()))

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
                check_line = line.strip()
                if line_type_from_line(check_line) == LineType.PART:
                    self.sup_part_files.append(get_file_from_part_line(check_line))


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
        'stud15.dat', 'stud2.dat', 'stud2a.dat', 'stud17a.dat',
        'stud9.dat', 'stud6.dat', 'stud6a.dat']

    check_name = file_name.lower()
    if check_name in top_stud_file_names:
        file_type = FileType.TOP_STUD

    return file_type


def get_top_stud_count_for_file(file_name):
    single_top_stud_file_types = [FileType.TOP_STUD]
    if get_ldraw_file_type(file_name) in single_top_stud_file_types:
        return 1
    return 0

# TODO REMOVE
ERIC_FILE_VISIT_COUNT = defaultdict(int)
ERIC_studs_used = defaultdict(int)
# TODO - Count how often each file is being processed
def calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic=None, rec_level=0):
    #print(F'{rec_level * "  "} Processing: {file_path}')
    file_name = os.path.basename(file_path)
    count = get_top_stud_count_for_file(file_name)
    ERIC_FILE_VISIT_COUNT[file_name] += 1

    # Process sub files
    if count == 0:
        ldraw_file = LdrawFile(file_path)
        for sub_file in ldraw_file.sup_part_files:
            ##print(F'{rec_level * "  "}   Checking Sub File: {sub_file} ({get_top_stud_count_for_file(sub_file)})')
            if get_top_stud_count_for_file(sub_file):
                ERIC_studs_used[sub_file] += 1
            if processed_files_dic and sub_file in processed_files_dic:
                count += processed_files_dic[sub_file]['top_stud_count']
                #print(F'{rec_level * "  "}   Count (Dict): {count}')
            else:
                count += calc_stud_count_for_part_file(file_dic[sub_file], file_dic, processed_files_dic, rec_level + 1)
                #print(F'{rec_level * "  "}   Count (Calc): {count}')
                '''
                if not processed_files_dic:
                    processed_files_dic = {}
                processed_files_dic[sub_file] = {'top_stud_count': count}
                '''
                #print(F'{rec_level * "  "}   Add {file_name} as processed with {count} studs')
    if not processed_files_dic:
        processed_files_dic = {}
    processed_files_dic[file_name] = {'top_stud_count': count}
    #print(F'{rec_level * "  "}   Returning Count: {count}')

    if rec_level == 0:
        #print(F'Studs Used: {ERIC_studs_used}')

        visited = '\n'.join(['%s:: %s' % (key, value) for (key, value) in ERIC_FILE_VISIT_COUNT.items()])
        #print(F'VISITED: {visited}')

    return count

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






