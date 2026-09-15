
# Word Processor

A simple Python script for processing text and counting word frequencies.

The script can either:
1. Accept text pasted directly into the terminal, or
2. Read text from a `.txt` file.

It then:
- Converts all text to lowercase
- Removes punctuation
- Splits the text into individual words
- Counts how many times each word occurs
- Identifies repeated words
- Creates a cleaned list of unique words
- Prints a word-frequency table

## Files

The project contains:

- `word_processor.py` - the main Python script
- `procomp.txt` - an example text file that can be used as input; it is located in `practice_files.` 

## Requirements

You only need:

- Python 3

The script uses Python's built-in `string` module, so no external packages need to be installed.

## How to Run

Open a terminal in the folder containing the script and run:

```bash
python word_processor.py

````

Depending on your system, you may need to use:

```bash
python3 word_processor.py
```

## Input Options

When you run the script, you will see:

```text
Type '1' to paste text or '2' to use a file:
```

### Option 1: Paste text

Type:

```text
1
```

Then paste your text when prompted:

```text
Paste your text here:
```

For example:

```text
This is a test. This is another test.
```

The script will process the text directly.

### Option 2: Use a text file

Type:

```text
2
```

You will then be asked:

```text
Enter file name (e.g., words.txt):
```

Enter the name of your `.txt` file.

For example:

```text
procomp.txt
```

Make sure the text file is in the same folder as `word_processor.py`, unless you provide a path to the file.

## Example

Using:

```text
procomp.txt
```

as the input file will produce three types of output.

### 1. Repeated Words

The script first prints the words that occur more than once:

```text
Repeated words:
['the', 'and', 'language', ...]
```

### 2. Cleaned List

It then prints a list containing each unique word:

```text
Cleaned list:
['the', 'language', 'is', 'important', ...]
```

### 3. Word Frequency Table

Finally, it prints each word together with the number of times it occurs:

```text
Word Frequency Table:
----------------------
Word            Count
the             12
language        8
and             7
...
```

## How the Processing Works

The script processes the text in several steps.

### 1. Convert text to lowercase

All text is converted to lowercase:

```python
text = text.lower()
```

This means that words such as:

```text
Language
language
LANGUAGE
```

are treated as the same word:

```text
language
```

### 2. Remove punctuation

Python's built-in `string.punctuation` is used to remove punctuation:

```python
text = text.translate(str.maketrans('', '', string.punctuation))
```

For example:

```text
"Hello, world!"
```

becomes:

```text
"Hello world"
```

### 3. Split the text into words

The text is split into individual words:

```python
words = text.split()
```

### 4. Count word frequencies

A dictionary is used to store each word and its frequency:

```python
word_counts = {}
```

Each time a word appears, its count is increased.

For example:

```text
the cat and the dog
```

produces:

```text
the: 2
cat: 1
and: 1
dog: 1
```

### 5. Find repeated words

Words with a frequency greater than 1 are added to the repeated-word list:

```python
if count > 1:
    repeated_words.append(word)
```

### 6. Create the cleaned list

The dictionary keys are used to create a list containing each unique word:

```python
unique_words = list(word_counts.keys())
```

## Important Notes

* The script is **case-insensitive** because all text is converted to lowercase.
* Standard punctuation is removed before the text is split into words.
* Words are separated using Python's `split()` method.
* The script does not modify the original `.txt` file.
* The results are printed in the terminal rather than saved to a new file.
* The word-frequency table follows the order in which words first appear in the input text.

## Limitations

This is a simple word-processing script and does not perform advanced linguistic processing.

For example, different forms of a word are treated as different words:

```text
run
runs
running
```

will be counted separately.

Similarly, the script does not perform:

* Lemmatization
* Stemming
* Part-of-speech tagging
* Stop-word removal
* Morphological analysis
* Language detection

These could be added in future versions if needed.

## Example Workflow

A typical workflow is:

```text
1. Put word_processor.py and procomp.txt in the same folder.
2. Open a terminal in that folder.
3. Run:
   
   python word_processor.py

4. Choose option 2.
5. Enter:
   
   procomp.txt

6. Review the repeated words, cleaned word list, and frequency table.
```

