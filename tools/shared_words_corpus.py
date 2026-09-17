import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


def extract_words(text: str) -> Set[str]:
    """
    Extract normalized words from text.

    This works with Spanish words, including accents such as á, é, í, ó, ú, ü, and ñ.
    It lowercases the text and keeps alphabetic words.
    """
    # Python's re module handles Unicode letters with \w.
    # This pattern extracts word-like tokens while excluding standalone underscores.
    tokens = re.findall(r"\b[^\W\d_]+\b", text.lower(), flags=re.UNICODE)
    return {token for token in tokens if token}


def collect_transcript_files(inputs: Iterable[Path], recursive: bool = False) -> List[Path]:
    """
    Collect transcript .txt files from file paths and/or folders.
    """
    transcript_files = []

    for input_path in inputs:
        if input_path.is_file():
            transcript_files.append(input_path)

        elif input_path.is_dir():
            pattern = "**/*.txt" if recursive else "*.txt"
            transcript_files.extend(sorted(input_path.glob(pattern)))

        else:
            raise FileNotFoundError(f"Input not found: {input_path}")

    # Remove duplicates while preserving order.
    unique_files = []
    seen = set()

    for file_path in transcript_files:
        resolved = file_path.resolve()
        if resolved not in seen:
            unique_files.append(file_path)
            seen.add(resolved)

    return unique_files


def read_words_from_files(transcript_files: Iterable[Path]) -> Tuple[Dict[Path, Set[str]], List[Path]]:
    """
    Read transcript files and return:
    - a dictionary mapping each file to its unique word set
    - a list of files that had zero readable words
    """
    words_by_file = {}
    empty_files = []

    for path in transcript_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        words = extract_words(text)
        words_by_file[path] = words

        if not words:
            empty_files.append(path)

    return words_by_file, empty_files


def compute_document_frequencies(words_by_file: Dict[Path, Set[str]]) -> Counter:
    """
    Count in how many transcript files each word appears.
    """
    frequencies = Counter()

    for words in words_by_file.values():
        frequencies.update(words)

    return frequencies


def select_shared_words(
    document_frequencies: Counter,
    total_files: int,
    min_files: Optional[int] = None,
    min_percent: Optional[float] = None,
) -> List[Tuple[str, int]]:
    """
    Select words that meet the requested sharing threshold.

    Default behavior:
    - if no threshold is provided, the word must appear in all files.
    """
    if min_percent is not None:
        required_files = max(1, round(total_files * (min_percent / 100)))
    elif min_files is not None:
        required_files = min_files
    else:
        required_files = total_files

    selected = [
        (word, count)
        for word, count in document_frequencies.items()
        if count >= required_files
    ]

    return sorted(selected, key=lambda item: (-item[1], item[0]))


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a corpus of words shared across transcript files. "
            "By default, words must appear in every transcript."
        )
    )

    parser.add_argument(
        "inputs",
        metavar="INPUT",
        type=Path,
        nargs="+",
        help=(
            "Transcript files or folders containing .txt transcripts. "
            "If a folder is given, all .txt files inside it will be used."
        ),
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for .txt files inside subfolders too.",
    )

    parser.add_argument(
        "--min-files",
        type=int,
        default=None,
        help=(
            "Include words that appear in at least this many transcript files. "
            "Example: --min-files 80"
        ),
    )

    parser.add_argument(
        "--min-percent",
        type=float,
        default=None,
        help=(
            "Include words that appear in at least this percentage of transcript files. "
            "Example: --min-percent 80"
        ),
    )

    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="If strict overlap returns zero words, show the top N most widely shared words.",
    )

    args = parser.parse_args(args=argv)

    try:
        transcript_files = collect_transcript_files(args.inputs, recursive=args.recursive)

        if len(transcript_files) < 2:
            raise ValueError(
                "At least two transcript .txt files are required to compute shared words."
            )

        words_by_file, empty_files = read_words_from_files(transcript_files)
        document_frequencies = compute_document_frequencies(words_by_file)

        selected_words = select_shared_words(
            document_frequencies,
            total_files=len(transcript_files),
            min_files=args.min_files,
            min_percent=args.min_percent,
        )

    except Exception as error:
        parser.error(str(error))
        return

    print(f"Transcript files analyzed ({len(transcript_files)} total):")
    for file_path in transcript_files:
        print(f"- {file_path}")

    print()

    if empty_files:
        print("Warning: these files had zero readable words:")
        for file_path in empty_files:
            print(f"- {file_path}")
        print()

    if args.min_percent is not None:
        threshold_description = f"at least {args.min_percent}% of files"
    elif args.min_files is not None:
        threshold_description = f"at least {args.min_files} files"
    else:
        threshold_description = "all files"

    print(f"Shared words threshold: {threshold_description}")
    print(f"Shared words found ({len(selected_words)} total):")

    for word, count in selected_words:
        print(f"{word}\t{count}/{len(transcript_files)}")

    if not selected_words:
        print()
        print("No words met the current threshold.")
        print(
            "This usually means no single word appears in every transcript, "
            "which is common when analyzing many files."
        )
        print()
        print(f"Top {args.top} words by number of transcript files they appear in:")

        for word, count in document_frequencies.most_common(args.top):
            print(f"{word}\t{count}/{len(transcript_files)}")


if __name__ == "__main__":
    main()
