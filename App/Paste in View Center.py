#MenuTitle: Paste in View Center
# -*- coding: utf-8 -*-
__doc__="""
Pastes components and paths in clipboard into the center of the Edit view.
"""

import math

def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
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

Font = Glyphs.font # frontmost font
selectedLayers = Font.selectedLayers # active layers of selected glyphs
Layer = selectedLayers[0]
pasteboard = NSPasteboard.generalPasteboard()
datatype = pasteboard.availableTypeFromArray_(["Glyphs elements pasteboard type"])
pastedata = pasteboard.dataForType_(datatype)
pastetext = NSString.alloc().initWithData_encoding_(pastedata, NSUTF8StringEncoding)
if pastetext:
	pastedict = pastetext.propertyList()
	pastepaths = ()
	pastecomponents = ()
	
	try:
		pastepaths = pastedict["paths"]
	except:
		pass
		
	try:
		pastecomponents = pastedict["components"]
	except:
		pass
	
	if pastepaths or pastecomponents:
		Layer.clearSelectionUndo()
		Layer.setDisableUpdates()
		for pathDict in pastepaths:
			newPath = GSPath.alloc().initWithPathDict_(pathDict)
			Layer.paths.append(newPath)
			newPath.selected = True
		for compDict in pastecomponents:
			newComp = GSComponent.alloc().initWithElementDict_(compDict)
			if newComp.component != Layer.parent:
				newComp.automaticAlignment = False
				Layer.components.append(newComp)
				# this should work, but doesn't:
				# newComp.selected = True
				# so this is a hack to fix it:
				Layer.addSelection_(newComp)
			else:
				print "Paste in View Center Error: Cannot paste a component into its base glyph."
		
		selectionCenterX = Layer.selectionBounds.origin.x + Layer.selectionBounds.size.width * 0.5
		selectionCenterY = Layer.selectionBounds.origin.y + Layer.selectionBounds.size.height * 0.5
		selectionCenter = NSPoint(selectionCenterX,selectionCenterY)
		
		tab = Font.currentTab
		scale = tab.scale
		layerOrigin = tab.selectedLayerOrigin
		viewport = tab.viewPort
		viewCenterX = (viewport.origin.x-layerOrigin.x)/scale + viewport.size.width/scale * 0.5
		viewCenterY = (viewport.origin.y-layerOrigin.y)/scale + viewport.size.height/scale * 0.5
		
		xShift = viewCenterX - selectionCenterX
		yShift = viewCenterY - selectionCenterY
		shiftToMiddle = transform(shiftX=xShift, shiftY=yShift).transformStruct()

		for thisPath in Layer.paths:
			if thisPath.selected:
				thisPath.applyTransform(shiftToMiddle)
				
		for thisComp in Layer.components:
			if thisComp in Layer.selection:
				thisComp.applyTransform(shiftToMiddle)

		Layer.setEnableUpdates()
