import json
import os
import subprocess
from pathlib import Path

import ruff

from TestHelpers import repositoryRoot


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

	formattedDiagnostics = []
	for diagnostic in diagnostics:
		location = diagnostic.get("location", {})
		formattedDiagnostics.append(
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
	assert not formattedDiagnostics, "Ruff found undefined names:\n" + "\n".join(formattedDiagnostics)
