from file import File
from pathlib import Path
from permissions import Permissions
import itertools
import re


class Directory:
    # fmt: off
    def __init__(
        self,
        path: Path,
        include_child_directories: bool = False,
        media_only: bool                = False,
        remove_empty: bool              = False,
        file_num_carries_over: bool     = False,
        add_filename_padding: bool      = False,
    ) -> None:
        self.path: Path                         = path
        self.include_child_directories: bool    = include_child_directories
        self.media_only: bool                   = media_only
        self.remove_empty: bool                 = remove_empty
        self.file_num_carries_over: bool        = file_num_carries_over
        self.add_filename_padding: bool         = add_filename_padding
        self.perms: Permissions                 = Permissions(path)
        self.child_directories: [Directory]     = []
        self.child_files: [File]                = []
        self.is_empty: bool                     = False
        self.file_amount: int                   = 0
        # fmt: on

        if self.perms.OK:
            self._collect()
            if self.child_files:
                if self.media_only:
                    self._filter_non_media()
                self._sort_files()
                self._add_files_data()

    def _collect(self) -> None:
        paths = self.path.iterdir()
        if not paths:
            self.is_empty = True
            return
        for path in paths:
            if path.isfile():
                self.child_files.append(File(path=path))
                self.file_amount += 1
            elif path.isdir() and self.include_child_directories:
                self.directory.append(
                    Directory(
                        path,
                        self.include_child_directories,
                        self.media_only,
                        self.remove_empty,
                    )
                )

    def _sort_files(self) -> None:
        """
        First sort exclusively by the numbers found in the names,
        then by letter if there is no numbers.
        """
        num_prefix: [Path] = []
        non_num_prefix: [Path] = []
        for path in self.child_files:
            res = re.findall(r"\d+", path.name)
            non_num_prefix.append(path) if not res else num_prefix.append(path)
        num_prefix = sorted(
            num_prefix,
            key=lambda path: int(re.findall(r"\d+", path.name)[0]),
        )
        non_num_prefix = sorted(non_num_prefix)
        self.child_files = list(itertools.chain(num_prefix, non_num_prefix))

    def _add_files_data(self) -> None:
        """
        Appending information from (this) Directory to the
        files after sorting and filtering is complete.
        """
        for i, f in enumerate(self.child_files):
            f.files = self.file_amount
            f.num = i

    def _filter_non_media(self) -> None:
        self.child_files = [f for f in self.child_files if f.is_media]

    def _remove_dir(self) -> None:
        self.path.rmdir()

    def run(self) -> None:
        for d in self.child_directories:
            d.run()
        for f in self.child_files:
            f.run(self.add_filename_padding)
        if self.is_empty and self.remove_empty:
            self._remove_dir()
