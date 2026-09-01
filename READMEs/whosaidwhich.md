# whosaidwhich.py

A command-line tool for comparing a set of plain-text transcripts. It answers two questions:

1. **Which words appear across all (or most) of my transcripts?**
2. **Which transcripts contain a specific word or phrase?**

Word extraction is Unicode-aware and handles Spanish accents and `ñ` correctly (`á é í ó ú ü ñ`), so accented forms are kept intact rather than being split or stripped.

## Requirements

Python 3.8 or newer. No third-party dependencies — standard library only.

## Input

Transcripts must be UTF-8 `.txt` files. You can pass individual files, folders, or a mix of both. When you pass a folder, every `.txt` file directly inside it is used; add `--recursive` to include subfolders. At least two transcript files are required.

Unreadable bytes are replaced rather than raising an error, so a file with mixed encoding will still be processed (possibly with a few mangled characters).

## Usage

### Shared-word mode (default)

```bash
python whosaidwhich.py transcripts/
```

Prints every word that appears in **all** transcripts:

```
Transcript files analyzed (3 total):
- transcripts/a.txt
- transcripts/b.txt
- transcripts/c.txt

Shared words threshold: all files
Shared words found (1 total):
dijo	3/3
```

The number after each word is a **document frequency**: how many files the word appears in, not how many times it occurs. A word appearing 40 times in one file still counts as 1.

Requiring a word in *every* file rarely returns much once you have more than a handful of transcripts, so you'll usually want to loosen the threshold:

```bash
# words appearing in at least 80% of the files
python whosaidwhich.py transcripts/ --min-percent 80

# words appearing in at least 12 files
python whosaidwhich.py transcripts/ --min-files 12
```

If both are given, `--min-percent` wins. If no word meets the threshold, the script falls back to listing the most widely shared words instead, so you get something useful rather than an empty result:

```bash
python whosaidwhich.py transcripts/ --top 100
```

`--top` defaults to 50 and only takes effect when the threshold returns nothing.

### Search mode

Pass `--terms` (`-t`) or `--term-file` (`-T`) and the script switches to searching instead:

```bash
python whosaidwhich.py transcripts/ -t dijo coche "niña está"
```

```
Search term results:
term                 count files
----                 ----- -----
dijo                     3 a, b, c
coche                    1 c
niña está                2 a, b
```

The `files` column lists filenames without their extension.

Single-word terms are matched against the file's word set, so `dijo` will not match inside `dijole`. Multi-word terms are matched against the raw text with flexible separators, so `"niña está"` also matches `niña, está` and `niña  está` across a line break. Matching is case-insensitive in both modes.

Terms that matched nothing are listed separately at the end of the run.

#### Term files

For anything more than a few terms, keep them in a file — one per line. Blank lines and lines beginning with `#` are ignored:

```
# terms.txt
dijo
niña está
coche azul
```

```bash
python whosaidwhich.py transcripts/ -T terms.txt
# or inline, with the @ prefix:
python whosaidwhich.py transcripts/ -t @terms.txt otro_término
```

You can pass several term files, and mix `-t`, `@file`, and `-T` freely — everything is merged into one list.

### Writing results to a file

```bash
python whosaidwhich.py transcripts/ -T terms.txt -o results.csv
```

A `.csv` extension produces CSV; anything else (`.txt`, `.tsv`) produces tab-separated output. Parent folders are created automatically.

`--append` adds to an existing file instead of overwriting it, with a section header separating each table. This is how you build one comparison file out of several runs:

```bash
python whosaidwhich.py entrevistas/ -T terms.txt -o results.csv
python whosaidwhich.py declaraciones/ -T terms.txt -o results.csv --append
python whosaidwhich.py llamadas/ -T terms.txt -o results.csv --append -s "llamadas telefónicas"
```

Section names default to the input folder name, or the first term file's name if you passed several inputs. Use `--section` (`-s`) to set one explicitly. Note that `--append` only appends when the target file already exists; otherwise it writes a fresh file with no section header.

## Options

| Option | Description |
| --- | --- |
| `INPUT...` | One or more transcript files or folders (required) |
| `--recursive` | Also search subfolders for `.txt` files |
| `--min-files N` | Keep words appearing in at least N files |
| `--min-percent P` | Keep words appearing in at least P% of files (takes precedence over `--min-files`) |
| `--top N` | Fallback list size when the threshold returns nothing (default 50) |
| `--terms`, `-t` | Words or phrases to search for; `@file` reads a term file |
| `--term-file`, `-T` | One or more files of search terms, one per line |
| `--output`, `-o` | Write search results to a `.csv` or `.tsv`/`.txt` file |
| `--append` | Append to `--output` instead of overwriting |
| `--section`, `-s` | Section label used when appending |

## Notes and limitations

- Search mode and shared-word mode are mutually exclusive. If any search term is given, the script reports the search results and exits without computing shared words.
- Digits and numbers are ignored entirely; only alphabetic tokens are counted.
- No stemming or lemmatization is applied. `dijo`, `dije`, and `decir` are three different words.
- Files with zero readable words are reported as a warning in shared-word mode, but pass silently in search mode.
- The whole corpus is held in memory. Fine for hundreds of interview transcripts, not intended for gigabyte-scale corpora.
