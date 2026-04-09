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
from directory import Directory
from permissions import Permissions


def main() -> None:
    # fmt: off
    targets: [Directory] = [
        Directory(
            path                        = t,
            include_child_directories   = args.recursive,
            media_only                  = args.disable_media_only,
            remove_empty                = args.delete_empty_dir,
            file_num_carries_over       = args.carry_over,
            add_filename_padding        = args.disable_padding
        )
        for t in args.targets
    ]
    # fmt: on

    if errors := Permissions.errors != []:
        print("[!] Operation was cancelled! Found errors when checking permissions!")
        for err, paths in errors.items():
            print(f"Error: [{err}] in these paths:")
            for path in paths:
                print(f"\t'{path}'")
        exit()

    for t in targets:
        t.run()

    print("Done!")


if __name__ == "__main__":
    main()
