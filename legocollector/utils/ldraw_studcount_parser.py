import datetime
import enum
import json
import os

from pathlib import Path, PureWindowsPath


class SubfileMissingError(Exception):
    """Subfile is Missing Exception."""


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
    STUD_RING = 'Stud Ring'


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
                rel_file = os.path.join(rel_dir, file_name)

                if not ignore_duplicates and rel_file in self:
                    raise ValueError(F'Error: Cannot handle multiple Part Locations, Duplicate File: {rel_file}')

                # Don't add duplicates
                if rel_file not in self:
                    self[rel_file] = Path(full_dir) / rel_file

    @staticmethod
    def _keytransform(key) -> str:
        return Path(str(key).lower())

    def __setitem__(self, key, value: str) -> None:
        self._files[self._keytransform(key)] = Path(value)

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

    def __contains__(self, item: str):
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

    underside_stud_file_names = [
        'stud3.dat', 'stud3a.dat', 'studx.dat', 'stud12.dat', 
    ]

    stud_ring_file_names = [
        'stud16.dat', 'stud21a.dat', 'stud22a.dat', 'stud4.dat', 'stud4a.dat',
        'stud4fns.dat', 'stud4h.dat', 'stud4o.dat', 'stud4od.dat']
    # Invisible Stud rings to ignore,
    #   Sloped: stud4s.dat, stud4s2.dat

    check_name = file_name.lower()
    if check_name in top_stud_file_names:
        file_type = FileType.TOP_STUD
    elif check_name in underside_stud_file_names:
        file_type = FileType.UNDERSIDE_STUD
    elif check_name in stud_ring_file_names:
        file_type = FileType.STUD_RING

    return file_type


def get_stud_count_for_file_type(file_path, file_type):
    if get_ldraw_file_type(os.path.basename(file_path)) == file_type:
        return 1
    return 0


def print_sub_files(file_path, file_dic, *, prefix=None, level=0):
    base_name = os.path.basename(file_path)
    if not prefix or base_name.lower().startswith(prefix.lower()):
        print(F'{level * 2 * " "}{os.path.basename(file_path)} - {get_ldraw_file_type(base_name)}')
    ldraw_file = LdrawFile(file_path)
    for sub_file in ldraw_file.sup_part_files:
        sub_file_path = file_dic[sub_file]
        print_sub_files(sub_file_path, file_dic, prefix=prefix, level=level + 1)


def calc_stud_count_for_part_file(
        file_path, file_dic, processed_files_dic=None, file_visited_count=None, rec_level=0):
    if processed_files_dic is None:
        processed_files_dic = {}
    if file_visited_count is not None:
        if file_path not in file_visited_count:
            file_visited_count[file_path] = 1
        else:
            file_visited_count[file_path] += 1

    top_stud_count = get_stud_count_for_file_type(file_path, FileType.TOP_STUD)
    underside_stud_count = get_stud_count_for_file_type(file_path, FileType.UNDERSIDE_STUD)
    stud_ring_count = get_stud_count_for_file_type(file_path, FileType.STUD_RING)

    # Process sub files
    if not any([top_stud_count, underside_stud_count, stud_ring_count]):
        ldraw_file = LdrawFile(file_path)
        for sub_file in ldraw_file.sup_part_files:

            try:
                sub_file_path = file_dic[sub_file]
            except KeyError:
                raise SubfileMissingError(F'"{file_path}" misses Subfile "{sub_file}"')

            if sub_file_path in processed_files_dic:
                top_stud_count += processed_files_dic[sub_file_path]['top_stud_count']
                underside_stud_count += processed_files_dic[sub_file_path]['underside_stud_count']
                stud_ring_count += processed_files_dic[sub_file_path]['stud_ring_count']
            else:
                try:
                    calc_stud_count_for_part_file(
                        sub_file_path, file_dic, processed_files_dic,
                        file_visited_count, rec_level + 1)
                except SubfileMissingError as error:
                    raise SubfileMissingError(F'{file_path} -> {error}')

                top_stud_count += processed_files_dic[sub_file_path]['top_stud_count']
                underside_stud_count += processed_files_dic[sub_file_path]['underside_stud_count']
                stud_ring_count += processed_files_dic[sub_file_path]['stud_ring_count']

    if file_path not in processed_files_dic:
        processed_files_dic[file_path] = {
            'top_stud_count': top_stud_count,
            'underside_stud_count': underside_stud_count,
            'stud_ring_count': stud_ring_count}


def calc_stud_count_for_part_list(part_list, file_dic):
    parts_dic = {}
    processed_files_dic = {}

    start_time = datetime.datetime.now()

    for idx, file_path in enumerate(part_list, 1):
        part_num = os.path.splitext(os.path.basename(file_path))[0]
        parts_dic[part_num] = {}
        try:
            calc_stud_count_for_part_file(file_path, file_dic, processed_files_dic)
        except SubfileMissingError as error:
            parts_dic[part_num]['processing_errors'] = [str(error)]
        else:
            parts_dic[part_num]['top_stud_count'] = processed_files_dic[file_path]['top_stud_count']
            parts_dic[part_num]['underside_stud_count'] = processed_files_dic[file_path]['underside_stud_count']
            parts_dic[part_num]['stud_ring_count'] = processed_files_dic[file_path]['stud_ring_count']

        if idx % 500 == 0:
            now = datetime.datetime.now()
            print(F'Processed {idx} parts - {(now - start_time).total_seconds():<4} seconds')
            start_time = now

    return parts_dic


def generate_part_list_to_process(dir_list):

    part_dic = {}
    for part_dir in dir_list:
        for file_name in os.listdir(part_dir):
            file_name = file_name.lower()
            file_path = Path(part_dir) / file_name
            if os.path.isfile(file_path) and file_name not in part_dic:
                part_dic[file_name] = Path(part_dir) / file_name

    return part_dic.values()


def create_json_for_parts(json_out_file_path):
    parts_dir = R'D:\Downloads\Finished\# Lego\ldraw\complete_2019.11.05\ldraw\parts'
    prim_dir = R'D:\Downloads\Finished\# Lego\ldraw\complete_2019.11.05\ldraw\p'
    unofficial_parts_dir = R'D:\Downloads\Finished\# Lego\ldraw\ldrawunf_2019.11.14\parts'
    unofficial_primitives_dir = R'D:\Downloads\Finished\# Lego\ldraw\ldrawunf_2019.11.14\p'

    file_dic = FileListDic(
        parts_dir=parts_dir, primitives_dir=prim_dir,
        unofficial_parts_dir=unofficial_parts_dir, unofficial_primitives_dir=unofficial_primitives_dir)

    part_list = generate_part_list_to_process([parts_dir, unofficial_parts_dir])
    print(F'Number of parts to process: {len(part_list)}')

    parts_dic = calc_stud_count_for_part_list(part_list, file_dic)

    with open(json_out_file_path, 'w', encoding='utf-8') as file_ptr:
        json.dump(parts_dic, file_ptr)


if __name__ == '__main__':
    create_json_for_parts('ldraw_studcount.json')
