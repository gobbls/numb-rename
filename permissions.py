from pathlib import Path
import os


__all__ = ["Permissions"]


class PermissionError:
    MISSING_WRITE = "Missing WRITE permissions!"
    MISSING_EXECUTE = "Missing EXECUTE (rename) permissions!"


class Permissions:
    errors: dict[str, [str]] = {}  # { "common_error_message": ["path/to/dir"] }

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self._check_can_remove_and_rename()

    def _check_can_remove_and_rename(self) -> None:
        if not os.access(self.path, os.X_OK):
            Permissions.errors[PermissionError.MISSING_EXECUTE].append(self.path)
        if not os.access(self.path, os.W_OK):
            Permissions.errors[PermissionError.MISSING_WRITE].append(self.path)

    @property
    def OK(self) -> bool:
        return Permissions.errors is None
