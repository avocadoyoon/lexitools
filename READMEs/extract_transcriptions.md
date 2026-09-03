# extract_transcriptions.py

Pulls the `transcripcion` column out of a folder of delimited files and writes each file's transcriptions to a plain-text file, one per line. Use it to turn exported spreadsheets into the clean `.txt` transcripts that `whosaidwhich.py` expects.

Python 3.6+, standard library only.

## Usage

```bash
python extract_transcriptions.py
```

```python
SOURCE_DIR       = "raw_data"                    # folder to scan
OUTPUT_DIR       = SOURCE_DIR                    # where results go
OUTPUT_SUFFIX    = "_transcription"              # appended before .txt
INPUT_EXTENSIONS = (".tsv", ".txt", ".csv")
COLUMN_NAME      = "transcripcion"
```

`SOURCE_DIR` is relative to where you run the script, so run it from the folder containing `raw_data/`.

For each input file `entrevista1.tsv` you get `entrevista1_transcription.txt` with the non-empty values from the transcription column, in row order:

```
Processing: entrevista1.tsv
  Header found at row 1, 'transcripcion' at column index 2
  → 2 transcription(s) written to entrevista1_transcription.txt
```

## What it handles

- **Tabs or commas**, detected per file from the first 4KB. Quoted fields and values containing line breaks parse correctly.
- **Accented and cased headers** — `Transcripción`, `TRANSCRIPCION` and `transcripcion_final` all match.
- **Headers below row 1**, so files with a title or blank rows on top still work.
- **Ragged rows**, by falling back to the nearest in-range column.
- **Missing columns** — prints a warning and writes nothing rather than leaving an empty file.
- **Re-runs**, since previously generated `_transcription.txt` files are skipped.

## Limitations

- Only the top level of `SOURCE_DIR` is scanned; no subfolders.
- Files are read as UTF-8 with unreadable bytes replaced, so a Latin-1 export will parse without error but with mangled accents.
- Only one column name at a time; change `COLUMN_NAME` to extract a different field.
