import math
import sys
import types
from types import SimpleNamespace

from TestHelpers import loadModule


try:
	import Foundation  # noqa: F401
except ImportError:
	class Point:
		def __init__(self, x, y):
			self.x = x
			self.y = y

	foundation = types.ModuleType("Foundation")
	foundation.NSClassFromString = lambda name: None
	foundation.NSPoint = Point
	sys.modules["Foundation"] = foundation

try:
	import AppKit  # noqa: F401
except ImportError:
	appKit = types.ModuleType("AppKit")
	appKit.NSAffineTransform = object
	sys.modules["AppKit"] = appKit

geometry = loadModule("geometryForTests", "geometry.py")


def rect(x, y, width, height):
	return SimpleNamespace(
		origin=SimpleNamespace(x=x, y=y),
		size=SimpleNamespace(width=width, height=height),
	)


def layer(x, y, width, height, nodeX=None, nodeY=None, italicAngle=0):
	paths = ()
	if nodeX is not None and nodeY is not None:
		paths = (SimpleNamespace(nodes=(SimpleNamespace(x=nodeX, y=nodeY),)),)
	return SimpleNamespace(bounds=rect(x, y, width, height), paths=paths, italicAngle=italicAngle)


def checkBezierEndpointsAndMidpoint():
	assert geometry.bezier(0, 0, 0, 0, 10, 10, 10, 10, 0) == (0, 0)
	assert geometry.bezier(0, 0, 0, 0, 10, 10, 10, 10, 1) == (10, 10)
	assert geometry.bezier(0, 0, 0, 0, 10, 10, 10, 10, 0.5) == (5, 5)


def checkDivideToleratesZero():
	assert geometry.divideAndTolerateZero(10, 0) is None
	assert geometry.divideAndTolerateZero(10, 4) == 2.5


def checkAngle():
	origin = geometry.NSPoint(0, 0)
	assert geometry.angle(origin, geometry.NSPoint(10, 0)) == 0
	assert geometry.angle(origin, geometry.NSPoint(0, 10)) == 90
	assert geometry.angle(origin, geometry.NSPoint(-10, 0)) == 180


def checkNormalizedCoordinate():
	boxLayer = layer(100, 200, 200, 400)
	assert geometry.normalizedCoordinate(150, 300, boxLayer) == (0.25, 0.25)


def checkNormalizedCoordinateAccountsForItalicAngle():
	angle = 10
	x = 100 + 0.25 * 200 + 100 * math.tan(math.radians(angle))
	boxLayer = layer(100, 200, 200, 400)
	normalizedX, normalizedY = geometry.normalizedCoordinate(x, 300, boxLayer, angle=angle)
	assert abs(normalizedX - 0.25) < 0.000001
	assert abs(normalizedY - 0.25) < 0.000001


def checkNormalizedCoordinateWithEmptyBounds():
	assert geometry.normalizedCoordinate(10, 20, layer(0, 0, 0, 100)) == (0.0, 0.0)
	assert geometry.normalizedCoordinate(10, 20, layer(0, 0, 100, 0)) == (0.0, 0.0)


def checkNormalizedMove():
	firstLayer = layer(0, 0, 100, 100, 25, 25)
	secondLayer = layer(0, 0, 100, 100, 50, 75)
	glyph = SimpleNamespace(layers={"first": firstLayer, "second": secondLayer})
	assert geometry.normalizedMove(glyph, 0, 0, "first", "second") == (0.25, 0.5)


def checkNormalizedMoveRejectsUnusableLayers():
	validLayer = layer(0, 0, 100, 100, 25, 25)
	emptyLayer = layer(0, 0, 0, 100, 25, 25)
	glyph = SimpleNamespace(layers={"missing": None, "valid": validLayer, "empty": emptyLayer})
	assert geometry.normalizedMove(glyph, 0, 0, "missing", "valid") is None
	assert geometry.normalizedMove(glyph, 0, 0, "valid", "empty") is None
	assert geometry.normalizedMove(glyph, 2, 0, "valid", "valid") is None
