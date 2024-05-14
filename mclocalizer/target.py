import abc
from dataclasses import dataclass


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


@dataclass
class FileTarget(Target):
    """Represents file target in repository."""

    path: str
    """Relative path to a file in repository."""

    def get_identifier(self) -> str:
        return self.path


@dataclass
class JavaClassTarget(Target):
    """Represents java class target in repository."""

    package: str
    """Java class package."""
    class_name: str
    """Java class name."""

    def get_identifier(self) -> str:
        return f"{self.package}.{self.class_name}"
