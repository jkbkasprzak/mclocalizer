import argparse
import csv

from tqdm import tqdm

from mclocalizer.commit_filter import FixKeywordCommitFilter
from mclocalizer.explorer import FileExplorer, JavaClassExplorer
from mclocalizer.extension import BlameExtension
from mclocalizer.file_filter import JavaFileFilter, NoTestDirFileFilter
from mclocalizer.inspection import RepoInspector, TargetTracker


def main() -> int:
    targets = dict()
    targets["file"] = ([], FileExplorer())
    targets["java_class"] = ([JavaFileFilter()], JavaClassExplorer())
    targets["java_file"] = ([JavaFileFilter()], FileExplorer())

    parser = argparse.ArgumentParser(
        prog="mclocalizer",
        description="""
        Tool for detecting what is notoriously broken in software repository.
        Process fixing commits and identify modified targets.
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
        "--include-test-dirs",
        action="store_true",
        help="force mclocalizer to include changes made in test directories.",
    )
    parser.add_argument(
        "--blame",
        action="store_true",
        help=" add list of blame commits to the report.",
    )
    parser.add_argument(
        "--oldest-blame",
        action="store_true",
        help="add oldest blame commit to the report.",
    )

    args = parser.parse_args()
    file_filters, explorer = targets[args.target]
    if not args.include_test_dirs:
        file_filters.append(NoTestDirFileFilter())
    commit_filters = [FixKeywordCommitFilter()]

    blame_ext = BlameExtension(args.repo, file_filters, args.oldest_blame)
    add_blame = args.blame or args.oldest_blame

    localizer = RepoInspector(args.repo, commit_filters, file_filters, explorer)
    result_path = "result.csv"
    summary_path = "summary.csv"
    tracker = TargetTracker()
    with open(result_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        row = ["Commit hash", "Changed targets"]
        if add_blame:
            row.append("Blame")
        writer.writerow(row)
        with tqdm(
            total=localizer.total_commits(),
            dynamic_ncols=True,
            desc="Processing commits",
            unit="commits",
            bar_format="{desc}: {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt} [{rate_fmt}{postfix}]",
        ) as pbar:
            for report in localizer.gen_reports():
                if report.kind == report.Kind.COMPLETE:
                    tracker.collect(report)
                    row = [
                        report.commit.hash,
                        "; ".join(str(t) for t in report.targets),
                    ]
                    if add_blame:
                        row.append(blame_ext.process(report))
                    writer.writerow(row)
                pbar.update(1)
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["Target", "Commit count"])
        for name, count in tracker.gen_stats():
            writer.writerow([name, count])
    return 0
