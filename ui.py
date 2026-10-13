import sys
import os

try:
    import rich.console
    import rich.panel
except ImportError:
    print("deslop needs the 'rich' library: pip install rich")
    raise

console = rich.console.Console()

try:
    import prompt_toolkit
    import prompt_toolkit.key_binding

    _HAVE_PTK = True
except ImportError:
    _HAVE_PTK = False

def is_tty():
    return sys.stdin.isatty() and sys.stdout.isatty()

def snippet(lines, line_no, context=2):
    start = max(0, line_no - 1 - context)
    end = min(len(lines), line_no + context)
    rows = []
    for num in range(start + 1, end + 1):
        text = lines[num - 1].rstrip()
        if len(text) > 100:
            text = text[:99] + "..."
        arrow = "  <" if num == line_no else ""
        rows.append("%5d | %s%s" % (num, text, arrow))
    return "\n".join(rows)

def review_banner(file_path, file_index, file_total, files_cleaned, remaining,
                  sessions, entry, lines, verdict, nag):
    status = "file %d/%d (%s) -  %d cleaned  -  %d unreviewed marker(s) here  -  session %d" % (
        file_index, file_total, os.path.basename(file_path), files_cleaned, remaining, sessions)
    if entry.malformed:
        meta = "MALFORMED marker (core grammar missing)"
    else:
        bits = [entry.model or "?"]
        if entry.date:
            bits.append(entry.date.isoformat())
        if entry.harness:
            bits.append("harness:" + entry.harness)
        if entry.session:
            bits.append("session:" + entry.session)
        meta = "  -  ".join(bits)
    body = "deslop > review\n"
    body += status + "\n\n"
    body += "line %d  -  %s\n\n" % (entry.line_no, meta)
    body += snippet(lines, entry.line_no)
    if verdict:
        body += "\n\nlast: " + verdict
    if nag:
        body += "\n" + nag
    console.print(rich.panel.Panel(body, border_style="magenta"))

def read_key(options):
    """Wait for a single keypress. options e.g. ['enter','q'] or ['enter','r','q']."""
    prompt_text = "  [Enter] continue / [q] quit"
    if "r" in options:
        prompt_text = "  [Enter] continue / [r] stamp reviewed / [q] quit"
    prompt_text += " > "
    if _HAVE_PTK and is_tty():
        bindings = prompt_toolkit.key_binding.KeyBindings()

        def _make(result_value):
            def _handler(event):
                event.app.exit(result=result_value)
            return _handler

        bindings.add("enter")(_make("enter"))
        if "r" in options:
            bindings.add("r")(_make("r"))
        bindings.add("q")(_make("q"))
        bindings.add("c-c")(_make("q"))
        session = prompt_toolkit.PromptSession(key_bindings=bindings, mouse_support=False)
        try:
            return session.prompt(prompt_text, reserve_space_for_menu=0)
        except KeyboardInterrupt:
            return "q"
    try:
        answer = input(prompt_text).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "q"
    if answer == "q":
        return "q"
    if answer == "r" and "r" in options:
        return "r"
    return "enter"
