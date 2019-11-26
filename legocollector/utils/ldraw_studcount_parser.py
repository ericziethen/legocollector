import enum
import json
import os

from pathlib import Path, PureWindowsPath


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

    def __init__(self, *, parts_dir, primitives_dir,
                 unofficial_parts_dir=None, unofficial_primitives_dir=None):
        self._files = {}

        self._parse_dir(parts_dir)
        self._parse_dir(primitives_dir)

        if unofficial_parts_dir is not None:
            self._parse_dir(unofficial_parts_dir, ignore_duplicates=True)

        if unofficial_primitives_dir is not None:
            self._parse_dir(unofficial_primitives_dir, ignore_duplicates=True)

    def _parse_dir(self, full_dir, *, ignore_duplicates=False):
        for root, _, files in os.walk(full_dir):
            for file_name in files:
                rel_dir = os.path.relpath(root, start=full_dir)
                rel_file = os.path.join(rel_dir, file_name.lower())

                if not ignore_duplicates and rel_file in self:
                    raise ValueError(F'Error: Cannot handle multiple Part Locations, Duplicate File: {rel_file}')

                # Don't add duplicates
                if rel_file not in self:
                    self[rel_file] = Path(full_dir) / rel_file

    @staticmethod
    def _keytransform(key) -> str:
        return Path(key)

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

    def __contains__(self, item):
        return self._keytransform(item) in self._files


class LdrawFile():

    def __init__(self, file_path):
        self.file_path = file_path
        self.sup_part_files = []

        self._parse(self.file_path)

    def _parse(self, file_path):
        with open(file_path, encoding='utf8', errors="surrogateescape") as file_ptr:
            for line in file_ptr:
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
    return Path(PureWindowsPath(line.split()[-1].lower()))


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


def get_top_stud_count_for_file(file_path):
    single_top_stud_file_types = [FileType.TOP_STUD]
    if get_ldraw_file_type(os.path.basename(file_path)) in single_top_stud_file_types:
        return 1
    return 0


def calc_stud_count_for_part_file(
        file_path, file_dic, processed_files_dic=None, file_visited_count=None, rec_level=0):
    if processed_files_dic is None:
        processed_files_dic = {}

    count = get_top_stud_count_for_file(file_path)
    if file_visited_count is not None:
        if file_path not in file_visited_count:
            file_visited_count[file_path] = 1

        else:
            file_visited_count[file_path] += 1

    # Process sub files
    if count == 0:
        ldraw_file = LdrawFile(file_path)
        for sub_file in ldraw_file.sup_part_files:
            sub_file_path = file_dic[sub_file]

            if sub_file_path in processed_files_dic:
                count += processed_files_dic[sub_file_path]['top_stud_count']
            else:
                sub_file_count = calc_stud_count_for_part_file(
                    sub_file_path, file_dic, processed_files_dic,
                    file_visited_count, rec_level + 1)
                count += sub_file_count

                processed_files_dic[sub_file_path] = {'top_stud_count': sub_file_count}

    if file_path not in processed_files_dic:
        processed_files_dic[file_path] = {'top_stud_count': count}
    return count


def calc_stud_count_for_part_list(part_list, *, parts_dir, primitives_dir):
    parts_dic = {}
    processed_files_dic = {}

    file_dic = FileListDic(parts_dir=parts_dir, primitives_dir=primitives_dir)

    for idx, part_num in enumerate(part_list, 1):
        file_path = os.path.join(parts_dir, F'{part_num}.dat')

        stud_count = calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic)
        parts_dic[part_num] = {}
        parts_dic[part_num]['stud_count'] = stud_count

        if idx % 500 == 0:
            print(F'Processed {idx} parts')

    return parts_dic


def create_json_for_parts(json_out_file_path):
    prim_dir = R'D:\Downloads\Finished\# Lego\ldraw\complete_2019.11.05\ldraw\p'
    parts_dir = R'D:\Downloads\Finished\# Lego\ldraw\complete_2019.11.05\ldraw\parts'

    part_num_list = [
        os.path.splitext(f)[0] for f in os.listdir(parts_dir)
        if os.path.isfile(os.path.join(parts_dir, f)) and f.lower().endswith('.dat')]

    parts_dic = calc_stud_count_for_part_list(
        part_num_list, parts_dir=parts_dir, primitives_dir=prim_dir)

    with open(json_out_file_path, 'w', encoding='utf-8') as file_ptr:
        json.dump(parts_dic, file_ptr)


if __name__ == '__main__':
    create_json_for_parts('ldraw_studcount.json')
