import enum
import operator
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
    def __init__(self, parts_dir='parts', primitives_dir='p'):
        self._files = {}

        self._parse_dir(parts_dir)
        self._parse_dir(primitives_dir)


    def _parse_dir(self, full_dir):
        for root, _, files in os.walk(full_dir):
            for file_name in files:
                rel_dir = os.path.relpath(root, start=full_dir)
                rel_file = os.path.join(rel_dir, file_name).lstrip('.\\')  # We don't want the leading period

                if rel_file in self:
                    raise ValueError(F'Error: Cannot handle multiple Part Locations, Duplicate File: {file_name}')
                self[rel_file] = os.path.join(full_dir, rel_file)

    @staticmethod
    def _keytransform(key) -> str:
        # TODO - Check if we're fine with flattening the key, s\file.dat becomes file.dat
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
        with open(file_path, encoding='utf8', errors="surrogateescape") as fp:
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
# TODO !!! Do we need a wrapper to process multiple parts, then we don't need to pass in dictionaries
# TODO !!! Write a test that tests processed_files_dic
def calc_stud_count_for_part_file(
        file_path, file_dic, processed_files_dic=None, rec_level=0, file_visited_count=None):
    if processed_files_dic is None:
        processed_files_dic = {}

    #print(F'{rec_level * "  "}  >> START Processing: {file_path}')
    file_name = os.path.basename(file_path)
    count = get_top_stud_count_for_file(file_name)
    if file_visited_count is not None:
        file_visited_count[file_path] += 1

    # Process sub files
    if count == 0:
        ldraw_file = LdrawFile(file_path)
        for sub_file in ldraw_file.sup_part_files:
            sub_file = sub_file.lower()
            #print(F'{rec_level * "  "}    Checking Sub File: {sub_file} ({get_top_stud_count_for_file(sub_file)})')
            if get_top_stud_count_for_file(sub_file):
                ERIC_studs_used[sub_file] += 1
            if sub_file in processed_files_dic:
                count += processed_files_dic[sub_file]['top_stud_count']
                #print(F'{rec_level * "  "}   Count (Dict): {count}')
            else:
                sub_file_count = calc_stud_count_for_part_file(file_dic[sub_file], file_dic, processed_files_dic, rec_level + 1)
                count += sub_file_count
                #print(F'{rec_level * "  "}   Count (Calc): {count}')

                processed_files_dic[sub_file] = {'top_stud_count': sub_file_count}
                #print(F'{rec_level * "  "}    Sub Count Set for {sub_file}')

    if file_name not in processed_files_dic:
        processed_files_dic[file_name] = {'top_stud_count': count}
    #print(F'{rec_level * "  "}   Returning Count: {count}')

    #if rec_level == 0:
        #print(F'Studs Used: {ERIC_studs_used}')

        #visited = '\n'.join(['%s:: %s' % (key, value) for (key, value) in ERIC_FILE_VISIT_COUNT.items()])
        #print(F'VISITED: {visited}')

    #print(F'{rec_level * "  "}  >> FINISH Processing: {file_path}')
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




def main():
    prim_dir = R'.eric\ldraw\complete\ldraw\p'
    parts_dir = R'.eric\ldraw\complete\ldraw\parts'

    file_dic = FileListDic(parts_dir=parts_dir, primitives_dir=prim_dir)
    processed_files_dic = {}
    stud_counts = {}

    #for idx, file_name in enumerate(glob.glob(parts_dir + R'\*.dat')):
    for idx, file_name in enumerate(os.listdir(parts_dir)):
        
        #print(F'CHECK: {file_name}')
        file_path = os.path.join(parts_dir, file_name)
        if not os.path.isfile(file_path) or not file_name.lower().endswith('.dat'):
            #print(F'  >> SKIP')
            continue
        #if idx > 5600:
        #    print(F'{file_name}')
        #print(F'{file_name}')
        stud_count = calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic)
        stud_counts[file_name] = stud_count

        if idx % 100 == 0:
            print(F'Processed Files: {idx}')

    sorted_stud_counts = sorted(stud_counts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_stud_counts_str = '\n'.join([F'{tup[1]}:: {tup[0]}' for tup in sorted_stud_counts if tup[1] > 0])
    print(F'STUD COUNTS: {sorted_stud_counts_str}')
    print(F'TOTAL FILE VISITS: {sum(ERIC_FILE_VISIT_COUNT.values())}\n\n')


if __name__ == '__main__':
    main()
