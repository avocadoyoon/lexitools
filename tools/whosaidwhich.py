import argparse
import re
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


def extract_words(text: str) -> Set[str]:
    """
    Extract normalized words from text.

    This works with Spanish words, including accents such as á, é, í, ó, ú, ü, and ñ.
    It lowercases the text and keeps alphabetic words.
    """
  
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


def read_terms_from_file(term_file: Path) -> List[str]:
    """Read terms or phrases from a file, one per line."""
    text = term_file.read_text(encoding="utf-8", errors="replace")
    terms = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)

    return terms


def read_search_terms(term_args: Optional[Iterable[str]], term_files: Optional[Iterable[Path]]) -> List[str]:
    """Combine terms passed on the command line with terms read from files."""
    terms = []

    if term_args:
        for term in term_args:
            if term.startswith("@"):
                term_file = Path(term[1:])
                if not term_file.exists():
                    raise FileNotFoundError(f"Term file not found: {term_file}")
                terms.extend(read_terms_from_file(term_file))
            else:
                terms.append(term)

    if term_files:
        for term_file in term_files:
            if not term_file.exists():
                raise FileNotFoundError(f"Term file not found: {term_file}")
            terms.extend(read_terms_from_file(term_file))

    return [term for term in (term.strip() for term in terms) if term]


def read_transcripts(transcript_files: Iterable[Path]) -> Tuple[Dict[Path, Set[str]], Dict[Path, str], List[Path]]:
    """
    Read transcript files and return:
    - a dictionary mapping each file to its unique word set
    - a dictionary mapping each file to its raw text
    - a list of files that had zero readable words
    """
    words_by_file = {}
    text_by_file = {}
    empty_files = []

    for path in transcript_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        text_by_file[path] = text
        words = extract_words(text)
        words_by_file[path] = words

        if not words:
            empty_files.append(path)

    return words_by_file, text_by_file, empty_files


def term_matches(raw_text: str, words: Set[str], term: str) -> bool:
    """Match single-word terms by token membership and multi-word terms by text search."""
    normalized_term = term.strip().lower()
    if not normalized_term:
        return False

    term_tokens = extract_words(normalized_term)
    if len(term_tokens) <= 1:
        return bool(term_tokens and next(iter(term_tokens)) in words)

    normalized_text = raw_text.lower()
    pattern = r"\b" + r"\W+".join(re.escape(token) for token in term_tokens) + r"\b"
    return bool(re.search(pattern, normalized_text, flags=re.UNICODE))


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

    parser.add_argument(
        "--terms",
        "-t",
        nargs="+",
        help=(
            "Words or phrases to search for across the transcripts. "
            "Use quotes for multi-word terms, e.g. -t \"niña está\"."
        ),
    )

    parser.add_argument(
        "--term-file",
        "-T",
        type=Path,
        nargs="+",
        help=(
            "Read search terms from one or more files, one term per line. "
            "Blank lines and lines starting with # are ignored."
        ),
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help=(
            "Write search results to a file. Use .csv for CSV or .txt/.tsv for tab-separated."
        ),
    )

    parser.add_argument(
        "--append",
        action="store_true",
        help="Append results to `--output` instead of overwriting.",
    )

    parser.add_argument(
        "--section",
        "-s",
        type=str,
        default=None,
        help=(
            "Section name to write before the table when appending multiple tables into one file. "
            "Defaults to the first input folder or term-file stem."
        ),
    )

    args = parser.parse_args(args=argv)

    try:
        transcript_files = collect_transcript_files(args.inputs, recursive=args.recursive)

        if len(transcript_files) < 2:
            raise ValueError(
                "At least two transcript .txt files are required to compute shared words."
            )

        words_by_file, transcript_texts, empty_files = read_transcripts(transcript_files)
        document_frequencies = compute_document_frequencies(words_by_file)

        # If the user requested specific terms, report which files/folders contain them.
        if args.terms or args.term_file:
            search_terms = read_search_terms(args.terms, args.term_file)
            if not search_terms:
                raise ValueError("No valid search terms provided via --terms or --term-file")

            files_by_term = defaultdict(list)
            folders_by_term = defaultdict(set)

            for path, words in words_by_file.items():
                raw_text = transcript_texts[path]
                for term in search_terms:
                    if term_matches(raw_text, words, term):
                        files_by_term[term].append(path)
                        folders_by_term[term].add(path.parent.name)

            print("Search term results:")
            print("{: <20} {: >5} {}".format("term", "count", "files"))
            print("{: <20} {: >5} {}".format("----", "-----", "-----"))

            rows = []
            for term in search_terms:
                files = files_by_term.get(term, [])
                short_names = ", ".join(sorted(p.stem for p in files))
                print("{: <20} {: >5} {}".format(term, len(files), short_names))
                rows.append((term, len(files), short_names))

            print()

            # Write results to file if requested
            if args.output:
                out_path = args.output
                out_path.parent.mkdir(parents=True, exist_ok=True)
                suffix = out_path.suffix.lower()

                # Decide write mode
                write_mode = "a" if (args.append and out_path.exists()) else "w"

                # Section name for grouping tables
                if args.section:
                    section_name = args.section
                else:
                    # Prefer input folder name, else first term-file stem, else a generic name
                    if len(args.inputs) == 1 and Path(args.inputs[0]).name:
                        section_name = Path(args.inputs[0]).name
                    elif args.term_file:
                        section_name = args.term_file[0].stem
                    else:
                        section_name = "results"

                if suffix == ".csv":
                    with out_path.open(write_mode, encoding="utf-8", newline="") as fh:
                        writer = csv.writer(fh)
                        # If appending, add a separator row first
                        if write_mode == "a":
                            writer.writerow([])
                            writer.writerow([f"SECTION: {section_name}"])
                        writer.writerow(["term", "count", "files"])
                        for r in rows:
                            writer.writerow(r)
                else:
                    # default to tab-separated for .txt/.tsv/others
                    with out_path.open(write_mode, encoding="utf-8", newline="") as fh:
                        if write_mode == "a":
                            fh.write("\n")
                            fh.write(f"### SECTION: {section_name}\n")
                        fh.write("term\tcount\tfiles\n")
                        for term, count, files_str in rows:
                            fh.write(f"{term}\t{count}\t{files_str}\n")

            unmatched = [term for term in search_terms if term not in files_by_term]
            if unmatched:
                print("No matches found for:")
                for term in unmatched:
                    print(f"- {term}")
                print()

            return

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


