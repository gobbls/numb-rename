import argparse

__all__ = ["args"]

_parser = argparse.ArgumentParser(
    prog="numb-renamer",
    description="Numerize all media files in given directories, recursing all child directories or not.",
)

_parser.add_argument("targets", nargs="+")

_parser.add_argument(
    "-p", "--padding", help="Add zero-padding to the filenames.", action="store_true"
)

_parser.add_argument(
    "-r",
    "--recursive",
    help="Recurse through child directories of given target.",
    action="store_true",
)

_parser.add_argument(
    "-d",
    "--delete-empty-dir",
    help="Delete empty directories we stumble upon (-r Required).",
    action="store_true",
)

_parser.add_argument(
    "--pre-check",
    help="Check if the renaming process will go as planned before running the process. Usefull for large directories.",
    action="store_true",
)

_parser.add_argument(
    "-c",
    "--carry-over",
    help="Let the file-numeration carry over to the next directory, instead of resetting to zero.",
    action="store_true",
)

args = _parser.parse_args()
