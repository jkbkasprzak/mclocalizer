from typing import Dict, Generator, List, Tuple

import pydriller as pyd

from mclocalizer.base import CommitFilter, CommitReport, FileFilter, TargetExplorer


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
            yield self._process_commit(commit)

    def _process_commit(self, commit: pyd.Commit) -> CommitReport:
        if not all(filter.filter(commit) for filter in self._commit_filters):
            return CommitReport(commit, CommitReport.Kind.FILTERED)

        extra = dict()
        extra["szz"] = set()
        self.explorer.reset()
        for file in commit.modified_files:
            if all(filter.filter(file) for filter in (self._file_filters)):
                self.explorer.find_modified(file)
                blame = self._git_repo.get_commits_last_modified_lines(commit, file)
                for hashes in blame.values():
                    extra["szz"].update(hashes)
        targets = self.explorer.collected_targets

        if len(targets) > 0:
            return CommitReport(commit, CommitReport.Kind.COMPLETE, targets, extra)
        else:
            return CommitReport(commit, CommitReport.Kind.EMPTY, targets, extra)


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
        for target in commit_report.targets:
            identifier = target.get_identifier()
            self._stats[identifier] = self._stats.get(identifier, 0) + 1

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
