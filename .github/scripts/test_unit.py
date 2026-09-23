import runpy
import traceback
from pathlib import Path


repositoryRoot = Path(__file__).resolve().parents[2]
unitTests = runpy.run_path(str(repositoryRoot / "UnitTest" / "UnitTest.py"))

# Load the Glyphs-visible tests without importing the repository's macOS-only
# top-level package on the Linux CI runner.
for name, test in unitTests.items():
	if name.startswith("test_") and callable(test):
		globals()[name] = test


def runTests():
	tests = sorted(
		(name, test)
		for name, test in unitTests.items()
		if name.startswith("test_") and callable(test)
	)
	failures = []
	for name, test in tests:
		try:
			test()
		except (KeyboardInterrupt, SystemExit):
			raise
		except Exception:
			failures.append(name)
			print("FAILED %s" % name)
			traceback.print_exc()
		except BaseException as error:
			failures.append(name)
			print("FAILED %s: %s" % (name, error))
		else:
			print("PASSED %s" % name)

	print("\n%d passed, %d failed" % (len(tests) - len(failures), len(failures)))
	return 1 if failures else 0


if __name__ == "__main__":
	raise SystemExit(runTests())
