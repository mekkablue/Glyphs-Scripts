#MenuTitle: New Tab with Path Problems
# -*- coding: utf-8 -*-
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
	return isMaster and isSpecial
	
zeroHandles = []
outlineOrder = []

Glyphs.clearLog()
Glyphs.showMacroWindow()
print "Checking for bad paths"
print "Font: %s\n" % thisFont.familyName

for thisGlyph in thisFont.glyphs:
	glyphName = thisGlyph.name
	for thisLayer in thisGlyph.layers:
		if hasZeroHandles( thisLayer ):
			print "%s: zero handle on Layer '%s'." % ( glyphName, thisLayer.name )
			if layerIsMasterLayer( thisLayer ):
				zeroHandles.append( glyphName )
		if hasBadOutlineOrder( thisLayer ):
			print "%s: bad path direction on Layer '%s'." % ( glyphName, thisLayer.name )
			if layerIsMasterLayer( thisLayer)
				outlineOrder.append( glyphName )

tabString = reportString(zeroHandles, "Zero Handles") + reportString(outlineOrder, "Outline Order and Orientation")

if tabString:
	# opens new Edit tab:
	thisFont.newTab( tabString )
else:
	# brings macro window to front and clears its log:
	Message( 
		"No problems found",
		"Could not find any zero handles, bad path order or directions in this font.",
		OKButton="Hurrah!"
	)