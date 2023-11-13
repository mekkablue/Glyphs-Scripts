#MenuTitle: Realign BCPs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Realigns handles (BCPs) in current layers of selected glyphs. Useful for resetting out-of-sync handles, e.g., after a transform operation, after interpolation or after switching to a different grid. Hold down Option to process ALL layers of the glyph.
"""

from Foundation import NSPoint, NSNumber, NSMutableArray, NSClassFromString
from AppKit import NSEvent, NSEventModifierFlagOption

Glyphs.clearLog()
thisFont = Glyphs.font
print(f"Aligning BCPs in {thisFont.filepath.lastPathComponent().stringByDeletingDotSuffix()}")

keysPressed = NSEvent.modifierFlags()
optionKeyPressed = keysPressed & NSEventModifierFlagOption == NSEventModifierFlagOption

def triplet(n1, n2, n3):
	return (*n1.position, *n2.position, *n3.position)

def straightenBCPs(layer):
	def closestPointOnLine(P, A, B):
		# vector of line AB
		AB = NSPoint(B.x - A.x, B.y - A.y)
		# vector from point A to point P
		AP = NSPoint(P.x - A.x, P.y - A.y)
		# dot product of AB and AP
		dotProduct = AB.x * AP.x + AB.y * AP.y
		ABsquared = AB.x**2 + AB.y**2
		t = dotProduct / ABsquared
		x = A.x + t * AB.x
		y = A.y + t * AB.y
		return NSPoint(x, y)
	
	def ortho(n1, n2):
		xDiff = n1.x - n2.x
		yDiff = n1.y - n2.y
		# must not have the same coordinates,
		# and either vertical or horizontal:
		if xDiff != yDiff and xDiff * yDiff == 0.0:
			return True
		return False
	
	handleCount = 0
	for p in layer.paths:
		for n in p.nodes:
			if n.connection != GSSMOOTH:
				continue
			nn, pn = n.nextNode, n.prevNode
			if all((nn.type == OFFCURVE, pn.type == OFFCURVE)):
				# surrounding points are BCPs
				smoothen, center, opposite = None, None, None
				for handle in (nn, pn):
					if ortho(handle, n):
						center = n
						opposite = handle
						smoothen = nn if nn != handle else pn
						oldPos = triplet(smoothen, center, opposite)
						p.setSmooth_withCenterNode_oppositeNode_(
							smoothen, center, opposite,
							)
						if oldPos != triplet(smoothen, center, opposite):
							handleCount += 1
						break
				if smoothen == center == opposite == None:
					oldPos = triplet(n, nn, pn)
					n.position = closestPointOnLine(
						n.position, nn, pn,
						)
					if oldPos != triplet(n, nn, pn):
						handleCount +=1
			elif n.type != OFFCURVE and (nn.type, pn.type).count(OFFCURVE) == 1:
				# only one of the surrounding points is a BCP
				center = n
				if nn.type == OFFCURVE:
					smoothen = nn
					opposite = pn
				elif pn.type == OFFCURVE:
					smoothen = pn
					opposite = nn
				else:
					continue # should never occur
				oldPos = triplet(smoothen, center, opposite)
				p.setSmooth_withCenterNode_oppositeNode_(
					smoothen, center, opposite,
					)
				if oldPos != triplet(smoothen, center, opposite):
					handleCount += 1
	return handleCount

thisFont.disableUpdateInterface() # suppresses UI updates in Font View
try:
	for thisLayer in thisFont.selectedLayers:
		thisGlyph = thisLayer.parent
		handleCount = 0
		if optionKeyPressed:
			for everyLayer in thisGlyph.layers:
				if everyLayer.isMasterLayer or everyLayer.isSpecialLayer:
					handleCount += straightenBCPs(everyLayer)
		else:
			handleCount = straightenBCPs(thisLayer)
		if handleCount:
			print("Processed %i BCPs in %s%s" % (handleCount, "all layers of " if optionKeyPressed else "", thisGlyph.name))
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
finally:
	thisFont.enableUpdateInterface() # re-enables UI updates in Font View
	print("Done.")
