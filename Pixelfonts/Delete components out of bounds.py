#MenuTitle: Delete Components out of Bounds
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Looks for components out of bounds.
"""

from math import fabs

def scanOutOfBounds( thisLayer ):
	listOfComponents = [c for c in thisLayer.components]
	indexesOutOfBounds = []

	for i in range( len( listOfComponents )):
		c = thisLayer.components[i]
		if fabs(c.y) > outOfBounds or fabs(c.x) > outOfBounds:
			indexesOutOfBounds.append(i)
	
	return sorted( set( indexesOutOfBounds ) )

def process( thisLayer ):
	count = 0
	glyphName = thisLayer.parent.name
	
	if len( thisLayer.components ) != 0:
		# thisLayer.parent.beginUndo() # undo grouping causes crashes
	
		indexesOutOfBounds = scanOutOfBounds( thisLayer )
		numberOfOffComponents = len(indexesOutOfBounds)
		count += numberOfOffComponents
		
		if numberOfOffComponents > 0:
			print("⚠️ %s: deleting %i components." % (glyphName, numberOfOffComponents))
		
			for indexOutOfBounds in indexesOutOfBounds[::-1]:
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					for i in range(len(thisLayer.shapes)):
						if thisLayer.shapes[i] == thisLayer.components[indexOutOfBounds]:
							del thisLayer.shapes[i]
							break
				else:
					# GLYPHS 2
					del thisLayer.components[indexOutOfBounds]
				
		else:
			print("✅ %s: no components out of bounds." % glyphName)
		
		# thisLayer.parent.endUndo() # undo grouping causes crashes
	else:
		print("🤷🏻‍♀️ %s: no components." % glyphName)
	
	return count

Font = Glyphs.font
Font.disableUpdateInterface()
try:
	selectedLayers = Font.selectedLayers
	outOfBounds = Glyphs.defaults["com.mekkablue.DeleteComponentsOutOfBounds.threshold"]
	if not outOfBounds:
		outOfBounds = 3000.0
	
	# report:
	Glyphs.clearLog()
	print("Deleting out-of-bounds components in font: %s" % thisFont.familyName)
	print("Threshold: %.1f" % outOfBounds)
	print('\nHint: set a different threshold by running this line in the Macro Window, e.g. 1000u:')
	print('Glyphs.defaults["com.mekkablue.DeleteComponentsOutOfBounds.threshold"] = 1000\n')
	
	componentCount = 0
	for thisLayer in selectedLayers:
		componentCount += process( thisLayer )
	
	# report:
	print("\nDeleted %i components. Done." % componentCount)
	Glyphs.showNotification( 
		"Components out off bounds: %s" % (thisFont.familyName),
		"Deleted %i components in %i selected glyphs. Details in Macro Window." % (componentCount, len(selectedLayers)),
		)
	
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e

finally:
	Font.enableUpdateInterface()
