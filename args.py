import argparse

__all__ = ["args"]

_parser = argparse.ArgumentParser(
    prog="numb-renamer",
    description="Numerize all media files in given directories, recursing all child directories or not.",
)

_parser.add_argument("targets", nargs="+")

_parser.add_argument(
    "--disable-padding",
    help="Add zero('0')-padding to the filenames to align the names with the amount.",
    action="store_false",
)

_parser.add_argument(
    "--disable-media-only",
    help="Include all files (not directories) in a directory, not only the media files.",
    action="store_false",
)

_parser.add_argument(
    "--carry-over",
    help="Let the file-numeration carry over to the next directory, instead of resetting to zero.",
    action="store_true",
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

args = _parser.parse_args()
