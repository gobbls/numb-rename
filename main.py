#!/usr/bin/env python3

#
# TODO:
# - Add ability to fill numbering-gaps by either picking files
#   from the very end of the directory or progressivly move
#   the entire tree "upwards" to close the gap
#   (takes more time, but has its purpose)
#
# - Find all the files already normalized in a directory before starting,
#   instead of checking if the file is normalized _during_ the operation.
#


from args import args

import os
import re
import itertools
import mimetypes


def add_padding(string: str, length: int, padding_char: str = "0") -> str:
    """
    Adds padding to the left of a given string to fit a wanted length.

    Args:
        string (str): The string you want to add padding.
        length (int): The length you want the string to be after padding is added.
        padding_char (str): The character you want to use as padding [default = "0"].

    Returns:
        str: The given string; with padding.
    """

    # fmt: off
    padding_amount  = length - len(string)
    padding         = padding_char * padding_amount
    _string         = padding + string
    # fmt: on

    return _string


def normalize_file_name(path: str, new_name: str, name_len: int) -> str:
    """
    Normalizes a given name by adding matching length of character-
    padding (if enabled by flag) and lowercase the extension.

    Args:
        path (str): The target filepath.
        new_name (str): The new filename.
        name_len (int): The wanted length of the new name, used for padding.

    Returns:
        str: The new name as a full path.
    """

    # fmt: off
    name =      os.path.basename(path)
    padding =   "0" * (name_len - len(new_name)) if args.padding else ""
    ext =       "." + name.split(".")[-1].lower() if "." in name else ""
    nname =     padding + new_name + ext
    parent =    os.path.dirname(path)
    nnamep =    os.path.join(parent, nname)
    # fmt: on

    return nnamep


def check_already_normalized(path: str, amount: int) -> bool:
    """
    Check if a file is already normalized, to avoid colliding with it or
    unecessarily normalize it.

    Args:
        path (str): The target filepath.
        amount (int): The amount of files in the directory the target belongs.

    Returns:
        bool: If the file has been normalized or not.
    """

    amount_len = len(str(amount))
    name = os.path.basename(path)
    wo_ext = name.rsplit(".", 1)[0]

    if not wo_ext.isnumeric():
        return False

    if args.padding:
        if len(wo_ext) != amount_len:
            return False

        pad_size = 0

        try:
            p = r"^(0+?)\1*"
            m = re.match(p, wo_ext)
            pad_size = len(m.group(0))
        except AttributeError:
            pass

        file_num = int(wo_ext[pad_size:])

        return file_num <= amount

    else:
        return wo_ext[0] != "0" and int(wo_ext) <= amount


def sort_paths_by_numbered_prefix(paths: [str]) -> [str]:
    """
    Takes a list of strings and sorts them based on their numbered prefix (numerically),
    then the strings that lacks a numbered prefix; by their letter (alphanumerically).

    Args:
        paths ([list]): The list of paths you want to sort.

    Returns:
        [str]: The given list sorted numerically.
    """

    numbered_prefix = []
    non_numbered_prefix = []

    for path in paths:
        name = os.path.basename(path)
        res = re.findall(r"\d+", name)
        non_numbered_prefix.append(path) if not res else numbered_prefix.append(path)

    numbered_prefix = sorted(
        numbered_prefix,
        key=lambda path: int(re.findall(r"\d+", os.path.basename(path))[0]),
    )

    non_numbered_prefix = sorted(non_numbered_prefix)

    _sorted = list(itertools.chain(numbered_prefix, non_numbered_prefix))

    return _sorted


def filter_non_media_files(paths: [str]) -> [str]:
    """
    Return the given list, keeping only the media files (image or video).

    This filtering is based on the files' MIME type.

    Args:
        paths ([str]): The list of filepaths to check.

    Returns:
        [str]: The same array with non-media files removed.
    """

    media_files = []

    for path in paths:
        if not os.path.isfile(path):
            continue

        mime_type, mime_encoding = mimetypes.guess_file_type(path)
        media_type = mime_type.split("/")[0]

        if media_type == "image" or media_type == "video":
            media_files.append(path)

    return media_files


def remove_empty_dir(path: str) -> None:
    print(f'[!] "{path}" is empty, removing...')

    try:
        os.rmdir(path)
    except PermissionError as e:
        print(
            f"[!!] You do not have permission to remove {path}!"
            + f"Got error:\n\n{e}\n\nContinuing as normal..."
        )
    except:  # noqa
        print(f"[!!] Unknown error while removing {path}! Continuing as normal...")


def recur(path: str, iteration: int = 1) -> None:
    print(f"[>] working on: {path}")

    unprocessed_files = os.listdir(path)

    if not unprocessed_files:
        return remove_empty_dir(path) if args.delete_empty_dir else None

    # fmt: off
    full_paths =    [os.path.join(path, n) for n in unprocessed_files]
    used_names =    [n.rsplit('.', 1)[0] for n in unprocessed_files]
    dir_paths =     [p for p in full_paths if os.path.isdir(p)]
    media_files =   filter_non_media_files(paths=full_paths)
    sorted_paths =  sort_paths_by_numbered_prefix(media_files)
    len_literal =   len(str(len(media_files)))
    # fmt: on

    #
    # TODO:
    # Fix --carry-over currently not working due to matching with
    # the amount of files in the file's directory.
    #
    _iter = iteration if args.carry_over else 1

    for file in sorted_paths:
        name = os.path.basename(file).rsplit(".", 1)[0]
        is_normalized = check_already_normalized(file, len(media_files))
        name_is_unique = used_names.count(name) == 1

        if is_normalized and name_is_unique:
            continue

        while True:
            new_name = normalize_file_name(
                path=file,
                new_name=str(_iter),
                name_len=len_literal,
            )
            _new_name = os.path.basename(new_name).rsplit(".")[0]

            _iter += 1

            if _new_name not in used_names:
                used_names.append(_new_name)
                break

        print(f"[D] Renaming {file} ==> {new_name}")
        os.rename(file, new_name)

    if args.recursive:
        for dir in dir_paths:
            recur(dir, iteration=_iter)


def main() -> None:
    for t in args.targets:
        recur(t)

    print("\nDone!")


if __name__ == "__main__":
    main()
