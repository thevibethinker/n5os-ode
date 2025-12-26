import argparse
import logging
from pathlib import Path

JS_SHELL_MARKERS = [
    "JavaScript is not available.",
    "We\u2019ve detected that JavaScript is disabled in this browser.",
    "Some privacy related extensions may cause issues on x.com.",
]

DEFAULT_SCAN_DIRS = [
    Path("/home/workspace/Articles"),
]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )


def file_contains_js_shell(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        logging.warning("Failed to read %s: %s", path, e)
        return False

    return any(marker in text for marker in JS_SHELL_MARKERS)


def scan_directory(dir_path: Path) -> list[Path]:
    matches: list[Path] = []
    if not dir_path.exists():
        logging.info("Directory does not exist, skipping: %s", dir_path)
        return matches

    for path in dir_path.rglob("*.md"):
        if file_contains_js_shell(path):
            matches.append(path)
    return matches


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description=(
            "Lint for broken JS-fallback shells from x.com in Articles/ and "
            "ContentLibrary/content. Exits with code 1 if any are found."
        )
    )
    parser.add_argument(
        "--dir",
        action="append",
        dest="dirs",
        help=(
            "Additional directory to scan (can be used multiple times). "
            "Defaults to Articles/ and ContentLibrary/content."
        ),
    )
    args = parser.parse_args()

    scan_dirs = list(DEFAULT_SCAN_DIRS)
    if args.dirs:
        scan_dirs.extend(Path(d) for d in args.dirs)

    all_matches: list[Path] = []
    for d in scan_dirs:
        logging.info("Scanning directory: %s", d)
        matches = scan_directory(d)
        if matches:
            logging.warning("Found %d JS-shell file(s) in %s", len(matches), d)
            for m in matches:
                print(m)
        all_matches.extend(matches)

    if all_matches:
        logging.error(
            "JS-shell lint FAILED: %d problematic file(s) found.", len(all_matches)
        )
        raise SystemExit(1)

    logging.info("JS-shell lint PASSED: no problematic files found.")


if __name__ == "__main__":
    main()

