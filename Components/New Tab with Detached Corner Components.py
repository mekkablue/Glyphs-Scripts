#MenuTitle: New Tab with Detached Corner Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Opens a new Edit tab containing all glyphs that have a corner component which is not properly connected to a node.
"""

def isLayerAffected( thisLayer ):
	for h in thisLayer.hints:
		if h.type == CORNER:
			if not h.originNode:
				return True
	return False

Glyphs.clearLog() # clears log of Macro window
thisFont = Glyphs.font # frontmost font
fileName = thisFont.filepath.lastPathComponent()
affectedLayers = []

Glyphs.clearLog()
print("Finding detached corner components")
print("📄 %s\n" % fileName)

for thisGlyph in thisFont.glyphs: # loop through all glyphs
	print("🔠 Searching %s..." % thisGlyph.name) # report status in Macro window
	for thisLayer in thisGlyph.layers: # loop through all layers
		# collect affected layers:
		if isLayerAffected( thisLayer ): 
			affectedLayers.append(thisLayer)
			if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
				warningSymbol = "🛑"
			else:
				warningSymbol = "⚠️"
			print("   %s layer ‘%s’" % (warningSymbol, thisLayer.name))

# open a new tab with the affected layers:
if affectedLayers:
	newTab = thisFont.newTab()
	newTab.layers = affectedLayers
	Message(
		title="Found Detached Corner Components",
		message="⚠️ %i layers affected in %s. Details in Macro Window." % (len(affectedLayers), fileName),
		OKButton=None,
		)
# otherwise send a message:
else:
	Message(
		title = "Nothing Found",
		message = "Could not find any glyphs with detached corner components in %s." % fileName,
		OKButton = "😁 Good"
	)
	
