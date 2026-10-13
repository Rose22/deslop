import scanner

def run(path, marker_literal, since, before):
    entries, _ = scanner.scan_tree(path, marker_literal, since=since, before=before)
    visible = [e for e in entries if not e.is_reviewed()]
    if not visible:
        print("clean. no unreviewed markers under %s" % path)
        return

    rows = []
    for e in visible:
        loc = "%s:%d" % (e.path, e.line_no)
        if e.malformed:
            rows.append((loc, "MALFORMED", "", "", ""))
        else:
            rows.append((
                loc,
                e.model or "",
                e.date.isoformat() if e.date else "",
                e.harness or "",
                e.session or "",
            ))

    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    for r in rows:
        print("  ".join(r[i].ljust(widths[i]) for i in range(5)).rstrip())
