#!/usr/bin/env python3

import re
from tempfile import mkstemp
from shutil import copymode
from glob import glob
import os
import argparse
import sys

class PathException(Exception):
    pass


class UndoException(Exception):
    pass

def delete_absolute_paths (file_path, patt, checks_undos):
    try:
        modified = False
        is_possible_undo = False
        is_undo_started = False
        # ceate temporary file
        fh, tmp_path = mkstemp()
        with open(file_path) as fin, open(tmp_path, "w+") as fout:
            for line in fin:
                # only operate on lines that start with "<template "
                if re.match("<template ", line):
                    # if the relative path of a template is relpath="Templates/... fail
                    if re.search(" relpath=\"(?:Templates|TemplatesOMAP)\/(?:[^\/.])+?\..+?\" ", line) is None:
                        raise PathException("Templates should be located in %(s)sTemplates or %(s)sTemplatesOMAP" % {"s": patt})
                    #  substitute the absolute path with the relative path
                    new_line = re.sub(" path=\"" + patt, " path=\"", line)
                    if new_line != line:
                        line = new_line
                        modified = True
                if checks_undos:
                    if re.match("<barrier version=\"6\" required=\"0.6.0\">", line):
                        is_possible_undo = True
                        old_line = line
                    else:
                        if is_possible_undo:
                            if re.match("<undo", line) is None and re.match("<redo", line) is None:
                                fout.write(old_line)
                            else:
                                is_undo_started = True
                            is_possible_undo = False
                        if not is_undo_started:
                            fout.write(line)
                        else:
                            modified = True
                            if re.match("</barrier>", line) is not None:
                                is_undo_started = False
                else:
                    fout.write(line)
        if modified:
            # copy the file permissions from the old file to the new file
            copymode(file_path, tmp_path)
            # remove original file
            os.remove(file_path)
            # move new file
            os.rename(tmp_path, file_path)
            return file_path
        else:
            return None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def check_map_paths_and_undos (file_path, checks_undos):
    with open(file_path) as fin:
        for line in fin:
            # only operate on lines that start with "<template "
            if re.match("<template ", line):
                # if the relative path of a template is relpath="Templates/... fail
                if re.search(" relpath=\"(?:Templates|TemplatesOMAP)\/(?:[^\/.])+?\..+?\" ", line) is None:
                    raise PathException("Templates should be located in Templates or TemplatesOMAP in %s" % file_path)
                if re.search(" path=\"(?:Templates|TemplatesOMAP)\/(?:[^\/.])+?\..+?\" ", line) is None:
                    raise PathException("The filepath %s needs to be cleaned" % file_path)
            if checks_undos:
                if re.match("<undo>", line) is not None or re.match("<redo>", line) is not None:
                    raise UndoException("File %s contains the undo/redo history" % file_path)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(
            prog='paths_util',
            description='Removes or checks for absolute paths in omap files'
        )
        parser.add_argument(
            'input',
            nargs='*', default=None, type=str,
            help='''
                files or directory to operate on, defaults to the repo directory.
                Multiple files or a single directory can be specified.
                if a directory is specified, *.omap files are searched recursively.'''
        )
        parser.add_argument(
            '-p', '--pattern',
            required=False, type=str,
            help='''
                pattern to remove from the template path specification,
                defaults to the directory of the file being analyzed.'''
        )
        parser.add_argument(
            '-m', '--modify_map',
            required=False, action="store_true",
            help='''
                whether to modify the map files or just check it.
                False if not specified.'''
        )
        parser.add_argument(
            '-u', '--check_undos',
            required=False, action="store_true",
            help='''
                whether to check and/or modify the undo/redo history.
                False if not specified.'''
        )
        args = parser.parse_args()
        input = args.input
        patt = args.pattern
        is_modifier = args.modify_map
        checks_undos = args.check_undos

        is_directory = False
        if input == []:
            input = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0] + "/"
            is_directory = True
        elif len(input) == 1:
            if os.path.exists(input[0]):
                if os.path.isdir(input[0]):
                    is_directory = True
                    input = input[0]
        if not is_directory:
            for f in input:
                if os.path.exists(f):
                    if not f.endswith('.omap'):
                        raise ValueError('The requested file %s is not an .omap file' % f)
                else:
                    raise ValueError('The requested input %s does not exist' % f)

        if is_directory:
            input = glob(os.path.join(input, "**/*.omap"), recursive=True)
        patt = [os.path.split(os.path.abspath(i))[0] + "/" if patt is None else patt for i in input]

        if is_modifier:
            modified = map(lambda i, p: delete_absolute_paths(i, p, checks_undos), input, patt)
            print(f'Files modified by the script: {", ".join(f for f in modified if f is not None)}')
        else:
            [check_map_paths_and_undos(i, checks_undos) for i in input]
            print(f'Files checked by the script: {", ".join(f for f in input)}')

        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)