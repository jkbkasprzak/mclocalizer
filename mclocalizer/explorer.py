import abc
from typing import List, Tuple

import pydriller as pyd
import tree_sitter as ts
import tree_sitter_java as tsjava

import mclocalizer.target as mctarget


class TargetExplorer(abc.ABC):
    """Abstract class for finding modified targets."""

    def __init__(self):
        self._collected_targets = dict()

    @property
    def collected_targets(self) -> Tuple[mctarget.Target]:
        return tuple(self._collected_targets.values())

    def _add_target(self, target: mctarget.Target):
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


class FileExplorer(TargetExplorer):
    """Explorer that finds file targets."""

    def find_modified(self, file: pyd.ModifiedFile) -> None:
        for path in (file.new_path, file.old_path):
            if path is not None:
                self._add_target(mctarget.FileTarget(path))


class JavaClassExplorer(TargetExplorer):
    """Explorer that finds java top level class targets."""

    _java_lang = ts.Language(tsjava.language(), "java")
    _query = _java_lang.query(
        """
        (package_declaration (scoped_identifier) @name)
        (class_declaration  name: (identifier) @name) @definition.type
        (interface_declaration name: (identifier) @name) @definition.type
        (enum_declaration name: (identifier) @name) @definition.type
        """
    )

    def __init__(self):
        self._parser = ts.Parser()
        self._parser.set_language(JavaClassExplorer._java_lang)

    def find_modified(self, file: pyd.ModifiedFile) -> None:
        diff_parsed = file.diff_parsed
        if len(diff_parsed["added"]) > 0:
            self._find_affected_classes(diff_parsed["added"], file.content)
        if len(diff_parsed["deleted"]) > 0:
            self._find_affected_classes(diff_parsed["deleted"], file.content_before)

    def _find_affected_classes(
        self, modified_lines: List[Tuple[int, str]], source: bytes
    ) -> None:
        classes = self.explore_source(source)
        for changed_line, _ in modified_lines:
            for java_class, class_start, class_end in classes:
                # TODO: Verify if this check is correct (consistent indexing)
                if class_start <= changed_line and changed_line <= class_end:
                    self._add_target(java_class)

    def explore_source(
        self, source: bytes
    ) -> List[Tuple[mctarget.JavaClassTarget, int, int]]:
        """Find java top level classes in source code.

        :param source: java source code
        :type source: bytes
        :returns: List of (java_class, class_start_line, class_end_line) tuples
        :rtype: List[Tuple[JavaClassTarget, int, int]]
        """
        classes = list()
        package = ""
        tree = self._parser.parse(source)
        matches = JavaClassExplorer._query.matches(tree.root_node)
        for match in matches:
            # check if match first package sexp in _query
            if match[0] == 0:
                captured = match[1]
                s = captured["name"].range.start_byte
                e = captured["name"].range.end_byte
                package = tree.text[s:e].decode()
            else:
                captured = match[1]
                s = captured["name"].range.start_byte
                e = captured["name"].range.end_byte
                parent = captured["definition.type"].parent
                # only return top level types
                if parent.type == "program":
                    classes.append(
                        [
                            tree.text[s:e].decode(),
                            captured["definition.type"].start_point[0],
                            captured["definition.type"].end_point[0],
                        ]
                    )
        for i in range(len(classes)):
            classes[i][0] = mctarget.JavaClassTarget(package, classes[i][0])
            classes[i] = tuple(classes[i])
        return classes
