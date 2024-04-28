import abc
from typing import List, Set, Tuple

import pydriller as pyd
import tree_sitter as ts
import tree_sitter_java as tsjava


class ChangeExplorer(abc.ABC):
    """Abstract class for finding scope of the changes made by the commit."""

    @abc.abstractmethod
    def find_scope(self, file: pyd.ModifiedFile) -> List[str]:
        """Find what constructs were affected by the changes.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: list of identifiers that have been affected by the change
        :rtype: List[str]
        """
        pass


class ChangedFileExplorer(ChangeExplorer):
    """Explorer that finds what files have been modified by the commit"""

    def find_scope(self, file: pyd.ModifiedFile) -> List[str]:
        """Find the filename of modified file.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: filename of modified file
        :rtype: List[str]
        """
        return [file.filename]


class ChangedJavaClassExplorer(ChangeExplorer):
    """Explorer that finds what java classes have been modified by the commit"""

    _java_lang = ts.Language(tsjava.language(), "java")
    _query = _java_lang.query(
        "(class_declaration name: (identifier) @name) @definition.class"
    )

    def __init__(self):
        self._parser = ts.Parser()
        self._parser.set_language(ChangedJavaClassExplorer._java_lang)

    def find_scope(self, file: pyd.ModifiedFile) -> List[str]:
        """Find the names of affected classes in modified file.

        :param file: file that has been modified by the commit
        :type file: pyd.ModifiedFile
        :returns: name of all the classes that have been modified
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

        return List(class_names)

    def _find_affected_classes(
        self, modified_lines: List[Tuple[int, str]], source: bytes
    ) -> Set[str]:
        names = set()
        classes = self._find_classes(source)
        for changed_line, _ in modified_lines:
            for class_name, class_start, class_end in classes:
                if class_start <= changed_line and changed_line <= class_end:
                    names.add(class_name)
        return names

    def _find_classes(self, source: bytes) -> List[Tuple[str, int, int]]:
        classes = list()
        tree = self._parser.parse(source)
        matches = ChangedJavaClassExplorer._query.matches(tree.root_node)
        for match in matches:
            # check if match first sexp in _query
            if match[0] == 0:
                captured = match[1]
                s = captured["name"].range.start_byte
                e = captured["name"].range.end_byte
                classes.append(
                    (
                        tree.text[s:e].decode(),
                        captured["definition.class"].start_point[0],
                        captured["definition.class"].end_point[0],
                    )
                )
        return classes
