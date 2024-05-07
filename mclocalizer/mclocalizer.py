from enum import Enum
from typing import Generator, List

import pydriller as pyd

from mclocalizer.commit_filter import CommitFilter
from mclocalizer.explorer import TargetExplorer
from mclocalizer.file_filter import FileFilter


class CommitReport:
    """
    Result of commit analysis.
    """

    class Kind(Enum):
        """Describes kind of generated commit report."""

        ERROR = 0
        """Error has occured and report is incorrect."""

        FILTERED = 1
        """Commit was filtered out and was not processed."""

        EMPTY = 2
        """Commit was processed but changes were not identified."""

        COMPLETE = 3
        """Commit was processed and changes were successfully identified."""

    def __init__(self, commit: pyd.Commit):
        """
        Create empty report for given commit.

        :param commit: commit under investigation
        :type commit: pyd.Commit
        """
        self._commit = commit
        self._changes = []
        self._kind = CommitReport.Kind.ERROR

    @property
    def commit(self) -> pyd.Commit:
        """
        Commit under investigation.
        """
        return self._commit

    @property
    def kind(self) -> Kind:
        """
        Report kind.
        """
        return self._kind

    @property
    def changes(self) -> List[str]:
        """
        Targets that were changed by the commit.
        """
        return self._changes


class McLocalizer:
    """
    Responsible for localizing problematic targets in software repository.
    """

    def __init__(
        self,
        repo_path: str,
        commit_filters: List[CommitFilter],
        file_filters: List[FileFilter],
        explorer: TargetExplorer,
    ):
        self._git_repo = pyd.Git(repo_path)
        self._commit_filters = commit_filters
        self._file_filters = file_filters
        self._explorer = explorer

    @property
    def repo(self) -> str:
        """
        Path to git repository.
        """
        return self._git_repo.path.as_posix()

    @repo.setter
    def repo(self, value: str):
        self._git_repo = pyd.Git(value)

    @property
    def commit_filters(self) -> List[CommitFilter]:
        """
        Filters for processing only relevant commits.
        """
        return self._commit_filters

    @commit_filters.setter
    def commit_filters(self, value: List[FileFilter]):
        self._commit_filters = value

    @property
    def file_filters(self) -> List[FileFilter]:
        """
        Filters for processing only relevant files.
        """
        return self._file_filters

    @file_filters.setter
    def file_filters(self, value: List[FileFilter]):
        self._file_filters = value

    @property
    def explorer(self) -> TargetExplorer:
        """
        Explorer responsible for identyfying what targets were changed.
        """
        return self._explorer

    @explorer.setter
    def explorer(self, value: TargetExplorer):
        self._explorer = value

    def total_commits(self) -> int:
        """
        Number of commits to process.
        """
        return self._git_repo.total_commits()

    def gen_reports(self) -> Generator[CommitReport, None, None]:
        """
        Process commits and generate reports.

        :returns: generator that produces a sequence of reports.
        :rtype: Generator[CommitReport]
        """
        for commit in self._git_repo.get_list_commits():
            self.__result = CommitReport(commit)
            self._process_commit(commit)
            yield self.__result

    def _filter_commit(self, commit: pyd.Commit) -> bool:
        return all(filter.filter(commit) for filter in self._commit_filters)

    def _filter_file(self, file: pyd.ModifiedFile) -> bool:
        return all(filter.filter(file) for filter in self._file_filters)

    def _process_commit(self, commit: pyd.Commit) -> None:
        if not self._filter_commit(commit):
            self.__result._kind = CommitReport.Kind.FILTERED
            return

        for file in commit.modified_files:
            self._process_file(file)
        if len(self.__result._changes) > 0:
            self.__result._kind = CommitReport.Kind.COMPLETE
        else:
            self.__result._kind = CommitReport.Kind.EMPTY

    def _process_file(self, file: pyd.ModifiedFile) -> None:
        if not self._filter_file(file):
            return

        self.__result._changes = self.__result._changes + self._explorer.find_modified(
            file
        )
