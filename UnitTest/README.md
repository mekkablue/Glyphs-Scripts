# Unit tests

Open `UnitTest.py` in Glyphs’ test sidebar. Glyphs can run the complete file or
any individual `test_*` function shown below it.

`UnitTest.py` is intentionally a thin facade: its top-level functions are what
Glyphs discovers and displays, but their implementation lives in the small
modules under `_Tests/`. This preserves Glyphs’ per-test UI without allowing the
main file to grow into thousands of lines.

To add a test:

1. Add the test logic as a `check...` function in the appropriate `_Tests`
   module. Use `TestHelpers.loadModule()` for scripts whose paths are not valid
   Python module names.
2. Add a short top-level `test_*` wrapper to `UnitTest.py`. That wrapper is the
   name Glyphs will display in the sidebar.

Prefer small fake Glyphs objects for unit tests. Tests that manipulate the UI or
require an open font should be clearly separated as integration tests because
they are slower and depend on application state.

`test_scripts_have_valid_python_syntax` checks whether Python can parse and
compile every script. The Ruff test additionally fails on new undefined names.
It uses Ruff from Glyphs’ Python runtime; trigger its installation with the
Code Checker button before running the test for the first time.