#!/usr/bin/env python3


import os
from sys import argv


TARGET = argv[1]


def get_new_name(name: str, num: int, longest_num: int) -> str:
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

    parent = os.path.dirname(name)
    extension = name.split('.')[-1].lower()
    new_name = str(num)
    prefix = "0" * (longest_num - len(new_name))
    new_full_name = os.path.join(parent, f'{prefix}{new_name}.{extension}')

    return new_full_name


def recur(path: str) -> None:
    # Append the found files to their parent path.
    paths = [os.path.join(path, p) for p in os.listdir(path)]

    # The longest number by literal characters.
    longest_num = len(str(len(paths)))

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

    for f_path in paths:
        if os.path.isdir(f_path):
            recur(f_path)

        elif os.path.isfile(f_path):
            new_name = get_new_name(f_path, iter, longest_num)
            iter += 1

            if (new_name in paths):
                print(f"[LOG] {new_name} already exists! Continuing without taking action...")
                continue

            if (f_path == new_name):
                print(f"[LOG] {f_path} == {new_name} ignoring same name...")
                continue

            os.rename(f_path, new_name)


def main() -> None:
    recur(TARGET)
    print("\nDone!")


if __name__ == '__main__':
    main()
