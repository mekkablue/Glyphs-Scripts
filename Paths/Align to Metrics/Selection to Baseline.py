#MenuTitle: Align Selection to Baseline
# -*- coding: utf-8 -*-
__doc__="""
Align selected paths (and parts of paths) in the frontmost layer to the Baseline.
"""

import GlyphsApp

Font = Glyphs.font
Doc = Glyphs.currentDocument
selectedLayer = Font.selectedLayers[0]

try:
	try:
		# until v2.1:
		selection = selectedLayer.selection()
	except:
		# since v2.2:
		selection = selectedLayer.selection
	
	lowestY = min( ( n.y for n in selection ) )

	Font.disableUpdateInterface()

	for thisNode in selection:
		thisNode.y -= lowestY

	Font.enableUpdateInterface()
	
except Exception, e:
	print "Error: Nothing selected in frontmost layer?"
	print e
