#MenuTitle: New Tab with Flipped Components
# -*- coding: utf-8 -*-
__doc__="""
Opens a new edit tab with components that are mirrored horizontally, vertically, or both.
"""



thisFont = Glyphs.font # frontmost font
thisFontMaster = thisFont.selectedFontMaster # active master
listOfSelectedLayers = thisFont.selectedLayers # active layers of selected glyphs

def containsTransformedComponents( thisGlyph ):
	for thisLayer in thisGlyph.layers:
		for thisComponent in thisLayer.components:
			firstFourMatrixValues = thisComponent.transform[:4]
			if firstFourMatrixValues[0] < 0.0 or firstFourMatrixValues[3] < 0.0:
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
		title="No Mirrored Components",
		message="No flipped components found in this font.",
		OKButton="Yeah"
		)