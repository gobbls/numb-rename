#!/usr/bin/env python3


#
# KNOWN QUIRK:
# - If a directory consists of a file named 01.jpg and 1.jpg,
#   both will be ignored, and not renamed.
#


import os
import re
import itertools
import mimetypes
from sys import argv


TARGET = argv[1]


def normalize_file_name(path: str, name: str, file_amount: int) -> str:
    '''
    Renames a file in a given path by;
    prefixing zeroes to the new given `name` to match the amount
    of files is the path (using `longest_num`) and lowercases the extension.

    Args:
        path (str): The target filepath.
        name (str): The new filename.
        file_amount (int): The amount of files in a directory.

    Returns:
        str: The new name as a full path, with the extension lower'cased.

    Raises:
        ValueError: If the given name arg does not contain an extension.
    '''

    if '.' not in path:
        raise ValueError(f'[!!] {path} does not contain an exstension!')

    parent = os.path.dirname(path)
    extension = path.split('.')[-1].lower()
    prefix = "0" * (file_amount - len(name))
    new_name_path = os.path.join(parent, f'{prefix}{name}.{extension}')

    return new_name_path


def sort_numbered_and_non_number_path_name_prefixes(paths: [str]) -> [str]:
    '''
    Takes a list of strings and sorts them based on their numbered prefix (numerically),
    then the strings that lacks a numbered prefix (alphanumerically).

    Args:
        paths ([list]): The list of paths you want to sort.

    Returns:
        [str]: The given list sorted numerically.
    '''

    numbered_prefix = []
    non_numbered_prefix = []

    for path in paths:
        name = os.path.basename(path)

        res = re.findall(r'\d+', name)
        if res == []:
            non_numbered_prefix.append(path)
        else:
            numbered_prefix.append(path)

    numbered_prefix = sorted(
            numbered_prefix,
            key=lambda path: int(re.findall(r'\d+', os.path.basename(path))[0]))

    non_numbered_prefix = sorted(non_numbered_prefix)

    _sorted = list(itertools.chain(numbered_prefix, non_numbered_prefix))

    return _sorted


def filter_non_media_files(paths: [str]) -> [str]:
    '''
    Returns a list of filepaths where the file is determined
    to be either an image or a video.

    Args:
        paths ([str]): The array of filepaths to check.

    Returns:
        [str]: The same array with non-media files removed.
    '''

    media_files = []

    for p in paths:
        if (not os.path.isfile(p)):
            continue

        mime_type, mime_encoding = mimetypes.guess_file_type(p)
        media_type = mime_type.split("/")[0]

        if (media_type == "image" or media_type == "video"):
            media_files.append(p)

    return media_files


def recur(path: str) -> None:
    print(f"[>] working with path: {path}")

    unsorted_files = os.listdir(path)

    if unsorted_files == []:
        print(f'[!] "{path}" is empty! Removing...')
        
        try:
            os.rmdir(path)
        except PermissionError as e:
            raise PermissionError(f"[!!] You do not have permission to delete {path}! Got error:\n{e}")
        except:
            raise Exception(f"[!!] Unknown error while removing {path}!")

        return

    full_paths = [os.path.join(path, p) for p in unsorted_files]
    dir_paths = [p for p in full_paths if os.path.isdir(p)]
    filtered_files = filter_non_media_files(paths=full_paths)
    sorted_paths = sort_numbered_and_non_number_path_name_prefixes(paths=filtered_files)
    target_paths = list(itertools.chain(dir_paths, sorted_paths))
    media_files_amount = len(str(len(target_paths)))

    iter = 1

    for path in target_paths:
        if os.path.isdir(path):
            recur(path)

        elif os.path.isfile(path):
            new_name = normalize_file_name(
                    path=path,
                    name=str(iter),
                    file_amount=media_files_amount)

            iter += 1

            if (new_name in target_paths or path == new_name):
                continue

            os.rename(path, new_name)


def main() -> None:
    recur(TARGET)

    print("\nDone!")


if __name__ == '__main__':
    main()
