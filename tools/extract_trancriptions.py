import os
import csv
import unicodedata 

# ── Configuration ────────────────────────────────────────────────────────────
SOURCE_DIR = "raw_data"
OUTPUT_DIR = SOURCE_DIR          # output files go to the same folder
OUTPUT_SUFFIX = "_transcription" # appended before .txt  →  filename_transcription.txt
INPUT_EXTENSIONS = (".tsv", ".csv" , ".txt")
# ─────────────────────────────────────────────────────────────────────────────

COLUMN_NAME = "transcripcion"
MAX_SHIFT   = 2   # how many columns left/right to search if the header isn't exact


def normalise(text):
    """Lower-case, strip whitespace, and remove accents.
 
    'Transcripción' and 'transcripcion' both become 'transcripcion'.
    """
    text = text.strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))
 
def find_column_index(header_row, target):
    """Return the index of *target* in header_row, or None if not found."""
    normalised = [normalise(h) for h in header_row]
    target_norm = normalise(target)
 
    # Exact match first.
    if target_norm in normalised:
        return normalised.index(target_norm)
 
    # Then a header that contains the target, e.g. 'transcripcion_final'.
    # Note the direction: the header must contain the target, never the
    # reverse, otherwise a one-letter cell like 'a' would match.
    for i, h in enumerate(normalised):
        if target_norm in h:
            return i
 
    return None
 
 
def extract_from_file(filepath):
    """Parse one delimited file.
 
    Returns a list of non-empty transcription values, or None if the column
    was never found.
    """
    transcriptions = []
 
    with open(filepath, encoding="utf-8", errors="replace") as fh:
        # Detect delimiter: try tab first, fall back to comma
        sample = fh.read(4096)
        fh.seek(0)
        delimiter = "\t" if "\t" in sample else ","
 
        reader = csv.reader(fh, delimiter=delimiter)
        col_idx = None
 
        for row_num, row in enumerate(reader):
            if not row:
                continue
 
            if col_idx is None:
                # Find header row (first row that contains our column name)
                col_idx = find_column_index(row, COLUMN_NAME)
                if col_idx is not None:
                    print(f"  Header found at row {row_num + 1}, "
                          f"'{COLUMN_NAME}' at column index {col_idx}")
                continue  # skip the header row itself
 
            if col_idx < len(row):
                value = row[col_idx].strip()
                if value:
                    transcriptions.append(value)
                continue
 
            for shift in range(1, MAX_SHIFT + 1):
                alt = col_idx - shift
                if 0 <= alt < len(row) and row[alt].strip():
                    transcriptions.append(row[alt].strip())
                    break
 
    if col_idx is None:
        print(f"  WARNING: '{COLUMN_NAME}' column not found in {filepath}")
        return None
 
    return transcriptions
 
 
def main():
    input_files = [
        f for f in os.listdir(SOURCE_DIR)
        if f.lower().endswith(INPUT_EXTENSIONS)
        and not os.path.splitext(f)[0].endswith(OUTPUT_SUFFIX)
    ]
 
    if not input_files:
        extensions = "/".join(INPUT_EXTENSIONS)
        print(f"No {extensions} files found in:\n  {SOURCE_DIR}")
        return
 
    print(f"Found {len(input_files)} file(s) in:\n  {SOURCE_DIR}\n")
 
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    for filename in sorted(input_files):
        src_path = os.path.join(SOURCE_DIR, filename)
        stem     = os.path.splitext(filename)[0]
 
        out_name = f"{stem}{OUTPUT_SUFFIX}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)
 
        print(f"Processing: {filename}")
        transcriptions = extract_from_file(src_path)
 
        if transcriptions is None:
            print("  → skipped, no file written\n")
            continue
 
        if not transcriptions:
            print("  → column found but empty, no file written\n")
            continue
 
        with open(out_path, "w", encoding="utf-8") as fh:
            for line in transcriptions:
                fh.write(line + "\n")
 
        print(f"  → {len(transcriptions)} transcription(s) written to {out_name}\n")
 
    print("Done.")
 
 
if __name__ == "__main__":
    main()
 
