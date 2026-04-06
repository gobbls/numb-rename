#!/usr/bin/env python3


#
# KNOWN QUIRK:
#
# If a directory consists of a file named 01.jpg and 1.jpg
# due to a 1.jpg being moved to a already processed directory;
#
# 1.jpg will be ignored and not renamed due to the script
# trying to rename 1.jpg to a file that already has the
# name it is trying to take. This is by intention,
# but this is a edgecase that should be fixed some way or another.
#
# Perhaps move such files to the back of the que / list, giving it a
# higher number-name that will not collide with other filenames.
#


#
# TODO:
# 1. Fix _that_ ^^.
# 2. Add some CL flags.
#    - For adding / not adding zero-padding
#      - Padding symbol (zero (0) as default)
#    - Ability to "pre-check" all targets before running the process,
#      to avoid conflicts during the process for bigger directories.
#      Should not be default, since we already know the possible
#      consequences along the way.
#
# 3. Support for multiple tartgets
#    - And support for the counter to carry over to the next target, or not.
#
# 4. Some errors only affect a single directory, collect those errors and display
#    them when the operation completes in stead of stopping the operation outright.
#


from args import args

import os
import re
import itertools
import mimetypes


def normalize_file_name(path: str, name: str, file_amount_num_literal: int) -> str:
    """
    Renames a file in a given path by;
    prefixing zeroes to the new given `name` to match the amount
    of files is the path (using `longest_num`) and lowercases the extension.

    Args:
        path (str): The target filepath.
        name (str): The new filename.
        file_amount (int): The amount of files in the directory the target belongs.

    Returns:
        str: The new name as a full path, with the extension lower'cased.

    Raises:
        ValueError: If the given name arg does not contain an extension.
    """

    if "." not in path:
        raise ValueError(f"[!!] {path} does not contain an exstension!")

    # fmt: off
    parent =            os.path.dirname(path)
    extension =         path.split(".")[-1].lower()
    padding =           args.padding * (file_amount_num_literal - len(name))
    new_name =          f"{padding}{name}.{extension}"
    new_name_path =     os.path.join(parent, new_name)
    # fmt: on

    return new_name_path


def check_already_normalized(path: str, file_amount: int) -> int | None:
    """
    Check if a file is already normalized, to avoid colliding with it or
    unecessarily normalize it.

    Args:
        path (str): The target filepath.
        file_amount (int): The amount of files in the directory the target belongs.

    Returns:
        int: The filenumber, if the file is already normalized.
        None: If the file was not previously normalized.
    """

    name = os.path.basename(path)

    if "." not in name:
        return None

    without_extension = name.rsplit(".", 1)[0]

    if len(without_extension) != len(str(file_amount)) or name.isnumeric() is False:
        return None

    pad_size = 0

    try:
        p = rf"^({re.escape(args.padding)}+?)\1*"
        m = re.match(p, without_extension)
        pad_size = int(m.group(0))
    except AttributeError:
        pass

    file_number = int(without_extension[pad_size:])

    if file_number <= file_amount:
        return file_number
    else:
        return None


def sort_numbered_and_non_number_path_name_prefixes(paths: [str]) -> [str]:
    """
    Takes a list of strings and sorts them based on their numbered prefix (numerically),
    then the strings that lacks a numbered prefix (alphanumerically).

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
        if res == []:
            non_numbered_prefix.append(path)
        else:
            numbered_prefix.append(path)

    numbered_prefix = sorted(
        numbered_prefix,
        key=lambda path: int(re.findall(r"\d+", os.path.basename(path))[0]),
    )

    non_numbered_prefix = sorted(non_numbered_prefix)

    _sorted = list(itertools.chain(numbered_prefix, non_numbered_prefix))

    return _sorted


def filter_non_media_files(paths: [str]) -> [str]:
    """
    Returns a list of filepaths where the file is determined
    to be either an image or a video.

    This filtering is based on the files MIME type.

    Args:
        paths ([str]): The array of filepaths to check.

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


#
# TODO:
# Add option to remove empty directories the process encounters along the way.
#
def remove_empty_dir(path: str) -> None:
    try:
        os.rmdir(path)
    except PermissionError as e:
        raise PermissionError(
            f"[!!] You do not have permission to delete {path}! Got error:\n{e}"
        )
    except:  # noqa
        raise Exception(f"[!!] Unknown error while removing {path}!")


def recur(path: str) -> None:
    print(f"[>] working with path: {path}")

    unprocessed_files = os.listdir(path)

    if unprocessed_files == []:
        print(f'[!] "{path}" is empty! Removing...')
        return remove_empty_dir(path)

    # fmt: off
    full_paths =                [os.path.join(path, p) for p in unprocessed_files]
    used_names =                [n.rsplit('.', maxsplit=1)[0] for n in full_paths]
    dir_paths =                 [p for p in full_paths if os.path.isdir(p)]
    media_files =               filter_non_media_files(paths=full_paths)
    sorted_paths =              sort_numbered_and_non_number_path_name_prefixes(paths=media_files)
    target_paths =              list(itertools.chain(dir_paths, sorted_paths))
    media_files_num_literal =   len(str(len(target_paths)))
    # fmt: on

    already_normalized = []

    iter = 1

    for path in target_paths:
        if os.path.isdir(path):
            recur(path)
        else:
            normalized = check_already_normalized(path, file_amount=len(target_paths))

            #
            # May already be normalized, but can confilict if there are
            # files with same name, but different extension. Handled
            # by checking if the name appears more than once in the dir.
            #
            name_is_unique = len([(n == normalized) for n in used_names]) == 1

            if normalized is not None and name_is_unique:
                already_normalized.append(normalized)
                continue

            new_name = normalize_file_name(
                path=path,
                name=str(iter),
                file_amount_num_literal=media_files_num_literal,
            )

            #
            # This is already checked by checking if the name is already
            # in use above, so perhaps this shouldn't be needed?
            #
            if new_name in target_paths:
                continue

            os.rename(path, new_name)

            iter += 1


def main() -> None:
    recur(TARGET)
    print("\nDone!")


if __name__ == "__main__":
    main()
