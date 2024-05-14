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
usage: mclocalizer [-h] -o OUT [-f] [-t {file,java_class,java_file}] 
[--include-test-dirs] [--blame] [--oldest-blame] repo

Tool for detecting what is notoriously broken in software repository.
Process fixing commits and identify modified targets.
Generate report and target statistics in csv format.

positional arguments:
  repo                  path to git repository.

options:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     output report file.
  -f, --force           overrides existing output files.
  -t {file,java_class,java_file}, --target {file,java_class,java_file}
                        the subject of mclocalizer investigation.
  --include-test-dirs   force mclocalizer to include changes made in test directories.
  --blame               add list of blame commits to the report.
  --oldest-blame        add oldest blame commit to the report.
```

## Examples
For all examples below mclocalizer will generate `out.csv` and `out_stat.csv` in current working directory with the collected data.
### Finding problematic java classes

For each fixing commit McLocalizer will identify changed java classes.

```sh
mclocalizer path_to_repository -t java_class -f -o out.csv
```

### Finding problematic java classes with blame info

For each fixing commit McLocalizer will identify changed java classes and run SZZ algorithm to find bug introducing commit.

```sh
mclocalizer path_to_repository -t java_class --blame -f -o out.csv
```
