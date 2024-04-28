import re

from pydriller import Commit, Git

from mclocalizer.bug import Bug


def censor_comment(match: re.match):
    return re.sub(r".", "#", match.group(0))


java_class_pattern = re.compile(r"^[A-Za-z ]*class (?P<class_name>\w+)", re.MULTILINE)
java_censor_patterns = (
    re.compile(r"/\*.*\*/", re.DOTALL),
    re.compile(r"//.*$", re.MULTILINE),
)


fix_pattern = re.compile(r"(\bfix\b)|(\bfixed\b)|(\bfixes\b)", re.IGNORECASE)


def is_fixing(commit: Commit) -> list[Bug]:
    return re.search(fix_pattern, commit.msg) is not None


def find_bug_scope(repo: str) -> dict:
    gr = Git(repo)
    result = []

    commit_num = 0
    for commit in gr.get_list_commits():
        if is_fixing(commit):
            commit_num += 1
            print(commit_num)
            buggy_commits = gr.get_commits_last_modified_lines(commit)

            modified_files = commit.modified_files
            bug_scope = []
            for mfile in modified_files:
                if mfile.filename.endswith(".java"):
                    bug_scope.append(mfile.filename[:-5])
            # Pretend this is not here
            #    classes = {}
            #    contents = mfile.source_code
            #    for p in java_censor_patterns:
            #        contents = re.sub(p, censor_comment, contents)
            #    contents = contents.splitlines()
            #    i = 0
            #    for line in contents:
            #        i += 1
            #        class_match = re.search(java_class_pattern, line)
            #        if class_match is not None:
            #            classes[i] = class_match.group(1)
            #    for _, changes in mfile.diff_parsed.items():
            #        for index, _ in changes:
            #            pass

            result.append(Bug(commit.hash, list(buggy_commits.items()), bug_scope))

    return result
