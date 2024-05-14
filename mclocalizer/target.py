from dataclasses import dataclass

from mclocalizer.base import Target


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
