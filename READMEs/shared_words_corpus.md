
# Shared Words Corpus

A Python script for identifying words that are shared across multiple transcript `.txt` files.

The script treats each transcript as a separate document and determines how many transcript files contain each word. This makes it possible to create a corpus of words that occur across a specified proportion of the transcripts.

By default, a word must appear in **every transcript file** to be included.

## Files

The project contains:

- `shared_words_corpus.py` - the main Python script
- `.txt` transcript files - the text files used as input

## Requirements

You only need:

- Python 3

The script uses Python's standard library, so no external packages need to be installed.

## What the Script Does

The script follows these main steps:

1. Finds the transcript `.txt` files.
2. Reads each transcript.
3. Converts words to lowercase.
4. Extracts alphabetic words, including Spanish characters such as `á`, `é`, `í`, `ó`, `ú`, `ü`, and `ñ`.
5. Creates a unique set of words for each transcript.
6. Counts how many transcript files contain each word.
7. Selects words according to a specified sharing threshold.
8. Prints the shared words and the number of transcript files in which each word occurs.

The word extraction keeps alphabetic words and excludes numbers and standalone underscores. :contentReference[oaicite:1]{index=1}

## Basic Usage

Run the script from the terminal:

```bash
python shared_words_corpus.py
## Basic Usage
````

Run the script from the terminal:

```bash
python shared_words_corpus.py
````

or, depending on your system:

```bash
python3 shared_words_corpus.py
```

You must provide at least one input file or folder.

For example:

```bash
python shared_words_corpus.py transcripts/
```

If you provide a folder, the script uses the `.txt` files directly inside that folder. 

## Using Individual Files

You can also provide individual transcript files:

```bash
python shared_words_corpus.py transcript1.txt transcript2.txt transcript3.txt
```

At least **two transcript files** are required for calculating shared words. 

## Using a Folder

If your transcripts are all stored in one folder:

```bash
python shared_words_corpus.py transcripts/
```

The script will automatically find the `.txt` files in that folder.

### Including Subfolders

By default, only `.txt` files directly inside the specified folder are included.

To also search through subfolders, use:

```bash
python shared_words_corpus.py transcripts/ --recursive
```

The `--recursive` option searches for `.txt` files inside subfolders as well. 

## Default Threshold

By default, a word must occur in **all transcript files**.

For example, if 425 transcript files are analyzed, a word must appear in all 425 files:

```text
Shared words threshold: all files
Shared words found (15 total):
y       422/425
la      409/425
...
```

The script therefore treats "shared" as a document-level measure: a word only needs to occur once in a transcript to count as present in that transcript.

It does **not** count the total number of times the word occurs within each transcript.

## Setting a Minimum Number of Files

You can specify the minimum number of transcript files in which a word must appear.

For example:

```bash
python shared_words_corpus.py transcripts/ --min-files 80
```

This means that a word is included if it appears in **at least 80 transcript files**.

The option is:

```bash
--min-files N
```

For example:

```bash
--min-files 50
```

includes words appearing in at least 50 transcript files. 

## Setting a Percentage Threshold

Instead of specifying a fixed number of files, you can specify a percentage.

For example:

```bash
python shared_words_corpus.py transcripts/ --min-percent 80
```

This selects words that occur in at least **80% of the transcript files**.

The option is:

```bash
--min-percent N
```

For example:

```bash
--min-percent 50
```

selects words appearing in at least 50% of the transcript files. 

### Example

If the corpus contains 100 transcript files:

```bash
python shared_words_corpus.py transcripts/ --min-percent 80
```

will select words appearing in at least 80 transcript files.

The percentage threshold is converted into a required number of files by the script. 

## Combining Options

The options can be combined.

For example:

```bash
python shared_words_corpus.py transcripts/ --recursive --min-percent 50
```

This will:

* Search the folder and its subfolders
* Read all `.txt` transcript files
* Select words appearing in at least 50% of the transcripts

You can also use a fixed number of files:

```bash
python shared_words_corpus.py transcripts/ --recursive --min-files 100
```

## Output

The script first reports which transcript files were analyzed:

```text
Transcript files analyzed (425 total):
- transcripts/file1.txt
- transcripts/file2.txt
- transcripts/file3.txt
...
```

It then displays the selected sharing threshold:

```text
Shared words threshold: at least 50.0% of files
```

