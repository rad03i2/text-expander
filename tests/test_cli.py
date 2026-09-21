import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from text_expander.cli import main

class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err): code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_add_expand_list_delete(self):
        with tempfile.TemporaryDirectory() as d:
            store = str(Path(d) / "store.json")
            code, _, _ = self.run_cli(["--store", store, "add", "welcome", "Hello {{name}}"]); self.assertEqual(code, 0)
            code, out, _ = self.run_cli(["--store", store, "expand", "welcome", "--var", "name=Radwan"]); self.assertEqual((code, out.strip()), (0, "Hello Radwan"))
            code, out, _ = self.run_cli(["--store", store, "list", "--json"]); self.assertEqual(code, 0); self.assertIn('"welcome"', out)
            code, _, _ = self.run_cli(["--store", store, "delete", "welcome"]); self.assertEqual(code, 0)

    def test_export_import(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, backup = [str(Path(d) / n) for n in ("a.json", "b.json", "backup.json")]
            self.assertEqual(self.run_cli(["--store", a, "add", "sig", "Regards"])[0], 0)
            self.assertEqual(self.run_cli(["--store", a, "export", backup])[0], 0)
            self.assertEqual(self.run_cli(["--store", b, "import", backup])[0], 0)
            self.assertIn("Regards", self.run_cli(["--store", b, "show", "sig"])[1])

if __name__ == "__main__": unittest.main()
