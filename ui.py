import sys
import os

try:
    import rich.console
    import rich.markup
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

def _bar(fraction, width=30):
    if fraction < 0:
        fraction = 0.0
    if fraction > 1:
        fraction = 1.0
    filled = int(round(width * fraction))
    return "[magenta]" + "\u2588" * filled + "[/]" + "[grey37]" + "\u2591" * (width - filled) + "[/]"

def _verdict_style(verdict):
    if verdict.startswith("removed") or verdict.startswith("stamped"):
        return "green"
    if verdict.startswith("edited"):
        return "yellow"
    if verdict.startswith("unchanged"):
        return "grey58"
    return "red"

def snippet(lines, line_no, context=3):
    start = max(0, line_no - 1 - context)
    end = min(len(lines), line_no + context)
    rows = []
    for num in range(start + 1, end + 1):
        raw = lines[num - 1].rstrip()
        if len(raw) > 110:
            raw = raw[:109] + "\u2026"
        text = rich.markup.escape(raw)
        if num == line_no:
            rows.append("[magenta]  %4d \u258c [/][bold magenta]%s[/][magenta] \u25c0[/]" % (num, text))
        else:
            rows.append("[grey37]  %4d \u2502[/] [grey62]%s[/]" % (num, text))
    return "\n".join(rows)

def review_banner(file_path, file_index, file_total, files_cleaned, remaining,
                  sessions, entry, lines, verdict, nag, marker_literal):
    if is_tty():
        console.clear()

    done = files_cleaned + (file_index - 1)
    progress = _bar(float(done) / max(1, file_total))
    head = ("[bold magenta]deslop[/] [grey37]\u25b8[/] review   %s  [bold]%d/%d[/] "
            "[grey37]files[/]  [green]%d cleaned[/]") % (progress, file_index, file_total, files_cleaned)
    sub = ("[bold]%s[/]  [grey37]\u00b7[/]  [yellow]%d[/] unreviewed marker%s here  "
           "[grey37]\u00b7[/]  session %d") % (
        rich.markup.escape(file_path), remaining, "" if remaining == 1 else "s", sessions)

    if entry.malformed:
        meta = "[red]MALFORMED[/] [grey62](no valid model :: date core)[/]"
    else:
        bits = ["[bold]%s[/]" % rich.markup.escape(entry.model or "?")]
        if entry.date:
            bits.append(entry.date.isoformat())
        if entry.harness:
            bits.append("[cyan]harness:[/]%s" % rich.markup.escape(entry.harness))
        if entry.session:
            bits.append("[cyan]session:[/]%s" % rich.markup.escape(entry.session))
        meta = " [grey37]\u2500[/] ".join(bits)

    body = head + "\n" + sub + "\n\n"
    body += "[grey37]line %d[/]  %s\n" % (entry.line_no, meta)
    body += snippet(lines, entry.line_no)
    if verdict:
        body += "\n\n[grey37]last:[/] [%s]%s[/]" % (_verdict_style(verdict), rich.markup.escape(verdict))
    if nag:
        body += "\n[i grey62]%s[/]" % rich.markup.escape(nag)
    body += "\n\n[grey37]marker:[/] [grey58]%s[/]" % rich.markup.escape(marker_literal)
    console.print(rich.panel.Panel(body, border_style="magenta", padding=(1, 2)))

def read_key(options):
    """Wait for a single keypress. options e.g. ['enter','q'] or ['enter','r','q']."""
    prompt_text = "  [Enter] open editor \u00b7 [q] quit"
    if "r" in options:
        prompt_text = "  [Enter] open editor \u00b7 [r] stamp reviewed \u00b7 [q] quit"
    prompt_text += "  > "
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
