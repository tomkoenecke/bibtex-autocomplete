# Bibtex Autocomplete

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://github.com/dlesbre/bibtex-autocomplete/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/bibtexautocomplete.svg)](https://pypi.python.org/pypi/bibtexautocomplete/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/bibtexautocomplete.svg)](https://pypi.python.org/pypi/bibtexautocomplete/)
[![License](https://img.shields.io/pypi/l/bibtexautocomplete.svg)](https://github.com/dlesbre/bibtex-autocomplete/blob/master/LICENSE)
[![PyPI status](https://img.shields.io/pypi/status/bibtexautocomplete.svg)](https://pypi.python.org/pypi/bibtexautocomplete/)
[![Downloads](https://pepy.tech/badge/bibtexautocomplete)](https://pepy.tech/project/bibtexautocomplete)
[![actions](https://img.shields.io/github/workflow/status/dlesbre/bibtex-autocomplete/Python%20application?label=tests)](https://github.com/dlesbre/bibtex-autocomplete/actions/workflows/python-app.yml)


**bibtexautocomplete** or **btac** is a python package to autocomplete bibtex bibliographies.
It is inspired and expanding on the solution provided by [thando](https://tex.stackexchange.com/users/182467/thando) in this [tex stackexchange post](https://tex.stackexchange.com/questions/6810/automatically-adding-doi-fields-to-a-hand-made-bibliography).

It attempts to complete a bibtex file by querying the following domains:
- [www.crossref.org](https://www.crossref.org/)
- [arxiv.org](https://arxiv.org/)
- [dlbp.org](https://dlbp.org)
- [researchr.org](https://researchr.org/)
- [unpaywall.org](https://unpaywall.org/)

Big thanks to all of them for allowing open, easy and well-documented access to their databases.

## Demo

![demo.svg](https://raw.githubusercontent.com/dlesbre/bibtex-autocomplete/master/imgs/demo.svg)

## Quick overview

**How does it find matches?**

`btac` queries the websites using the entry doi if known otherwise the title. So entries that don't have one of those two fields *will not* be completed. Additionally, the title should be the full title (title are compared excluding case and punctuation, but missing words are a mismatch).

**Disclaimers**

- There is no guarantee that the script will find matches for your entries, or that the websites will have any data to add to your entries, (or even that the website data is correct, but that's not for me to say...)

- The script is designed to minimize the chance of false positives - that is adding data from another similar-ish entry to your entry. If you find any such false positive please report them using the [issue tracker](https://github.com/dlesbre/bibtex-autocomplete/issues).

**How are entries completed?**

Once responses from all websites have been found, the script will add fields from website with the following priority : crossref > arxiv > dblp > researchr > unpaywall.

So if both crossref's and dblp's response contain a publisher, the one from crossref will be used.

The script will not overwrite any user given non-empty fields, unless the `-f/--force-overwrite` flag is given.

## Installation

Can be installed with [pip](https://pypi.org/project/pip/) :

```
pip install bibtexautocomplete
```

You should now be able to run the script using either command:

```
btac --version
python3 -m bibtexautocomplete --version
```

### Dependencies

This package has two dependencies (automatically installed by pip) :

- [bibtexparser](https://bibtexparser.readthedocs.io/)
- [alive_progress](https://github.com/rsalmei/alive-progress) (>= 2.4.0) for the fancy progressbar

## Usage

The command line tool can be used as follows:
```
btac [-flags] <input_files>
```

**Examples :**

- `btac my/db.bib` : reads from `./my/db.bib`, writes to  `./my/db.btac.bib`
- `btac -i db.bib` : reads from `db.bib` and overwrites it (inplace flag)
- `btac db1.bib db2.bib -o out1.bib -o out2.bib` reads multiple files and write their outputs to `out1.bib` and `out2.bib` respectively


**Optional arguments:**

- `-o --output <file.bib>`

  Write output to given file. Can be used multiple times when also giving multiple inputs. Maps inputs to outputs in order in that case If there are extra inputs, use default name (`old_name.btac.bib`). Ignored in inplace (`-i`) mode.

- `-q --only-query <website>` or `-Q --dont-query <website>`

  Restrict which websites to query from. `<site>` must be one of: `crossref`, `dblp`, `researchr`, `unpaywall`. These arguments can be used multiple times, for example to only query crossref and dblp use `-q crossref -q dblp` or `-Q researchr -Q unpaywall`

- `-e --only-entry <id>` or `-E --exclude-entry <id>`

  Restrict which entries should be autocomplete. `<id>` is the entry id used in your bibtex file (e.g. `@inproceedings{<id> ... }`). These arguments can also be used multiple times to select only/exclude multiple entries

- `-c --only-complete <field>` or `-C --dont-complete <field>`

  Restrict which fields you wish to autocomplete. Field is a bibtex field (e.g. `author`, `doi`,...). So if you only wish to add missing doi's used `-c doi`.

**Output formatting:**

- `--fa --align-values` pad fieldnames to align all values

  ```bibtex
  @article{Example,
    author = {Someone},
    doi    = {10.xxxx/yyyyy},
  }
  ```

- `--fc --comma-first` use comma first syntax

  ```bibtex
  @article{Example
    , author = {Someone}
    , doi = {10.xxxx/yyyyy}
    ,
  }
  ```

- `--fl --no-trailing-comma` don't add the last trailing comma
- `--fi --indent <space>` space used for indentation, default is a tab

**Flags:**
- `-i --inplace` Modify input files inplace, ignores any specified output files
- `-f --force-overwrite`  Overwrite already present fields. The default is to overwrite a field if it is empty or absent
- `-t --timeout <float>` set timeout on request in seconds, default: 10.0 s, increase this if you are getting a lot of timeouts.

- `-d --dump-data <file.json>` writes matching entries to the given JSON files.

  This allows to see duplicate fields from different sources that are otherwise overwritten when merged into a single entry.

  The JSON file will have the following formatting:

  ```json
  [
    {
      "entry": "<entry_id>",
      "new-fields": 8,
      "crossref": {
        "query-url": "https://api.crossref.org/...",
        "query-response-time": 0.556,
        "query-response-status": 200,
        "author" : "Lastname, Firstnames and Lastname, Firstnames ...",
        "title" : "super interesting article!",
        "..." : "..."
      },
      "arxiv": null, // null when no match found
      "dblp": ...,
      "researchr": ...,
      "unpaywall": ...
    },
    ...
  ]
  ```

- `-O --no-output` don't write any output files (except the one specified by `--dump-data`)

- `-v --verbose` verbose mode shows more info. It details entries as they are being processed and shows a summary of new fields and their source at the end. Using it more then once prints debug info (up to three times).
- `-s --silent` hide info and progressbar. Keep showing warnings and errors. Use twice to also hide warnings, thrice to also hide errors and four times to also hide critical error, effectively killing all output.
- `-n --no-color` don't color use ANSI codes to color and stylise output

- `--version` show version number
- `-h --help` show help
