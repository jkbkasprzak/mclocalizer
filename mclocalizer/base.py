import abc
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

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


@dataclass
class Target(abc.ABC):
    """Abstract class that represents target in specific commit.

    Target is an entity that exists in the repository and can contain bugs (for example file or class).
    """

    def __str__(self) -> str:
        return self.get_identifier()

    @abc.abstractmethod
    def get_identifier(self) -> str:
        """Get target unique identifier.
        If two targets have same identifier within a single commit they are considered the same target.

        :returns: string that identifies the target.
        :rtype: str
        """
        pass


class TargetExplorer(abc.ABC):
    """Abstract class for finding targets in modified files."""

    def __init__(self):
        self._collected_targets = dict()

    @property
    def collected_targets(self) -> Tuple[Target]:
        """Targets that has been modified."""
        return tuple(self._collected_targets.values())

    def _add_target(self, target: Target):
        """Add target to the list of already collected targets."""
        self._collected_targets[target.get_identifier()] = target

    def reset(self) -> None:
        """Reset already collected targets."""
        self._collected_targets = dict()

    @abc.abstractmethod
    def find_modified(self, file: pyd.ModifiedFile) -> None:
        """Find what targets were modified in specific file.
        Updates collected targets property.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        """
        pass


@dataclass
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
        """Commit was processed but changed targets were not identified."""

        COMPLETE = 3
        """Commit was processed and changed targets were successfully identified."""

    commit: pyd.Commit
    "Commit under investigation"
    kind: Kind
    "Report kind"
    targets: Tuple[Target] = tuple()
    "Targets that were changed by the commit"


class Extension(abc.ABC):
    """
    Abstract class for generating additional text information for CommitReport.
    """

    @abc.abstractmethod
    def process(self, commit_report: CommitReport) -> str:
        """
        Process report and get information in human readable form.

        :param commit_report: commit report to be processed
        :type commit_report: CommitReport
        :returns: human readable string with additional information.
        :rtype: str
        """
        pass
