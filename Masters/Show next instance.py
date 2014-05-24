#MenuTitle: Show next instance
# -*- coding: utf-8 -*-
__doc__="""
Jumps to next instance shown in the preview field of the current Edit tab.
"""

import GlyphsApp

Doc = Glyphs.currentDocument
numberOfInstances = len( Glyphs.font.instances )

try:
	currentInstanceNumber = Doc.windowController().activeEditViewController().selectedInstance()
	
	if currentInstanceNumber < numberOfInstances:
		Doc.windowController().activeEditViewController().setSelectedInstance_( currentInstanceNumber + 1 )
	else:
		Doc.windowController().activeEditViewController().setSelectedInstance_( 1 )
		
except Exception, e:
	print "Error:", e

