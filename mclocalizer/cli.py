import argparse
import csv

from tqdm import tqdm

from mclocalizer.change_explorer import ChangedFileExplorer, ChangedJavaClassExplorer
from mclocalizer.commit_filter import FixKeywordCommitFilter
from mclocalizer.file_filter import JavaFileFilter, NoTestDirFileFilter
from mclocalizer.mclocalizer import McLocalizer


def main() -> int:
    targets = dict()
    targets["file"] = ([], ChangedFileExplorer())
    targets["java_class"] = ([JavaFileFilter()], ChangedJavaClassExplorer())
    targets["java_file"] = ([JavaFileFilter()], ChangedFileExplorer())

    parser = argparse.ArgumentParser(
        prog="mclocalizer",
        description="""
        Tool for detecting what is notoriously broken in software repository.
        Process fixing commits and identify the changes.
        """,
    )
    parser.add_argument("repo", type=str, help="path to git repository.")
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        choices=list(targets.keys()),
        help="the subject of mclocalizer investigation.",
        default="file",
    )
    parser.add_argument(
        "--all-commits",
        action="store_true",
        help="force mclocalizer to process all commits in the repository.",
    )
    parser.add_argument(
        "--include-test-dirs",
        action="store_true",
        help="force mclocalizer to include changes made in test directories.",
    )
    args = parser.parse_args()
    file_filters, explorer = targets[args.target]
    if not args.include_test_dirs:
        file_filters.append(NoTestDirFileFilter())
    commit_filters = []
    if not args.all_commits:
        commit_filters.append(FixKeywordCommitFilter())

    localizer = McLocalizer(args.repo, commit_filters, file_filters, explorer)
    result_path = "result.csv"
    with open(result_path, "w", newline="") as result:
        writer = csv.writer(result, delimiter=",")
        writer.writerow(["Commit hash", "Changed targets"])
        with tqdm(
            total=localizer.total_commits(),
            dynamic_ncols=True,
            desc="Processing commits",
            unit="commits",
            bar_format="{desc}: {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt} [{rate_fmt}{postfix}]",
        ) as pbar:
            for report in localizer.gen_reports():
                if report.kind == report.Kind.COMPLETE:
                    writer.writerow([report.commit.hash, "; ".join(report.changes)])
                pbar.update(1)
    return 0
