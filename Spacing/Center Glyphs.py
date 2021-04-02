#MenuTitle: Center Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Center all selected glyphs inside their respective widths.
"""

import math
from AppKit import NSAffineTransform, NSAffineTransformStruct

Font = Glyphs.font
selectedLayers = Font.selectedLayers

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		skewStruct = NSAffineTransformStruct()
		skewStruct.m11 = 1.0
		skewStruct.m22 = 1.0
		skewStruct.m21 = math.tan(math.radians(skew))
		skewTransform = NSAffineTransform.transform()
		skewTransform.setTransformStruct_(skewStruct)
		myTransform.appendTransform_(skewTransform)
	return myTransform

Font.disableUpdateInterface()
try:
	for thisLayer in selectedLayers:
		thisMaster = thisLayer.master
		shift = ( thisLayer.LSB - thisLayer.RSB ) * -0.5
		shiftMatrix = transform(shiftX=shift).transformStruct()
		thisLayer.applyTransform( shiftMatrix )
		
except Exception as e:
	Glyphs.showMacroWindow()
	print("\n⚠️ 'Center Glyphs' Script Error:\n")
	import traceback
	print(traceback.format_exc())
	print()
	raise e
	
finally:
	Font.enableUpdateInterface() # re-enables UI updates in Font View

print("✅ Centered: %s" % (", ".join( [ l.parent.name for l in selectedLayers ] )))

