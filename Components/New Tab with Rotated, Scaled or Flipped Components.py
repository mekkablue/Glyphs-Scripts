#MenuTitle: New Tab with Rotated, Scaled or Flipped Components
# -*- coding: utf-8 -*-
__doc__="""
Opens a new edit tab with components that are transformed beyond mere shifts.
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def containsTransformedComponents( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for thisComponent in thisLayer.components:
			if thisComponent.transform[:4] != (1.0,0.0,0.0,1.0):
				return True
	return False

glyphList = []

for thisGlyph in thisFont.glyphs:
	if containsTransformedComponents( thisGlyph ):
		glyphList.append(thisGlyph.name)

if glyphList:
	tabString = "/"+"/".join(glyphList)
	thisFont.newTab(tabString)
else:
	Message(
		title="No Transformed Components",
		message="No rotated, mirrored, or flipped components found in this font.",
		OKButton="Yeah"
		)