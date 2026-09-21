import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from text_expander.core import ExpanderError, Snippet, Store, expand, parse_values, variables

class CoreTests(unittest.TestCase):
    def test_template_expansion_and_builtins(self):
        s = Snippet("hello", "Hello {{name}} on {{date}}")
        out = expand(s, {"name": "Radwan"}, now=datetime(2026, 9, 21, tzinfo=timezone.utc))
        self.assertEqual(out, "Hello Radwan on 2026-09-21")
        self.assertEqual(variables(s.text), ["name"])

    def test_missing_variable_is_error(self):
        with self.assertRaises(ExpanderError): expand(Snippet("x", "{{missing}}"))

    def test_allow_missing(self):
        self.assertEqual(expand(Snippet("x", "{{missing}}"), strict=False), "{{missing}}")

    def test_parse_values_preserves_equals(self):
        self.assertEqual(parse_values(["url=https://x.test/?a=b"])["url"], "https://x.test/?a=b")

    def test_store_round_trip_overwrite_delete(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "nested" / "snippets.json"
            store = Store(path)
            store.put(Snippet("sig", "Regards"))
            self.assertEqual(store.load()["sig"].text, "Regards")
            with self.assertRaises(ExpanderError): store.put(Snippet("sig", "New"))
            store.put(Snippet("sig", "New"), overwrite=True)
            self.assertEqual(store.load()["sig"].text, "New")
            store.delete("sig")
            self.assertEqual(store.load(), {})

    def test_rejects_bad_name_and_malformed_store(self):
        with self.assertRaises(ExpanderError): Snippet("bad name", "x").validate()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.json"; path.write_text(json.dumps({"version": 99, "snippets": []}))
            with self.assertRaises(ExpanderError): Store(path).load()

if __name__ == "__main__": unittest.main()
