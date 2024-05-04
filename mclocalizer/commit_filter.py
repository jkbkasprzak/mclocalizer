import abc
import re

import pydriller as pyd


class CommitFilter(abc.ABC):
    """Abstract class for filtering out commits."""

    @abc.abstractmethod
    def filter(self, commit: pyd.Commit) -> bool:
        """Checks whether the commit passes.

        :param commit: commit to be checked
        :type commit: pyd.Commit
        :returns: boolean, whether the commit has passed the filter
        :rtype: bool
        """
        pass


class FixKeywordCommitFilter(CommitFilter):
    """Filter that returns True only for commits that mention fixing something in their message."""

    _pattern = re.compile(
        r"(\bfix\b)|(\bfixed\b)|(\bfixes\b)|(\bfixing\b)", re.IGNORECASE
    )

    def filter(self, commit: pyd.Commit) -> bool:
        return re.search(FixKeywordCommitFilter._pattern, commit.msg) is not None
