import abc
import re
from pathlib import PurePath
from typing import Optional

import pydriller as pyd


class FileFilter(abc.ABC):
    """Abstract class for filtering out files."""

    @abc.abstractmethod
    def filter(self, file: pyd.ModifiedFile) -> bool:
        """Checks whether the file passes.

        :param file: file to be checked
        :type file: pyd.Commit
        :returns: boolean, whether the file has passed the filter
        :rtype: bool
        """
        pass


class JavaFileFilter(FileFilter):
    """Filter that returns True only for java source files."""

    def _is_java_file(self, path: Optional[str]) -> bool:
        return path is not None and path.endswith(".java")

    def filter(self, file: pyd.ModifiedFile) -> bool:
        return self._is_java_file(file.old_path) or self._is_java_file(file.new_path)


class NoTestDirFileFilter(FileFilter):
    """Filter that returns True only for files outside of test directories."""

    _pattern = re.compile(
        r"(/test/|(/tested/)|(/tests/)|(/testing/)",
        re.IGNORECASE,
    )

    def __init__(self, repo_root: PurePath) -> bool:
        self._repo_root = repo_root
        if not repo_root.is_absolute():
            raise ValueError("Repository path is not absolute")

    def filter(self, file: pyd.ModifiedFile) -> bool:
        test_dir = False
        for path in (file.old_path, file.new_path):
            if path is not None:
                rel_path = PurePath(path).relative_to(self._repo_root)
                test_dir = test_dir or (
                    re.search(NoTestDirFileFilter._pattern, rel_path.as_posix())
                    is not None
                )

        return not test_dir
