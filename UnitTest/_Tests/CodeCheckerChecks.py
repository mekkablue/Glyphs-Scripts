import json
import os
import re
import subprocess
from pathlib import Path

import ruff

from TestHelpers import repositoryRoot


# These names predate the tests and are supplied implicitly by Glyphs, hidden
# behind wildcard imports, or otherwise existing technical debt. New undefined
# names are still reported by Ruff.
knownUndefinedNames = {
}


def runRuff(arguments):
	ruffExecutable = ruff.find_ruff_bin()
	assert ruffExecutable, "Ruff is installed but did not return its executable path."
	assert os.path.isfile(ruffExecutable), "Ruff executable does not exist: %s" % ruffExecutable
	command = [str(ruffExecutable)] + arguments
	return subprocess.run(
		command,
		cwd=str(repositoryRoot),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
	)


def relativePath(path):
	path = Path(path)
	if not path.is_absolute():
		path = repositoryRoot / path
	try:
		return str(path.resolve().relative_to(repositoryRoot.resolve()))
	except ValueError:
		return str(path)


def isKnownUndefinedName(path, name):
	return name in knownUndefinedNames.get(relativePath(path), set())


def checkRuffUndefinedNames():
	result = runRuff(
		[
			"check",
			"--select=F821",
			"--output-format=json",
			str(repositoryRoot),
		],
	)
	try:
		diagnostics = json.loads(result.stdout or "[]")
	except json.JSONDecodeError:
		raise AssertionError("Ruff did not return JSON:\n%s\n%s" % (result.stdout, result.stderr))

	unexpectedDiagnostics = []
	for diagnostic in diagnostics:
		match = re.search(r"`([^`]+)`", diagnostic.get("message", ""))
		name = match.group(1) if match else ""
		if isKnownUndefinedName(diagnostic.get("filename", ""), name):
			continue
		location = diagnostic.get("location", {})
		unexpectedDiagnostics.append(
			"%s:%s:%s: %s %s" % (
				relativePath(diagnostic.get("filename", "")),
				location.get("row", 0),
				location.get("column", 0),
				diagnostic.get("code", "F821"),
				diagnostic.get("message", "Undefined name"),
			)
		)

	if result.returncode not in (0, 1):
		raise AssertionError("Ruff failed to run:\n%s\n%s" % (result.stdout, result.stderr))
	assert not unexpectedDiagnostics, "Ruff found undefined names:\n" + "\n".join(unexpectedDiagnostics)
