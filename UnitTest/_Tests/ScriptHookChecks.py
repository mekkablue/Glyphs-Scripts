import ast
import os
import runpy
import sys
import tokenize

import pytest

from TestHelpers import repositoryRoot


excludedDirectories = {".git", ".github", ".claude", "__pycache__", "UnitTest"}
unavailableInCI = {"AppKit", "Foundation", "GlyphsApp", "vanilla"}


def scriptTestPaths():
	paths = []
	for path in sorted(repositoryRoot.rglob("*.py")):
		relativePath = path.relative_to(repositoryRoot)
		if any(part in excludedDirectories or part.startswith(".") for part in relativePath.parts):
			continue
		with tokenize.open(path) as sourceFile:
			tree = ast.parse(sourceFile.read(), filename=str(path))
		if any(isinstance(node, ast.FunctionDef) and node.name == "__test__" for node in tree.body):
			paths.append(relativePath)
	return paths


def unguardedTopLevelCalls(path):
	with tokenize.open(path) as sourceFile:
		tree = ast.parse(sourceFile.read(), filename=str(path))
	return [
		node.lineno
		for node in tree.body
		if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
	]


def isUnavailableGlyphsImport(error):
	if not os.environ.get("GITHUB_ACTIONS"):
		return False
	if error.name in unavailableInCI:
		return True
	message = str(error)
	return any("from '%s'" % moduleName in message for moduleName in unavailableInCI)


def checkScriptTestHook(relativePath):
	path = repositoryRoot / relativePath
	callLines = unguardedTopLevelCalls(path)
	assert not callLines, (
		"%s has executable top-level calls on line(s) %s. Put the script entry "
		"point behind `if __name__ == \"__main__\":` before adding __test__()."
		% (relativePath, ", ".join(str(line) for line in callLines))
	)

	originalPath = list(sys.path)
	try:
		sys.path.insert(0, str(path.parent))
		try:
			namespace = runpy.run_path(str(path), run_name="__mekkablue_script_test__")
		except ImportError as error:
			if isUnavailableGlyphsImport(error):
				print("SKIPPED %s (__test__ requires the Glyphs runtime)" % relativePath)
				return False
			raise
	finally:
		sys.path[:] = originalPath

	testHook = namespace.get("__test__")
	assert callable(testHook), "%s: __test__ is not callable" % relativePath
	try:
		testHook()
	except Exception as error:
		traceback = error.__traceback__
		while traceback.tb_next:
			traceback = traceback.tb_next
		failurePath = traceback.tb_frame.f_code.co_filename
		if not os.path.isabs(failurePath):
			failurePath = os.path.join(str(repositoryRoot), failurePath)
		failurePath = os.path.realpath(failurePath)
		detail = str(error) or error.__class__.__name__
		pytest.fail("%s:%s: %s" % (failurePath, traceback.tb_lineno, detail), pytrace=False)
	return True


def checkScriptTestHooks():
	for relativePath in scriptTestPaths():
		passed = checkScriptTestHook(relativePath)
		if passed:
			print("PASSED %s::__test__" % relativePath)
