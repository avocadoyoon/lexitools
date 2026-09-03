import os
import csv

# ── Configuration ────────────────────────────────────────────────────────────
SOURCE_DIR = "raw_data"
OUTPUT_DIR = SOURCE_DIR          # output files go to the same folder
OUTPUT_SUFFIX = "_transcription" # appended before .txt  →  filename_transcription.txt
# ─────────────────────────────────────────────────────────────────────────────

COLUMN_NAME = "transcripcion"
MAX_SHIFT   = 2   # how many columns left/right to search if the header isn't exact


def find_column_index(header_row, target, max_shift):
    """Return the index of *target* in header_row, or None if not found."""
    # Normalise: strip whitespace, lower-case
    normalised = [h.strip().lower() for h in header_row]
    target_norm = target.strip().lower()

    # Exact match first
    if target_norm in normalised:
        return normalised.index(target_norm)

    # Sliding-window search within max_shift of any candidate
    for i, h in enumerate(normalised):
        if h == target_norm:
            return i

    # Partial / shifted match: look for the target anywhere near a header that
    # contains the same root letters
    for i, h in enumerate(normalised):
        if target_norm in h or h in target_norm:
            return i

    return None


def extract_from_file(filepath):
    """Parse one TSV file and return all non-empty transcription values."""
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
                col_idx = find_column_index(row, COLUMN_NAME, MAX_SHIFT)
                if col_idx is not None:
                    print(f"  Header found at row {row_num + 1}, "
                          f"'{COLUMN_NAME}' at column index {col_idx}")
                continue  # skip the header row itself

            # Safety: skip if this row is too short
            if col_idx >= len(row):
                # Try shifting right up to MAX_SHIFT
                found = False
                for shift in range(1, MAX_SHIFT + 1):
                    alt = col_idx + shift
                    if alt < len(row) and row[alt].strip():
                        transcriptions.append(row[alt].strip())
                        found = True
                        break
                if not found:
                    continue
            else:
                value = row[col_idx].strip()
                if value:
                    transcriptions.append(value)

    if col_idx is None:
        print(f"  WARNING: '{COLUMN_NAME}' column not found in {filepath}")

    return transcriptions


def main():
    txt_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".tsv")]

    if not txt_files:
        print(f"No .txt files found in:\n  {SOURCE_DIR}")
        return

    print(f"Found {len(txt_files)} .txt file(s) in:\n  {SOURCE_DIR}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in sorted(txt_files):
        src_path = os.path.join(SOURCE_DIR, filename)
        stem     = os.path.splitext(filename)[0]

        # Skip files that are already output files
        if stem.endswith(OUTPUT_SUFFIX):
            continue

        out_name = f"{stem}{OUTPUT_SUFFIX}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        print(f"Processing: {filename}")
        transcriptions = extract_from_file(src_path)

        with open(out_path, "w", encoding="utf-8") as fh:
            for line in transcriptions:
                fh.write(line + "\n")

        print(f"  → {len(transcriptions)} transcription(s) written to {out_name}\n")

    print("Done.")


if __name__ == "__main__":
    main()
