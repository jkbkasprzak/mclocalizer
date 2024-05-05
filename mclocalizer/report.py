from typing import Dict, List, Tuple

from mclocalizer.mclocalizer import CommitReport


class Report:
    def __init__(
        self,
    ):
        self._changes = dict()

    @property
    def changes(self) -> Dict[str, int]:
        return self._changes

    def process(self, commit_report: CommitReport) -> None:
        for symbol in commit_report.changes:
            self._changes[symbol] = self._changes.get(symbol, 0) + 1

    def gen_stats(self) -> List[Tuple[str, int]]:
        return sorted(
            ((name, count) for name, count in self._changes.items()),
            key=lambda e: e[1],
            reverse=True,
        )
