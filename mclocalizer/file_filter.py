import re
from typing import Optional

import pydriller as pyd

from mclocalizer.base import FileFilter


class JavaFileFilter(FileFilter):
    """Filter that returns True only for java source files."""

    def _is_java_file(self, path: Optional[str]) -> bool:
        return path is not None and path.endswith(".java")

    def filter(self, file: pyd.ModifiedFile) -> bool:
        return self._is_java_file(file.old_path) or self._is_java_file(file.new_path)


class NoTestDirFileFilter(FileFilter):
    """Filter that returns True only for files outside of test directories."""

    _pattern = re.compile(
        r"(\btest\b)|(\btested\b)|(\btests\b)|(\btesting\b)",
        re.IGNORECASE,
    )

    def filter(self, file: pyd.ModifiedFile) -> bool:
        test_dir = False
        for path in (file.old_path, file.new_path):
            if path is not None:
                test_dir = test_dir or (
                    re.search(NoTestDirFileFilter._pattern, path) is not None
                )

        return not test_dir


class NoNewFileFilter(FileFilter):
    """Filter that returns True only for files that already existed in repository prior to commit."""

    def filter(self, file: pyd.ModifiedFile) -> bool:
        return file.old_path is not None


class NoDeletedFileFilter(FileFilter):
    """Filter that returns True only for files that continue to exist in repository after the commit."""

    def filter(self, file: pyd.ModifiedFile) -> bool:
        return file.new_path is not None
