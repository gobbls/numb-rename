#!/usr/bin/env python3


#
# KNOWN QUIRK(s):
#
# 1. When files in a directory is already renamed from a first-time-run;
#    Running the script again will still rename the files if;
#    the files are not in the same position / index as the first run
#    due to how unix lists files in order: 1, 10, 11, 12, ...2, 20, 21...
#
#    - Can be fixed by prefixing numbers with:
#      "0" * (longest_file_name_len - current_file_name_len)
#      
#      But this beats the convention I want to follow here,
#      since I usually use Thunar to browse media files anyways.
#


import os
from sys import argv


TARGET = argv[1]


def get_new_name(name: str, num: int) -> str:
    '''
    Takes a filename (the entire path) and simplifies
    it to a unique number as well as making the entire
    name (the remaining extension that is...) lower-case.

    Args:
        `name` (str): The old filename (full path).
        `num` (int): The number used as the filename.

    Returns:
        `str`: The new name as a full path, with the extension lower'cased.
    '''

    if '.' not in name:
        raise ValueError(f'[ERROR] {name} does not contain an exstension!')

    extension = name.split('.')[-1].lower()
    parent = os.path.dirname(name)
    new_name = os.path.join(parent, f'{num}.{extension}')

    return new_name


def recur(path: str) -> None:
    paths = os.listdir(path)

    if paths == []:
        print(f'[WARNING] "{path}" is empty! Deleting...')
        
        try:
            os.rmdir(path)
        except PermissionError as e:
            raise PermissionError(f"[ERROR] You do not have permission to delete {path}! Got error:\n{e}")
        except:
            raise Exception(f"[ERROR] Unknown error while removing {path}!")

        return

    iter = 1

    for p in paths:
        p_path = os.path.join(path, p)

        if os.path.isdir(p_path):
            recur(p_path)

        elif os.path.isfile(p_path):
            new_name = get_new_name(p_path, iter)
            iter += 1

            if (p_path == new_name):
                continue

            try:
                os.rename(p_path, new_name)
            except FileExistsError as e:
                raise FileExistsError(f'[ERROR] {new_name} already exists! Got error:\n{e}')
            except:
                raise Exception(f"[ERROR] Unknown error while renaming {path}!")


def main() -> None:
    recur(TARGET)
    print("\nDone!")


if __name__ == '__main__':
    main()
