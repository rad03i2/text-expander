"""Core storage and expansion logic. Standard-library only."""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Mapping

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
VAR_RE = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")
BUILTINS = {"date", "time", "datetime"}

class ExpanderError(ValueError):
    """Expected user-facing error."""

@dataclass(frozen=True)
class Snippet:
    name: str
    text: str
    description: str = ""

    def validate(self) -> None:
        if not NAME_RE.fullmatch(self.name):
            raise ExpanderError("name must be 1-64 characters: letters, numbers, dot, dash or underscore")
        if not self.text:
            raise ExpanderError("snippet text cannot be empty")
        if len(self.text) > 100_000:
            raise ExpanderError("snippet text exceeds 100,000 characters")
        if len(self.description) > 500:
            raise ExpanderError("description exceeds 500 characters")

def default_store_path() -> Path:
    override = os.environ.get("TEXT_EXPANDER_STORE")
    if override:
        return Path(override).expanduser()
    if os.name == "nt" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "TextExpander" / "snippets.json"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "text-expander" / "snippets.json"

class Store:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else default_store_path()

    def load(self) -> dict[str, Snippet]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExpanderError(f"cannot read store: {exc}") from exc
        if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("snippets"), list):
            raise ExpanderError("unsupported or malformed store format")
        result: dict[str, Snippet] = {}
        try:
            for item in raw["snippets"]:
                snippet = Snippet(str(item["name"]), str(item["text"]), str(item.get("description", "")))
                snippet.validate()
                if snippet.name in result:
                    raise ExpanderError(f"duplicate snippet name in store: {snippet.name}")
                result[snippet.name] = snippet
        except (KeyError, TypeError) as exc:
            raise ExpanderError("malformed snippet in store") from exc
        return result

    def save(self, snippets: Mapping[str, Snippet]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "snippets": [asdict(snippets[k]) for k in sorted(snippets)]}
        data = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        fd, tmp = tempfile.mkstemp(prefix=".snippets-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, self.path)
        except Exception:
            try: os.unlink(tmp)
            except OSError: pass
            raise

    def put(self, snippet: Snippet, overwrite: bool = False) -> None:
        snippet.validate()
        snippets = self.load()
        if snippet.name in snippets and not overwrite:
            raise ExpanderError(f"snippet already exists: {snippet.name}; use --overwrite")
        snippets[snippet.name] = snippet
        self.save(snippets)

    def delete(self, name: str) -> None:
        snippets = self.load()
        if name not in snippets:
            raise ExpanderError(f"snippet not found: {name}")
        del snippets[name]
        self.save(snippets)

def variables(text: str) -> list[str]:
    return sorted(set(VAR_RE.findall(text)) - BUILTINS)

def expand(snippet: Snippet, values: Mapping[str, str] | None = None, *, now: datetime | None = None, strict: bool = True) -> str:
    values = dict(values or {})
    moment = now or datetime.now().astimezone()
    context = {"date": moment.strftime("%Y-%m-%d"), "time": moment.strftime("%H:%M:%S"), "datetime": moment.isoformat(timespec="seconds"), **values}
    missing = [name for name in variables(snippet.text) if name not in context]
    if missing and strict:
        raise ExpanderError("missing variables: " + ", ".join(missing))
    return VAR_RE.sub(lambda m: context.get(m.group(1), m.group(0)), snippet.text)

def parse_values(items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ExpanderError(f"variable must use KEY=VALUE: {item}")
        key, value = item.split("=", 1)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ExpanderError(f"invalid variable name: {key}")
        result[key] = value
    return result
