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


class AlwaysTrueFilter(CommitFilter):
    """Filter that returns True for all the commits."""

    def filter(self, commit: pyd.Commit) -> bool:
        return True


class CommitFilterDecorator(CommitFilter):
    """Abstract class that allows to chain multiple filters together.

    New filters should inherit from this class and override _check function.
    """

    def __init__(self, prev_filter: CommitFilter = AlwaysTrueFilter()):
        """Creates new filter

        :param prev_filter: filter to check before this filter
        :type prev_filter: CommitFilter
        """
        self.prev_filter = prev_filter

    def filter(self, commit: pyd.Commit) -> bool:
        return self.prev_filter.filter(commit) and self._check(commit)

    @abc.abstractmethod
    def _check(self, commit: pyd.Commit) -> bool:
        """Checks whether the commit passes.

        :param commit: commit to be checked
        :type commit: pyd.Commit
        :returns: boolean, whether the commit has passed the filter
        :rtype: bool
        """
        pass


class FixKeywordFilter(CommitFilterDecorator):
    """Filter that returns True only for commits that mention fixing something in their message."""

    _pattern = re.compile(
        r"(\bfix\b)|(\bfixed\b)|(\bfixes\b)|(\bfixing\b)", re.IGNORECASE
    )

    def _check(self, commit: pyd.Commit) -> bool:
        return re.search(FixKeywordFilter._pattern, commit.msg) is not None
