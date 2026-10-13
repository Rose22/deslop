# -- AI GENERATED CODE (Qwen3.8 Flash Next) :: 2026-10-14

import hashlib
import os

import marker

DEFAULT_EXCLUDES = (".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", ".idea", ".vscode")


def read_text(path):
    """Returns (text, md5) or (None, None) for unreadable / binary / undecodable files."""
    try:
        with open(path, "rb") as handle:
            blob = handle.read()
    except OSError:
        return None, None
    if b"\x00" in blob[:8192]:
        return None, None  # binary
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError:
        return None, None
    return text, hashlib.md5(blob).hexdigest()


def scan_file(path, marker_literal):
    """Returns (entries, text, digest). text/digest are None if unreadable."""
    text, digest = read_text(path)
    if text is None:
        return [], None, None
    found = []
    for num, line in enumerate(text.splitlines(), start=1):
        entry = marker.parse_line(line, marker_literal)
        if entry is not None:
            entry.path = path
            entry.line_no = num
            found.append(entry)
    return found, text, digest


def walk_files(root, excludes):
    excl = set(excludes)
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in excl and not d.endswith(".egg-info"))
        for name in sorted(files):
            if name.startswith("."):
                continue
            yield os.path.join(dirpath, name)


def passes_filters(entry, since, before):
    if since or before:
        if entry.malformed or entry.date is None:
            return False
        if since and entry.date < since:
            return False
        if before and entry.date >= before:
            return False
    return True


def scan_tree(root, marker_literal, excludes=DEFAULT_EXCLUDES, since=None, before=None):
    """Returns (entries, files_scanned). Entries include reviewed+malformed;
    callers filter. Date filters exclude malformed entries."""
    entries = []
    files_scanned = 0
    for path in walk_files(root, excludes):
        files_scanned += 1
        found, _, _ = scan_file(path, marker_literal)
        for entry in found:
            if passes_filters(entry, since, before):
                entries.append(entry)
    return entries, files_scanned
