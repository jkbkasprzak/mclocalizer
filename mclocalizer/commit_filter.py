import re

import pydriller as pyd

from mclocalizer.base import CommitFilter


class FixKeywordCommitFilter(CommitFilter):
    """Filter that returns True only for commits that mention fixing something in their message."""

    _pattern = re.compile(
        r"(\bfix\b)|(\bfixed\b)|(\bfixes\b)|(\bfixing\b)", re.IGNORECASE
    )

    def filter(self, commit: pyd.Commit) -> bool:
        return re.search(FixKeywordCommitFilter._pattern, commit.msg) is not None
