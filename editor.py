# -- AI GENERATED CODE (Qwen3.8 Flash Next) :: 2026-10-14

import os
import shlex
import subprocess

_warned = {}


def resolve(override):
    raw = override or os.environ.get("EDITOR") or ""
    if not raw.strip():
        raw = "vi"
    return shlex.split(raw)


def build_command(editor_argv, path, line_no):
    name = os.path.basename(editor_argv[0])
    args = list(editor_argv)
    if name in ("vi", "vim", "nvim", "nano", "gedit"):
        args.append("+%d" % line_no)
        args.append(path)
    elif name == "kate":
        args.append("--line")
        args.append(str(line_no))
        if "--wait" not in args:
            args.append("--wait")
        args.append(path)
    elif name == "code":
        args.append("--goto")
        args.append("%s:%d" % (path, line_no))
        if "--wait" not in args:
            args.append("--wait")
    elif name in ("hx", "helix", "micro"):
        args.append("%s:%d" % (path, line_no))
    else:
        if name not in _warned:
            _warned[name] = True
            print("warning: unknown editor '%s' - no line jump, assuming it blocks until closed" % name)
        args.append(path)
    return args


def open_at(editor_argv, path, line_no):
    try:
        return subprocess.run(build_command(editor_argv, path, line_no)).returncode
    except OSError as err:
        print("could not launch editor: %s" % err)
        return None