Finally, it lists the shared words and the number of transcript files containing each word:

```text
Shared words found (15 total):
y       422/425
la      409/425
el      383/425
de      380/425
que     357/425
```

The format is:

```text
WORD    NUMBER_OF_FILES/NUMBER_OF_TOTAL_FILES
```

For example:

```text
y       422/425
```

means that the word `y` appears in 422 out of 425 transcript files.

## Empty Files

If a transcript contains no readable words, the script reports it as a warning:

```text
Warning: these files had zero readable words:
- transcripts/empty_file.txt
```

The script continues processing the other files. 

## What Counts as a Word?

The script:

* Converts text to lowercase
* Keeps alphabetic words
* Supports Unicode characters
* Supports Spanish accented characters
* Removes numbers from word tokens
* Excludes standalone underscores

For example:

```text
Hola, HOLA, español, niño
```

is normalized to:

```text
hola
español
niño
```

Because the text is converted to lowercase, `Hola`, `hola`, and `HOLA` are treated as the same word. 

## Important: Document Frequency vs. Word Frequency

This script measures **document frequency**.

For each word, it asks:

> In how many transcript files does this word occur?

It does **not** ask:

> How many times does this word occur across the entire corpus?

For example, suppose there are three transcripts:

```text
Transcript 1: the the the cat
Transcript 2: the dog
Transcript 3: the bird
```

The word `the` occurs in:

```text
3/3 files
```

Therefore, its document frequency is 3.

The fact that it occurs three times in Transcript 1 does not increase its document frequency.

This is implemented by first creating a unique set of words for each file and then counting those sets across the files.  

## Sorting

Shared words are sorted by:

1. Number of transcript files containing the word, from highest to lowest
2. Alphabetically when two words have the same count

For example:

```text
the     425/425
and     423/425
language 410/425
...
```

This makes the most widely shared words appear first. 

## When No Words Meet the Threshold

If no words meet the selected threshold, the script prints:

```text
No words met the current threshold.
```

It then displays the most widely shared words as an alternative overview.

For example:

```text
Top 50 words by number of transcript files they appear in:
y       422/425
la      409/425
el      383/425
...
```

This is particularly useful when the threshold is set to require a word to occur in every transcript, but no word actually meets that requirement. 

## Controlling the Fallback List

The default fallback list contains the top 50 most widely shared words.

You can change this using:

```bash
--top N
```

For example:

```bash
python shared_words_corpus.py transcripts/ --top 20
```

will display the top 20 most widely shared words if the selected threshold returns no words. 

## Example Workflows

### Analyze all transcripts in a folder

```bash
python shared_words_corpus.py transcripts/
```

### Analyze transcripts recursively

```bash
python shared_words_corpus.py transcripts/ --recursive
```

### Find words shared by at least 50% of transcripts

```bash
python shared_words_corpus.py transcripts/ --min-percent 50
```

### Find words shared by at least 100 transcripts

```bash
python shared_words_corpus.py transcripts/ --min-files 100
```

### Find words shared by at least 80% of transcripts, including subfolders

```bash
python shared_words_corpus.py transcripts/ --recursive --min-percent 80
```

### Show the top 20 words if no words meet the threshold

```bash
python shared_words_corpus.py transcripts/ --top 20
```

## Command-Line Options

| Option            | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| `INPUT`           | Transcript `.txt` files or folders                                   |
| `--recursive`     | Search for `.txt` files inside subfolders                            |
| `--min-files N`   | Include words appearing in at least N transcript files               |
| `--min-percent N` | Include words appearing in at least N% of transcript files           |
| `--top N`         | Number of widely shared words to show if no words meet the threshold |

## Limitations

This script performs relatively simple word-level processing.

It does not perform:

* Lemmatization
* Stemming
* Part-of-speech tagging
* Stop-word removal
* Morphological analysis
* Syntactic analysis
* Language detection
* Frequency counting within individual transcripts

Different word forms are therefore treated as different words.

For example:

```text
hablar
hablando
habló
```

are treated as three separate words.

## Summary

The main purpose of this script is to identify **words that are shared across a collection of transcript files**.

The key distinction is:

```text
Word frequency
    = How many times does a word occur?

Document frequency
    = How many transcript files contain the word?
```

This script uses **document frequency** to determine how widely a word is shared across the transcript corpus.
