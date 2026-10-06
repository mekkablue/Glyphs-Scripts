import importlib.util
from pathlib import Path


repositoryRoot = Path(__file__).resolve().parent.parent


def loadModule(moduleName, relativePath):
	path = repositoryRoot / relativePath
	spec = importlib.util.spec_from_file_location(moduleName, path)
	if spec is None or spec.loader is None:
		raise ImportError("Could not load %s" % path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module
