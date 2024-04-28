import argparse
import csv

from tqdm import tqdm

from mclocalizer.find_bug_scope import find_bug_scope


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mclocalizer",
        description="Tool for finding problematic classes in software repositories.",
    )
    parser.add_argument("repo", type=str, help="path to git repository.")

    args = parser.parse_args()
    bugs = find_bug_scope(args.repo)
    result_path = "result.csv"
    with open(result_path, "w", newline="") as result:
        writer = csv.writer(result)
        writer.writerow(["Fix commit hash", "Bug Introducing commits", "Bug scope"])
        for bug in bugs:
            writer.writerow([bug.fixing_commit, bug.introducing_commits, bug.scope])
    return 0
