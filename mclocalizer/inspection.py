from enum import Enum
from typing import Dict, Generator, List, Set, Tuple

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
        self._blame = set()
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

    @property
    def blame(self) -> Set[str]:
        """
        Hashes for commits whose lines have been deleted. Result of SZZ algorithm.
        """
        return self._blame


class RepoInspector:
    """
    Responsible for processing commits and generating reports.

    For commits that pass provided commit_filters obtain a list of modified files.
    For files that pass provided file_filters identify changed targets with provided target explorer.
    """

    def __init__(
        self,
        repo_path: str,
        commit_filters: List[CommitFilter],
        file_filters: List[FileFilter],
        explorer: TargetExplorer,
    ):
        """
        Create new repository analyzer.

        :param repo_path: path to git repository to investigate
        :type repo_path: str
        :param commit_filters: filters for processing only relevant commits
        :type commit_filters: List[CommitFilter]
        :param file_filters: filters for processing only relevant files.
        :type file_filters: List[FileFilter]
        :param explorer: explorer responsible for identyfying what targets were changed.
        :type explorer: TargetExplorer
        """
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
            self._process_file(commit, file)
        if len(self.__result._changes) > 0:
            self.__result._kind = CommitReport.Kind.COMPLETE
        else:
            self.__result._kind = CommitReport.Kind.EMPTY

    def _process_file(self, commit: pyd.Commit, file: pyd.ModifiedFile) -> None:
        if not self._filter_file(file):
            return
        blame = self._git_repo.get_commits_last_modified_lines(commit, file)
        for hashes in blame.values():
            self.__result._blame.update(hashes)
        self.__result._changes = self.__result._changes + self._explorer.find_modified(
            file
        )


class TargetTracker:
    """
    Responsible for collecting target statistics from commit reports.
    """

    def __init__(self):
        """
        Create new target tracker.
        """
        self._stats = dict()

    @property
    def stats(self) -> Dict[str, int]:
        """
        Dictionary with target identifier and fix count.
        """
        return self._stats

    def collect(self, commit_report: CommitReport) -> None:
        """
        Update statistics with data from commit report.

        :param commit_report: report to collect data from
        :type commit_report: CommitReport
        """
        for symbol in commit_report.changes:
            self._stats[symbol] = self._stats.get(symbol, 0) + 1

    def gen_stats(self) -> List[Tuple[str, int]]:
        """
        Get ordered list of most fixed targets.

        :returns: List of (target, fix_count) tuples, ordered by fix_count in descending order.
        :rtype: List[Tuple[str, int]]
        """
        return sorted(
            ((name, count) for name, count in self._stats.items()),
            key=lambda e: e[1],
            reverse=True,
        )
