import argparse
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple

# Paths are absolute to avoid surprises
N5_SCRIPTS = Path("/home/workspace/N5/scripts")
PCL_SCRIPTS = Path("/home/workspace/Personal/Knowledge/ContentLibrary/scripts")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )


def run_n5_protect_check(path: Path) -> Tuple[bool, str]:
    """Return (is_safe, message). If not safe, message explains why.
    
    n5_protect.py check returns:
    - exit 0 + "⚠️ PROTECTED" → directory IS protected → NOT safe to operate
    - exit 1 + "✓ Not protected" → directory is NOT protected → safe to operate
    """
    cmd = [
        "python3",
        str(N5_SCRIPTS / "n5_protect.py"),
        "check",
        str(path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or proc.stderr).strip()
    
    # exit code 1 = "not protected" = safe to proceed
    if proc.returncode == 1:
        return True, output
    # exit code 0 = "protected" = blocked
    return False, output


def discover_targets() -> List[Tuple[Path, Path, Path]]:
    """Discover .py.new files and map to (new, target, backup).

    Returns list of tuples: (new_file, target_file, backup_file).
    """
    patterns = [
        N5_SCRIPTS / "email_composer.py.new",
        N5_SCRIPTS / "auto_populate_content.py.new",
        N5_SCRIPTS / "b_block_parser.py.new",
        N5_SCRIPTS / "email_corrections.py.new",
        N5_SCRIPTS / "content_library.py.new",
        N5_SCRIPTS / "content_library_db.py.new",
        PCL_SCRIPTS / "ingest.py.new",
        PCL_SCRIPTS / "enhance.py.new",
        PCL_SCRIPTS / "summarize.py.new",
        PCL_SCRIPTS / "content_to_knowledge.py.new",
    ]

    triples: List[Tuple[Path, Path, Path]] = []
    for new_path in patterns:
        if not new_path.exists():
            logging.warning("Expected .new file not found, skipping: %s", new_path)
            continue
        target = new_path.with_suffix("")  # strip single ".new"
        backup = target.with_suffix(target.suffix + ".bak") if target.suffix else target.with_name(target.name + ".bak")
        triples.append((new_path, target, backup))
    return triples


def plan_moves() -> List[Tuple[Path, Path, Path]]:
    triples = discover_targets()
    if not triples:
        logging.info("No .py.new files discovered for cutover.")
    return triples


def perform_cutover(triples: List[Tuple[Path, Path, Path]], dry_run: bool, force: bool) -> None:
    if not triples:
        logging.info("Nothing to do.")
        return

    # n5_protect checks (directory-level)
    checked_dirs = {}
    for _new, target, _backup in triples:
        root = target.parent
        if root in checked_dirs:
            continue
        ok, msg = run_n5_protect_check(root)
        checked_dirs[root] = ok
        if not ok:
            if force:
                logging.warning("n5_protect: %s is PROTECTED but --force used. Proceeding anyway.", root)
                logging.warning("   %s", msg)
            else:
                logging.error("n5_protect blocked operations in %s: %s", root, msg)
                logging.error("Use --force to override protected directory checks.")
                raise SystemExit(1)
        else:
            logging.info("n5_protect OK for %s: %s", root, msg)

    for new_path, target, backup in triples:
        logging.info("Planned move: %s -> %s (backup: %s)", new_path, target, backup)
        if dry_run:
            continue

        # Backup existing target if present
        if target.exists():
            if backup.exists():
                logging.warning("Backup already exists, overwriting: %s", backup)
                backup.unlink()
            logging.info("Backing up %s -> %s", target, backup)
            target.rename(backup)

        # Promote .new to live
        logging.info("Promoting %s -> %s", new_path, target)
        new_path.rename(target)


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(
        description=(
            "Cutover helper for Content Library v3. "
            "By default runs in DRY-RUN mode and only prints planned moves. "
            "Use --execute to perform the renames after reviewing output."
        )
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the cutover (not just dry-run)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override n5_protect checks for protected directories",
    )
    args = parser.parse_args()

    dry_run = not args.execute
    if dry_run:
        logging.info("Running in DRY-RUN mode. No files will be renamed.")
    else:
        logging.warning("EXECUTE mode: this will rename .py.new files into place and create .bak backups.")

    triples = plan_moves()
    perform_cutover(triples, dry_run=dry_run, force=args.force)


if __name__ == "__main__":
    main()



