#MenuTitle: New Tab with Path Problems
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Opens a new tab with glyphs containing zero handles, bad outline orders or path directions. Only opens master layers in tabs. Full layer report (including non-master layers) in the Macro Window log.
"""

thisFont = Glyphs.font # frontmost font

def hasZeroHandles( thisLayer ):
	for thisPath in thisLayer.paths:
		numberOfNodes = len(thisPath.nodes)
		for i in range(numberOfNodes-1):
			thisNode = thisPath.nodes[i]
			if thisNode.type == GSOFFCURVE:
				prevNodeIndex = (i-1) % numberOfNodes
				nextNodeIndex = (i+1) % numberOfNodes
				prevNode = thisPath.nodes[prevNodeIndex]
				nextNode = thisPath.nodes[nextNodeIndex]
				if thisNode.position == prevNode.position or thisNode.position == nextNode.position:
					return True
	return False
	
def hasTwoPointPaths( thisLayer ):
	for thisPath in thisLayer.paths:
		onCurveNodes = [n for n in thisPath.nodes if n.type != OFFCURVE]
		if len(onCurveNodes) < 3:
			return True
	return False

def hasOpenPaths( thisLayer ):
	for thisPath in thisLayer.paths:
		if not thisPath.closed:
			return True
	return False

def hasBadOutlineOrder( thisLayer ):
	firstPath = thisLayer.paths[0]
	if firstPath and firstPath.direction != -1:
		return True
	else:
		return False

def reportString( myList, myMsg ):
	if myList:
		glyphNames = "/" + "/".join(myList)
		return "%s:\n%s\n\n" % ( myMsg, glyphNames )
	else:
		return ""

def layerIsMasterLayer(thisLayer):
	isMaster = thisLayer.associatedMasterId == thisLayer.layerId
	isSpecial = "[" in thisLayer.name or "{" in thisLayer.name
	return isMaster or isSpecial

def recordLayerInList( thisLayer, thisList, message ):
	# append to list:
	thisGlyph = thisLayer.parent
	glyphName = thisGlyph.name
	thisList.append( glyphName )
	
	# report in macro window:
	print("%s: %s on layer '%s'." % ( glyphName, message, thisLayer.name ))
	
zeroHandles = []
outlineOrder = []
openPaths = []
twoPointPaths = []

Glyphs.clearLog()
Glyphs.showMacroWindow()
print("Checking for bad paths")
print("Font: %s\n" % thisFont.familyName)

for thisGlyph in thisFont.glyphs:
	glyphName = thisGlyph.name
	for thisLayer in thisGlyph.layers:
		if hasZeroHandles( thisLayer ):
			recordLayerInList( thisLayer, zeroHandles, "zero handles" )
		if hasBadOutlineOrder( thisLayer ):
			recordLayerInList( thisLayer, outlineOrder, "bad outline order" )
		if hasOpenPaths( thisLayer ):
			recordLayerInList( thisLayer, openPaths, "open paths" )
		if hasTwoPointPaths( thisLayer ):
			recordLayerInList( thisLayer, twoPointPaths, "two-node paths" )

tabString = reportString(zeroHandles, "Zero Handles")
tabString += reportString(outlineOrder, "Outline Order and Orientation")
tabString += reportString(openPaths, "Open Paths")
tabString += reportString(twoPointPaths, "Two-Node Paths")

if tabString:
	# opens new Edit tab:
	thisFont.newTab( tabString )
else:
	# brings macro window to front and clears its log:
	Message( 
		title="No problems found",
		message="Could not find any zero handles, bad path order or directions, open or two-point paths in this font.",
		OKButton="Hurrah!"
	)