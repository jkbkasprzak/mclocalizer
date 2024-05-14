from typing import List

import pydriller as pyd

from mclocalizer.base import CommitReport, Extension, FileFilter


class BlameExtension(Extension):
    """
    Generate additional blame information.
    """

    def __init__(
        self,
        repo_path: str,
        file_filters: List[FileFilter] = [],
        oldest_blame: bool = False,
    ):
        """
        Initialize BlameExtension

        :param repo_path: path to repository
        :type repo_path: str
        :param file_filters: filters for excluding files
        :type file_filters: List[FileFilter]
        :param oldest_blame: if True, process will return single oldest blame commit
        :type oldest_blame: bool
        """
        self._git_repo = pyd.Git(repo_path)
        self._file_filters = file_filters
        self._oldest_blame = oldest_blame

    def process(self, commit_report: CommitReport) -> str:
        """
        Identify commits that added lines that were changed by the given commit.
        Given the fixing commit it applies SZZ algorithm and identifies bug introducing commits.

        :param commit_report: commit report to be processed
        :type commit_report: CommitReport
        :returns: "; " separated list of blame commit hashes.
        :rtype: str
        """
        modifications = []
        for file in commit_report.commit.modified_files:
            if all(filter.filter(file) for filter in (self._file_filters)):
                modifications.append(file)
        if len(modifications) > 0:
            blame = self._git_repo._calculate_last_commits(
                commit_report.commit, modifications
            )
            blame_hashes = set()
            for file, hashes in blame.items():
                blame_hashes.update(hashes)

            if not self._oldest_blame:
                return "; ".join(blame_hashes)
            else:
                oldest = min(
                    blame_hashes,
                    key=lambda hash: self._git_repo.get_commit(hash).author_date,
                    default="",
                )
                return oldest

        return ""
