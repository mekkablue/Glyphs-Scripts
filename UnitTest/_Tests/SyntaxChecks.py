import tokenize
import warnings

from TestHelpers import repositoryRoot


def compileScript(relativePath):
	path = repositoryRoot / relativePath
	with tokenize.open(path) as sourceFile:
		source = sourceFile.read()
	with warnings.catch_warnings():
		warnings.simplefilter("ignore", SyntaxWarning)
		compile(source, str(path), "exec")


def checkScriptsCompile():
	for path in sorted(repositoryRoot.rglob("*.py")):
		relativePath = path.relative_to(repositoryRoot)
		if any(part in (".git", ".claude", "__pycache__") for part in relativePath.parts):
			continue
		compileScript(relativePath)
