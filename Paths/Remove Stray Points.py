#MenuTitle: Remove Stray Points
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes stray points (single node paths) in selected glyphs. Careful: a stray point can be used as a quick hack to disable automatic alignment.
"""

def process( thisLayer ):
	strayPoints = 0
	for i in range(len(thisLayer.paths))[::-1]:
		thisPath = thisLayer.paths[i]
		if len(thisPath) == 1:
			if Glyphs.versionNumber >= 3:
				index = thisLayer.shapes.index(thisPath)
				del thisLayer.shapes[index]
			else:
				# Glyphs 2 code
				thisLayer.removePathAtIndex_(i)
			strayPoints += 1
	return strayPoints

thisFont = Glyphs.font # frontmost font
selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
Glyphs.clearLog() # clears macro window log:
thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	namesOfAffectedGlyphs = []
	totalCount = 0
	for thisLayer in selectedLayers:
		thisGlyph = thisLayer.parent
		numberOfDeletedStrayPoints = process( thisLayer )
		totalCount += numberOfDeletedStrayPoints
	
		# Report deleted nodes:
		glyphName = thisGlyph.name
		if numberOfDeletedStrayPoints > 0:
			print("⚠️ Deleted %i stray nodes in %s." % ( numberOfDeletedStrayPoints, glyphName ))
			namesOfAffectedGlyphs.append( glyphName )
		else:
			print("✅ No stray points in %s." % glyphName)
	
	# Report affected glyphs:
	if namesOfAffectedGlyphs:
		print("\nWARNING:\nStray nodes can be used as a hack to disable automatic alignment. It may be a good idea to check these glyphs for unwanted shifts, and undo if necessary:\n\n/%s\n" % "/".join(namesOfAffectedGlyphs))
	
	print("🔢 %i selected glyphs (of %i in total in the font)." % (len(selectedLayers), len(thisFont.glyphs)))
	print("🔢 %i affected glyphs with %i stray points." % (len(namesOfAffectedGlyphs), totalCount))
	
	# Floating notification:
	Glyphs.showNotification( 
		"Stray Points in %s" % (thisFont.familyName),
		"Deleted %i stray points in %i selected glyphs. Details in Macro Window." % (
			totalCount,
			len(selectedLayers)
			),
		)
	
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
