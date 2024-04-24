import abc
import re
import pydriller as pyd
from typing import Generator, Iterable


class CommitFilter(abc.ABC):
    def __init__(self, iterable: Iterable[pyd.Commit]):
        self._iterable = iterable

    @abc.abstractmethod
    def __iter__(self) -> Generator[pyd.Commit]:
        pass


class FixKeywordFilter(CommitFilter):
    _pattern = re.compile(
        r"(\bfix\b)|(\bfixed\b)|(\bfixes\b)|(\bfixing\b)", re.IGNORECASE
    )

    def is_fixing(self, commit: pyd.Commit) -> bool:
        return re.search(FixKeywordFilter._pattern, commit.msg) is not None

    def __iter__(self) -> Generator[pyd.Commit]:
        for commit in self._iterable:
            if self.is_fixing(commit):
                yield commit
