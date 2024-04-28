# McLocalizer

Tool for finding problematic classes in software repositories.

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

Run mclocalizer and provide path to repository for analysis.

```sh
mclocalizer path_to_repository
```

mclocalizer will generate `result.csv` in cwd with the collected data.
