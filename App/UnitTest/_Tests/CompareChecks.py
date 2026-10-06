import io
import sys
import types
from contextlib import redirect_stdout

from TestHelpers import loadModule


try:
	import GlyphsApp  # noqa: F401
except ImportError:
	glyphsApp = types.ModuleType("GlyphsApp")
	glyphsApp.Glyphs = types.SimpleNamespace(versionNumber=4)
	glyphsApp.GSCustomParameter = type("GSCustomParameter", (), {})
	sys.modules["GlyphsApp"] = glyphsApp

compare = loadModule("compareForTests", "Compare Frontmost Fonts/compare.py")


def checkCompareListsReturnsUniqueItems():
	thisItems = ["shared", "only this"]
	otherItems = ["only other", "shared"]
	assert compare.compareLists(thisItems, otherItems) == (["only this"], ["only other"])


def checkCompareListsCanIgnoreEmptyItems():
	thisItems = [None, "", "only this"]
	otherItems = ["only other", None, ""]
	assert compare.compareLists(thisItems, otherItems, ignoreEmpty=True) == (["only this"], ["only other"])


def checkCleanupShortensAndFlattensContent():
	content = compare.cleanUpAndShortenParameterContent("first line\nsecond  line", maxLength=18)
	assert content == "'first line second..."


def checkCompareCountReport():
	output = io.StringIO()
	with redirect_stdout(output):
		compare.compareCount("glyphs", 2, 2, "A", "B")
		compare.compareCount("masters", 1, 3, "A", "B")
	report = output.getvalue()
	assert "Same number of glyphs: 2" in report
	assert "Different number of MASTERS" in report
