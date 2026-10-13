#!/usr/bin/env python3
import argparse
import datetime
import sys

import cmd_list
import cmd_review
import cmd_stats

# lol oh no it detects this marker here
DEFAULT_MARKER = "AI GENERATED CODE"

def add_common(sub):
    sub.add_argument("path", nargs="?", default=".", help="root folder to sweep (default: .)")
    sub.add_argument("--marker", default=DEFAULT_MARKER, help="marker string to search for")
    sub.add_argument("--since", default=None, help="only markers dated on/after YYYY-MM-DD")
    sub.add_argument("--before", default=None, help="only markers dated before YYYY-MM-DD")

def parse_date_arg(text, flag):
    try:
        parts = text.split("-")
        return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        print("error: %s expects YYYY-MM-DD, got '%s'" % (flag, text))
        sys.exit(2)

SUBCOMMANDS = ("review", "stats", "list")

def main():
    parser = argparse.ArgumentParser(
        prog="deslop",
        description="sweeps through massive codebases to find markers that denote AI generated code, and lets you manually review and edit each snippet using your favorite editor."
    )
    subs = parser.add_subparsers(dest="command")

    p_review = subs.add_parser("review", help="interactive mode: go through every marker in a file until the file is clean")
    add_common(p_review)
    p_review.add_argument("-e", "--editor", default=None, help="editor override (default: $EDITOR)")
    p_review.add_argument("--stamp", action="store_true", help="allow stamping kept markers with status:reviewed, for code that is fully AI generated and unedited, but deemed good and clean")

    p_stats = subs.add_parser("stats", help="dashboard of markers across the tree")
    add_common(p_stats)
    p_stats.add_argument("--json", action="store_true", help="machine-readable output")

    p_list = subs.add_parser("list", help="list unreviewed markers (skips reviewed and clean files)")
    add_common(p_list)

    # review is the default command: `deslop my_project` == `deslop review my_project`
    argv = sys.argv[1:]
    if argv and argv[0] not in SUBCOMMANDS and argv[0] not in ("-h", "--help"):
        argv = ["review"] + argv

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(1)

    since = parse_date_arg(args.since, "--since") if args.since else None
    before = parse_date_arg(args.before, "--before") if args.before else None

    if args.command == "list":
        cmd_list.run(args.path, args.marker, since, before)
    elif args.command == "stats":
        cmd_stats.run(args.path, args.marker, since, before, args.json)
    elif args.command == "review":
        cmd_review.run(args.path, args.marker, since, before, args.editor, args.stamp)

if __name__ == "__main__":
    main()
