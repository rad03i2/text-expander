"""Command-line interface for Text Expander."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .core import ExpanderError, Snippet, Store, expand, parse_values, variables

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="text-expander", description="Local text snippet and template expander")
    p.add_argument("--store", type=Path, help="override snippet store path")
    p.add_argument("--version", action="version", version=f"text-expander {__version__} — Radwan Abdulhadi Ahmed (@rad03i2)")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("add", help="add a snippet")
    a.add_argument("name"); a.add_argument("text", nargs="?"); a.add_argument("--file", type=Path); a.add_argument("--description", default=""); a.add_argument("--overwrite", action="store_true")
    l = sub.add_parser("list", help="list snippets"); l.add_argument("--json", action="store_true")
    s = sub.add_parser("show", help="show one snippet"); s.add_argument("name"); s.add_argument("--json", action="store_true")
    e = sub.add_parser("expand", help="expand a snippet"); e.add_argument("name"); e.add_argument("--var", action="append", default=[], metavar="KEY=VALUE"); e.add_argument("--allow-missing", action="store_true"); e.add_argument("--json", action="store_true")
    d = sub.add_parser("delete", help="delete a snippet"); d.add_argument("name")
    x = sub.add_parser("export", help="export store JSON"); x.add_argument("path", type=Path); x.add_argument("--overwrite", action="store_true")
    i = sub.add_parser("import", help="import a version-1 store"); i.add_argument("path", type=Path); i.add_argument("--overwrite", action="store_true")
    return p

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    store = Store(args.store)
    try:
        if args.command == "add":
            if bool(args.text is not None) == bool(args.file):
                raise ExpanderError("provide exactly one of TEXT or --file")
            text = args.file.read_text(encoding="utf-8") if args.file else args.text
            store.put(Snippet(args.name, text, args.description), args.overwrite)
            print(f"Saved {args.name}")
        elif args.command == "list":
            items = list(store.load().values())
            if args.json: print(json.dumps([asdict(x) for x in items], ensure_ascii=False, indent=2))
            elif not items: print("No snippets saved.")
            else:
                for item in items: print(f"{item.name}\t{item.description}")
        elif args.command == "show":
            item = store.load().get(args.name)
            if not item: raise ExpanderError(f"snippet not found: {args.name}")
            if args.json: print(json.dumps({**asdict(item), "variables": variables(item.text)}, ensure_ascii=False, indent=2))
            else: print(item.text)
        elif args.command == "expand":
            item = store.load().get(args.name)
            if not item: raise ExpanderError(f"snippet not found: {args.name}")
            output = expand(item, parse_values(args.var), strict=not args.allow_missing)
            if args.json: print(json.dumps({"name": item.name, "text": output}, ensure_ascii=False))
            else: print(output)
        elif args.command == "delete":
            store.delete(args.name); print(f"Deleted {args.name}")
        elif args.command == "export":
            if args.path.exists() and not args.overwrite: raise ExpanderError("export destination exists; use --overwrite")
            args.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": 1, "snippets": [asdict(x) for x in store.load().values()]}
            args.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Exported to {args.path}")
        elif args.command == "import":
            source = Store(args.path).load()
            current = store.load()
            conflicts = set(source) & set(current)
            if conflicts and not args.overwrite: raise ExpanderError("conflicting snippets: " + ", ".join(sorted(conflicts)) + "; use --overwrite")
            current.update(source); store.save(current); print(f"Imported {len(source)} snippets")
        return 0
    except (ExpanderError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2

if __name__ == "__main__":
    raise SystemExit(main())
