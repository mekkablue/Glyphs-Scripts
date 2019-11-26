from __future__ import print_function
#MenuTitle: Set Style Linking
# -*- coding: utf-8 -*-
__doc__="""
Tries to set Bold/Italic bits in Font Info > Instances.
"""

thisFont = Glyphs.font # frontmost font

def guessStyleLinking( thisInstance ):
	regular = "Regular"
	bold = "Bold"
	italic = "Italic"
	thisInstance.isBold = False
	thisInstance.isItalic = False
	thisInstance.linkStyle = ""
	
	if italic in thisInstance.name:
		thisInstance.isItalic = True
		linkStyleName = thisInstance.name.replace(italic,"").strip()
		if linkStyleName == bold:
			thisInstance.isBold = True
			thisInstance.linkStyle = regular
		else:
			thisInstance.linkStyle = linkStyleName
		
	elif thisInstance.name == bold:
		thisInstance.isBold = True
		thisInstance.linkStyle = regular
	

for thisInstance in thisFont.instances:
	print("BEFORE: %s is %s %s of '%s'" % (
		thisInstance.name,
		"Bold" if thisInstance.isBold else "-",
		"Italic" if thisInstance.isItalic else "-",
		thisInstance.linkStyle if thisInstance.linkStyle else "-"
	))
	guessStyleLinking( thisInstance )
	print("AFTER: %s is %s %s of '%s'\n" % (
		thisInstance.name,
		"Bold" if thisInstance.isBold else "-",
		"Italic" if thisInstance.isItalic else "-",
		thisInstance.linkStyle if thisInstance.linkStyle else "-"
	))
