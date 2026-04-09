from pathlib import Path
import mimetypes
import re


class File:
    def __init__(self, path: Path, add_filename_padding: bool = False) -> None:
        # fmt: off
        self.path: Path                 = path
        self.name: str                  = path.stem
        self.add_filename_padding: bool = add_filename_padding
        self.files: int | None          = None
        self.num: int | None            = None
        # fmt: on

        if not self._is_normalized():
            self._normalize()

    def _add_padding(self, string: str, length: int) -> str:
        length = length - len(string)
        padding = "0" * length
        padded = padding + self.name
        return padded

    def _normalize(self) -> None: ...

    def _is_normalized(self) -> None:
        amount_len = len(str(self.files))
        wo_ext = self.path.name.rsplit(".", 1)[0]
        if not wo_ext.isnumeric():
            return False
        if self.add_filename_padding:
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
            return file_num <= self.files
        else:
            return wo_ext[0] != "0" and int(wo_ext) <= self.files

    def run(self) -> None: ...

    @property
    def is_media(self) -> bool:
        mime_type, mime_encoding = mimetypes.guess_file_type(self.path)
        media_type = mime_type.split("/")[0]
        return media_type == "image" or media_type == "video"
