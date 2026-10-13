# -- AI GENERATED CODE (Qwen3.8 Flash Next) :: 2026-10-14
# Marker grammar:
#   <MARKER> (MODEL) :: (YYYY-MM-DD) [harness:X] [session:ID] [status:reviewed]
# The delimiters around MODEL and DATE are intentionally lenient: real-world
# markers drift ((DATE) vs DATE vs [DATE] etc. depending on how prompts were
# worded), so we accept any non-digit wrapper characters. The date itself
# stays strict (YYYY-MM-DD) - a marker line with no valid date after the
# marker is malformed. key:value tokens are found anywhere on the line.

import datetime
import re

STATUS_REVIEWED = "reviewed"

CORE_RE = re.compile(r"^\s*\(?\s*([^()\s][^()]*?)\s*\)?\s*::\s*[^0-9]*?(\d{4}-\d{2}-\d{2})")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*:\S+")


class Marker(object):
    def __init__(self):
        self.path = ""
        self.line_no = 0
        self.raw = ""
        self.model = None
        self.date = None
        self.harness = None
        self.session = None
        self.status = None
        self.other = {}
        self.malformed = False

    def is_reviewed(self):
        return self.status == STATUS_REVIEWED


def parse_line(line, marker_literal):
    """Parse a single line. Returns a Marker if the marker literal is present, else None."""
    idx = line.find(marker_literal)
    if idx < 0:
        return None
    entry = Marker()
    entry.raw = line.rstrip("\n")
    rest = line[idx + len(marker_literal):]
    core = CORE_RE.match(rest)
    if core is None:
        entry.malformed = True
        return entry
    entry.model = core.group(1).strip(" ()[]{}<>")
    digits = core.group(2)
    try:
        entry.date = datetime.date(int(digits[0:4]), int(digits[5:7]), int(digits[8:10]))
    except ValueError:
        entry.malformed = True
        return entry
    tail = rest[core.end():]
    # tolerate closing comment syntax like */ on the same line
    tail = re.sub(r"\*/\s*$", "", tail)
    for tok in TOKEN_RE.finditer(tail):
        key, _, value = tok.group(0).partition(":")
        if key == "harness":
            entry.harness = value
        elif key == "session":
            entry.session = value
        elif key == "status":
            entry.status = value
        else:
            entry.other[key] = value
    # lenient: trailing prose/junk after the core is tolerated, not malformed.
    # only a missing/unparseable model+date core demotes an entry.
    return entry


def stamp_line(line, marker_literal):
    """Append/replace status:reviewed on a marker line. Returns new line or None."""
    idx = line.find(marker_literal)
    if idx < 0:
        return None
    rest = line[idx + len(marker_literal):]
    core = CORE_RE.match(rest)
    if core is None:
        return None  # never stamp malformed markers
    existing = re.search(r"\bstatus:\S+", line)
    if existing:
        return line[:existing.start()] + "status:" + STATUS_REVIEWED + line[existing.end():]
    insert_at = idx + len(marker_literal) + core.end()
    return line[:insert_at] + " status:" + STATUS_REVIEWED + line[insert_at:]
