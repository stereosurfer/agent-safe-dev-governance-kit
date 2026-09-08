import contextlib
import io
import tempfile
import unittest
from pathlib import Path
import asgk3 as a


class UtilityTests(unittest.TestCase):
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'input.json'
            path.write_text('{"x":1,"x":2}', encoding='utf-8')
            with self.assertRaises(a.Invalid) as error:
                a.load(path)
            self.assertEqual('DUPLICATE_KEY', error.exception.finding['code'])

    def test_paths(self):
        for name in ('../x', '/x', 'x//y', './x', 'x/*', 'x\\y'):
            with self.subTest(name=name), self.assertRaises(a.Invalid):
                a.path_name(name, 'path')

    def test_new_output_only(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(a.Invalid) as error:
                a.save_bundle(temp, {'x.txt': 'no overwrite'})
            self.assertEqual('OUTPUT_EXISTS', error.exception.finding['code'])

    def test_output_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(a.Invalid):
                a.save_bundle(Path(temp) / 'out', {'../x.txt': 'bad'})
            self.assertFalse((Path(temp) / 'out').exists())

    def test_no_standalone_authority_command(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            a.main(['compile', '--input', 'arbitrary-local-authority.json'])

    def test_digest(self):
        self.assertEqual(a.digest({'a': 1, 'b': 2}), a.digest({'b': 2, 'a': 1}))


if __name__ == '__main__':
    unittest.main()
