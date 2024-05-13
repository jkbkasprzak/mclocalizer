# McLocalizer

Tool for detecting what is notoriously broken in software repository.

## Install
Clone the repository:

```sh
git clone https://github.com/jkbkasprzak/mclocalizer.git
```

Install mclocalizer and its dependencies using pip

```sh
cd mclocalizer
pip install .
```

## Usage

For detailed information check the help message.

```
usage: mclocalizer [-h] [-t --target {file,java_class,java_file}]
[--all-commits] [--include-test-dirs] repo

Tool for detecting what is notoriously broken in software repository.
Process fixing commits and identify the changes.

positional arguments:
  repo                  path to git repository.

options:
  -h, --help            show this help message and exit
  -t --target {file,java_class,java_file}
                        the subject of mclocalizer investigation.
  --include-test-dirs   force mclocalizer to include changes made in test directories.
```

## Examples
### Finding problematic java classes

Run mclocalizer with target set to `java_class` and provide path to repository for analysis.

```sh
mclocalizer -t java_class path_to_repository
```

mclocalizer will generate `result.csv` and `summary.csv` in current working directory with the collected data.
