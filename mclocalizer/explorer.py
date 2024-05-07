import abc
from typing import List, Set, Tuple

import pydriller as pyd
import tree_sitter as ts
import tree_sitter_java as tsjava


class TargetExplorer(abc.ABC):
    """Abstract class for finding targets in the repository."""

    @abc.abstractmethod
    def find_modified(self, file: pyd.ModifiedFile) -> List[str]:
        """Find what targets were modified.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: list of identifiers that have been affected by the change
        :rtype: List[str]
        """
        pass


class FileExplorer(TargetExplorer):
    """Explorer that finds file targets."""

    def find_modified(self, file: pyd.ModifiedFile) -> List[str]:
        """Find the paths of modified files.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: paths of modified files
        :rtype: List[str]
        """
        paths = set()
        for path in (file.new_path, file.old_path):
            if path is not None:
                paths.add(path)
        return list(paths)


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

    def find_modified(self, file: pyd.ModifiedFile) -> List[str]:
        """Find full names (with package) of modified java top level classes.
        Expects file content to be java source code.

        :param file: java source file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: names of all the classes that have been modified
        :rtype: List[str]
        """
        class_names = set()
        diff_parsed = file.diff_parsed
        if len(diff_parsed["added"]) > 0:
            class_names.update(
                self._find_affected_classes(diff_parsed["added"], file.content)
            )
        if len(diff_parsed["deleted"]) > 0:
            class_names.update(
                self._find_affected_classes(diff_parsed["deleted"], file.content_before)
            )

        return list(class_names)

    def _find_affected_classes(
        self, modified_lines: List[Tuple[int, str]], source: bytes
    ) -> Set[str]:
        names = set()
        classes = self.explore_source(source)
        for changed_line, _ in modified_lines:
            for class_name, class_start, class_end in classes:
                if class_start <= changed_line and changed_line <= class_end:
                    names.add(class_name)
        return names

    def explore_source(self, source: bytes) -> List[Tuple[str, int, int]]:
        """Find java top level classes in source code.

        :param source: java source code
        :type source: bytes
        :returns: List of (class_name, class_start_line, class_end_line) tuples
        :rtype: List[Tuple[str, int, int]]
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
                package = tree.text[s:e].decode() + "."
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
            classes[i][0] = package + classes[i][0]
            classes[i] = tuple(classes[i])
        return classes
