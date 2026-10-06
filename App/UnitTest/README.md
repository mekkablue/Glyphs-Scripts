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

## Tests embedded in scripts

A script can opt into automatic test discovery by defining a top-level
`__test__()` function:

```python
def __test__():
	result = helperFunction(2)
	assert result == 4, "Expected 4, got %s" % result


if __name__ == "__main__":
	main()
```

`test_script_test_hooks` discovers these functions recursively and runs them.
The hook takes no arguments; use ordinary assertions, and let unexpected
exceptions propagate. Include expected and actual values in assertion messages,
because dynamically loaded hooks do not receive pytest's assertion rewriting.
The runner reduces a hook failure to its absolute script path, line number, and
message so consoles can turn the location into a clickable link. Internal
discovery and loading frames are suppressed.

Discovery parses files without importing them. Only files that contain an
`__test__()` hook are loaded. A hook-bearing script must therefore put its
entry point behind the `if __name__ == "__main__":` guard shown above; the
runner rejects unguarded top-level calls before loading the script.

Hooks containing only portable Python run both in Glyphs and in GitHub CI.
Hooks whose script requires `GlyphsApp`, `AppKit`, `Foundation`, or `vanilla`
run in Glyphs and are reported as skipped by Linux CI when that import is not
available. Use the existing `_Tests` modules and fake objects when such logic
also needs CI coverage.

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
