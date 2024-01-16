# MenuTitle: Fix Arabic Anchor Ordering in Ligatures
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Fix the order of top_X and bottom_X anchors to RTL.
"""

from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnchor


Font = Glyphs.font
FontMaster = Font.selectedFontMaster
selectedLayers = Font.selectedLayers


def makeAnchor(thisLayer, anchorName, x, y):
	thisAnchorPosition = NSPoint()
	thisAnchorPosition.x = x
	thisAnchorPosition.y = y
	thisAnchorName = anchorName

	thisAnchor = GSAnchor(thisAnchorName, thisAnchorPosition)
	thisLayer.addAnchor_(thisAnchor)

	print("-- %s (%.1f, %.1f)" % (thisAnchorName, thisAnchorPosition.x, thisAnchorPosition.y))


def addListOfAnchors(thisLayer, baseName, listOfCoordinates):
	for i in range(len(listOfCoordinates)):
		currCoord = listOfCoordinates[i]
		makeAnchor(thisLayer, "%s_%i" % (baseName, i + 1), currCoord[0], currCoord[1])


def deleteAnchors(listOfAnchors):
	for i in range(len(listOfAnchors))[::-1]:
		del listOfAnchors[i]


def process(thisLayer):
	topAnchors = [a for a in thisLayer.anchors if "top_" in a.name]
	bottomAnchors = [a for a in thisLayer.anchors if "bottom_" in a.name]
	topAnchorCoords = sorted([[a.x, a.y] for a in topAnchors], key=lambda l: l[0], reverse=True)
	bottomAnchorCoords = sorted([[a.x, a.y] for a in bottomAnchors], key=lambda l: l[0], reverse=True)

	deleteAnchors(topAnchors)
	deleteAnchors(bottomAnchors)

	addListOfAnchors(thisLayer, "top", topAnchorCoords)
	addListOfAnchors(thisLayer, "bottom", bottomAnchorCoords)


Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		thisGlyphName = thisGlyph.name
		if "-ar" in thisGlyphName and "_" in thisGlyphName:
			print("Processing", thisGlyphName)
			process(thisLayer)
except Exception as e:
	raise e
finally:
	Font.enableUpdateInterface()
