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

## Manual UI smoke test

`UITest.py` is a separate, user-invoked smoke test for the Vanilla dialogs. Run
it inside Glyphs, choose how long each dialog should remain visible, and click
**Start**. It discovers every repository script that constructs a Vanilla
window, runs the scripts one at a time, and closes only the windows created by
the current script. It does not press any buttons in those dialogs.

For representative results, open a font before starting. The runner reports
script exceptions, dialogs that could not be closed, and scripts that did not
produce a window in `UnitTest/UITest.log`. The Macro window only receives the
current script name and a compact final summary. The runner is intentionally not
imported by `UnitTest.py` and is not run in CI. Every script lifecycle and
window-close attempt is written immediately to the log beside the runner, so
the final entry survives an application crash and identifies where the run
stopped.

`test_scripts_have_valid_python_syntax` checks whether Python can parse and
compile every script. The Ruff test additionally fails on new undefined names.
It uses Ruff from Glyphs’ Python runtime; trigger its installation with the
Code Checker button before running the test for the first time.
