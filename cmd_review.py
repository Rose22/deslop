import editor
import marker
import scanner
import ui

def _unreviewed(path, marker_literal, since, before):
    found, text, digest = scanner.scan_file(path, marker_literal)
    kept = [e for e in found if not e.is_reviewed() and scanner.passes_filters(e, since, before)]
    return kept, text, digest

def _stamp(path, marker_literal, entry):
    """adds status:reviewed to a marked snippet of code"""
    text, _ = scanner.read_text(path)
    if text is None:
        return False

    lines = text.splitlines(True)
    idx = entry.line_no - 1
    if idx < 0 or idx >= len(lines):
        return False

    newline = "\n" if lines[idx].endswith("\n") else ""
    stamped = marker.stamp_line(lines[idx].rstrip("\n"), marker_literal)
    if stamped is None:
        return False

    lines[idx] = stamped + newline
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("".join(lines))
    except OSError:
        return False

    return True

def _summary(cleaned, total, removed, stamped, dirty, interrupted):
    print("")
    print("deslop interrupted." if interrupted else "deslop complete.")
    print("  files cleaned: %d/%d" % (cleaned, total))
    print("  markers removed: %d" % removed)
    if stamped:
        print("  markers stamped reviewed: %d" % stamped)
    if dirty:
        print("  left dirty:")
        for path in dirty:
            print("    " + path)

def run(path, marker_literal, since, before, editor_override, stamp):
    entries, _ = scanner.scan_tree(path, marker_literal, since=since, before=before)
    files = sorted(set(e.path for e in entries if not e.is_reviewed()))
    if not files:
        print("clean. no unreviewed markers under %s" % path)
        return

    argv = editor.resolve(editor_override)
    cleaned = 0
    removed = 0
    stamped = 0
    dirty = []
    interrupted = False
    total = len(files)

    for index, file_path in enumerate(files, start=1):
        sessions = 0
        streak = 0
        verdict = ""
        while True:
            kept, text, digest = _unreviewed(file_path, marker_literal, since, before)
            if text is None:
                dirty.append(file_path)
                verdict = "unreadable, skipping"
                break
            if not kept:
                cleaned += 1
                print("OK  %s  cleaned in %d session(s)" % (file_path, sessions))
                break

            first = kept[0]
            nag = ""
            if streak >= 3:
                nag = "this marker has survived %d sessions. you should really clean that up!" % streak
            ui.review_banner(file_path, index, total, cleaned, len(kept), sessions,
                             first, text.splitlines(), verdict, nag)

            options = ["enter", "q"]
            if stamp and not first.malformed:
                options.append("r")
            key = ui.read_key(options)

            if key == "q":
                interrupted = True
                dirty.append(file_path)
                _summary(cleaned, total, removed, stamped, dirty, interrupted)
                return

            if key == "r":
                if _stamp(file_path, marker_literal, first):
                    stamped += 1
                    verdict = "stamped as reviewed"
                else:
                    verdict = "stamp failed"
                continue

            editor.open_at(argv, file_path, first.line_no)
            sessions += 1
            after, _, new_digest = _unreviewed(file_path, marker_literal, since, before)
            if digest is not None and new_digest == digest:
                streak += 1
                verdict = "unchanged"
            elif len(after) < len(kept):
                removed += len(kept) - len(after)
                streak = 0
                verdict = "removed %d marker(s)" % (len(kept) - len(after))
            else:
                streak = 0
                verdict = "edited, still dirty"

    _summary(cleaned, total, removed, stamped, dirty, interrupted)
