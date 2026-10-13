import json
import os

import rich.console
import rich.panel

import scanner

console = rich.console.Console()

def bar(count, max_count, width=20):
    if max_count <= 0:
        return ""
    filled = int(round(width * float(count) / max_count))
    return "####"[:0] + ("\u2593" * filled) + ("\u2591" * (width - filled))

def rollup(items, keyfunc):
    out = {}
    for e in items:
        key = keyfunc(e)
        if key:
            out[key] = out.get(key, 0) + 1
    return out

def section(lines, title, counts, cap=None, chrono=False):
    if not counts:
        return

    lines.append(title)
    if chrono:
        items = sorted(counts.items())
    else:
        items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    overflow = 0

    if cap and len(items) > cap:
        overflow = len(items) - cap
        items = items[:cap]
    top = max(counts.values())

    for name, count in items:
        lines.append("  %-30s %s %d" % (name[:30], bar(count, top), count))
    if overflow:
        lines.append("  ... %d more" % overflow)

    lines.append("")


def run(path, marker_literal, since, before, as_json):
    entries, files_scanned = scanner.scan_tree(path, marker_literal, since=since, before=before)
    parsed = [e for e in entries if not e.malformed]
    malformed = [e for e in entries if e.malformed]
    reviewed = [e for e in parsed if e.is_reviewed()]
    slop = [e for e in parsed if not e.is_reviewed()]
    files_with = len(set(e.path for e in entries))

    data = {
        "files_scanned": files_scanned,
        "files_with_markers": files_with,
        "markers_total": len(entries),
        "slop": len(slop),
        "reviewed": len(reviewed),
        "malformed": len(malformed),
        "by_model": rollup(parsed, lambda e: e.model),
        "by_harness": rollup(parsed, lambda e: e.harness),
        "by_month": rollup(parsed, lambda e: e.date.strftime("%Y-%m") if e.date else None),
        "by_session": rollup(parsed, lambda e: e.session),
        "by_dir": rollup(parsed, lambda e: os.path.dirname(os.path.relpath(e.path, path)) or "."),
    }

    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return

    touched = (100.0 * files_with / files_scanned) if files_scanned else 0.0
    lines = []
    lines.append("files scanned: %d  -  files with markers: %d (%.0f%%)" % (files_scanned, files_with, touched))
    lines.append("markers: %d total  -  %d slop  -  %d reviewed  -  %d malformed" % (
        len(entries), len(slop), len(reviewed), len(malformed)))
    lines.append("")
    section(lines, "by model", data["by_model"])
    section(lines, "by harness", data["by_harness"])
    section(lines, "by month", data["by_month"], chrono=True)
    section(lines, "by directory (worst first)", data["by_dir"], cap=15)
    section(lines, "top sessions", data["by_session"], cap=10)
    console.print(rich.panel.Panel("\n".join(lines).rstrip(), title="deslop > stats", border_style="magenta"))
