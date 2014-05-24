#MenuTitle: Report top positions
# -*- coding: utf-8 -*-
__doc__="""
Reports the y positions of the top anchors of selected glyphs to the Macro Window.
"""

import GlyphsApp

myAnchor = "top"
Font = Glyphs.font
selectedLayers = Font.selectedLayers

try:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
except:
	pass

def process( thisLayer ):
	try:
		myY = thisLayer.anchors[ myAnchor ].y
		print thisLayer.parent.name, "--->", myY
	except Exception, e:
		pass
		# print thisLayer.parent.name, "has no %s anchor." % myAnchor

for thisLayer in selectedLayers:
	process( thisLayer )
