#MenuTitle: Populate Layer Backgrounds with Component
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Adds a component to all backgrounds of all layers of all selected glyphs. Useful, e.g., for putting A in the background of (decomposed) Aogonek.
"""

import vanilla, math
from Foundation import NSAffineTransform, NSAffineTransformStruct, NSEvent

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


class PopulateAllBackgroundswithComponent( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 380
		windowHeight = 155
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Populate Layer Backgrounds with Component", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.PopulateAllBackgroundswithComponent.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 10, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), 
			"In selected glyphs, insert component in all layer backgrounds:", 
			sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 100, 14), "Add component:", sizeStyle='small' )
		self.w.componentName = vanilla.EditText( (inset+100, linePos, -inset-25, 19), "a", sizeStyle='small', callback=self.SavePreferences)
		self.w.componentName.getNSTextField().setToolTip_("Name of the glyph that should be inserted as component in the background of all layers of the selected glyph(s).")
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), u"↺", sizeStyle='small', callback=self.update )
		self.w.updateButton.getNSButton().setToolTip_("Guess the component name. Hold down OPTION to ignore the suffix.")
		linePos += lineHeight
		
		self.w.alignRight = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Align with right edge of layer", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.alignRight.getNSButton().setToolTip_("Right-aligns the component width with the layer width. Useful for the e in ae or oe, for example.")
		linePos += lineHeight
		
		self.w.replaceBackgrounds = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Replace existing backgrounds", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.replaceBackgrounds.getNSButton().setToolTip_("Deletes existing background content before it inserts the component. Recommended if you want to align selected nodes with the background.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Populate", sizeStyle='regular', callback=self.PopulateAllBackgroundswithComponentMain )
		self.w.runButton.getNSButton().setToolTip_("Inserts the specified component in ALL layers of the current glyph(s).")
		self.w.setDefaultButton( self.w.runButton )
		
		self.w.alignButton = vanilla.Button( (-240-inset, -20-inset, -130-inset, -inset), "Align Nodes", sizeStyle='regular', callback=self.AlignNodesMain )
		self.w.alignButton.getNSButton().setToolTip_("Aligns selected nodes with the (original) nodes in the background components. Only does this on the CURRENT layer.")
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Populate All Backgrounds with Component' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def update(self, sender):
		# check if Option key is pressed or not:
		optionKeyFlag = 524288
		optionKeyPressed = NSEvent.modifierFlags() & optionKeyFlag == optionKeyFlag
		
		# some predetermined guesses:
		betterGuesses = {
			"perthousand": "percent",
			"brokenbar": "bar",
			"daggerdbl": "dagger",
			"dollar": "S",
			"cent": "c",
			"Fhook": "florin",
			"endash": "hyphen",
			"emdash": "endash",
			"Eng": "N",
			"eng": "n",
			"thorn": "p",
			"Thorn": "I",
			"ae": "e",
			"oe": "e",
			"AE": "E",
			"OE": "E",
			"germandbls": "f",
			"Germandbls": "F",
		}
		
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				currentLayer = thisFont.selectedLayers[0]
				currentGlyph = currentLayer.parent
				
				# do predetermined guesses apply:
				if currentGlyph.name in betterGuesses:
					glyphName = betterGuesses[currentGlyph.name]
					self.w.componentName.set(glyphName)
					self.SavePreferences(sender)
					return True
				
				# check for the dot suffix:
				suffix = ""
				if "." in currentGlyph.name:
					offset = currentGlyph.name.find(".")
					suffix = currentGlyph.name[offset:]
				
				# if glyph info has components, take the base letter name:
				thisInfo = currentGlyph.glyphInfo
				if thisInfo and thisInfo.components:
					firstComponentName = thisInfo.components[0].name
					if firstComponentName:
						if not optionKeyPressed: # hold down OPT to ignore suffix
							firstComponentName += suffix
						self.w.componentName.set(firstComponentName)
						self.SavePreferences(sender)
						return True
						
				# no first component found, so try same name without suffix:
				if suffix:
					self.w.componentName.set(currentGlyph.name[:offset])
					self.SavePreferences(sender)
					return True

		return False
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.componentName"] = self.w.componentName.get()
			Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.alignRight"] = self.w.alignRight.get()
			Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.replaceBackgrounds"] = self.w.replaceBackgrounds.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.PopulateAllBackgroundswithComponent.componentName", "a")
			Glyphs.registerDefault("com.mekkablue.PopulateAllBackgroundswithComponent.alignRight", 0)
			Glyphs.registerDefault("com.mekkablue.PopulateAllBackgroundswithComponent.replaceBackgrounds", 0)
			self.w.componentName.set( Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.componentName"] )
			self.w.alignRight.set( Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.alignRight"] )
			self.w.replaceBackgrounds.set( Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.replaceBackgrounds"] )
		except:
			return False
			
		return True

	def PopulateAllBackgroundswithComponentMain( self, sender ):
		try:
			
			# determine component:
			componentName = Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.componentName"]
			if not componentName:
				Message(title="Component Error", message="No component name specified. Please specify a valid glyph name.", OKButton=None)
			else:
				# determine frontmost font:
				thisFont = Glyphs.font
				if thisFont:
					# verify user input and selection:
					if not thisFont.glyphs[componentName]:
						Message(title="Component Name Error", message=u"There is no glyph called ‘%s’ in the frontmost font. Please specify a valid glyph name."%componentName, OKButton=None)
					elif not thisFont.selectedLayers:
						Message(title="Selection Error", message="No glyphs are selected. Please select a glyph and try again.", OKButton=None)
					else:
						# brings macro window to front and clears its log:
						Glyphs.clearLog()
						# Glyphs.showMacroWindow()
						
						# go through all selected glyphs:
						for thisLayer in thisFont.selectedLayers:
							thisGlyph = thisLayer.parent
							if thisGlyph:
								if thisGlyph.name == componentName:
									print("Skipping %s: cannot insert component of itself." % thisGlyph.name)
								else:
									numOfLayers = len(thisGlyph.layers)
									print("%s: adding %s as component in %i layer background%s." % (thisGlyph.name, componentName, numOfLayers, "s" if numOfLayers!=1 else ""))
									
									# go through all layers of each glyph:
									for glyphLayer in thisGlyph.layers:
										
										# delete existing background if user asked for it:
										if Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.replaceBackgrounds"]:
											glyphLayer.background.clear()
										
										# add component:
										newComponent = GSComponent(componentName)
										glyphLayer.background.components.append(newComponent)
										
										# align right if user asked for it:
										if Glyphs.defaults["com.mekkablue.PopulateAllBackgroundswithComponent.alignRight"]:
											
											# determine right edges:
											componentLayer = newComponent.componentLayer
											hShiftAmount = glyphLayer.width - componentLayer.width
											
											# layerBounds = glyphLayer.bounds
											# rightLayerEdge = layerBounds.origin.x + layerBounds.size.width
											# backgroundBounds = glyphLayer.background.bounds
											# rightBackgroundEdge = backgroundBounds.origin.x + backgroundBounds.size.width
											# hShiftAmount = rightLayerEdge - rightBackgroundEdge
											
											# move background component:
											newComponent.automaticAlignment = False
											hShift = transform( shiftX=hShiftAmount )
											hShiftMatrix = hShift.transformStruct()
											newComponent.applyTransform( hShiftMatrix )
			
			if not self.SavePreferences( self ):
				print("Note: 'Populate All Backgrounds with Component' could not write preferences.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Populate All Backgrounds with Component Error: %s" % e)
			import traceback
			print(traceback.format_exc())
	

	def alignNodeWithNodeInOtherLayer(self, thisNode, otherLayer, tolerance=5, maxTolerance=80, alreadyTaken=[]):
		while tolerance < maxTolerance:
			nearestNode = otherLayer.nodeAtPoint_excludeNodes_traversComponents_tollerance_( thisNode.position, None, False, tolerance )
			if nearestNode and (thisNode.type == nearestNode.type) and (not nearestNode.position in alreadyTaken):
				thisNode.position = nearestNode.position
				return True
			# else:
			# 	print tolerance
			# 	if nearestNode:
			# 		print "Type:", thisNode.type, nearestNode.type
			# 		print "Pos:", thisNode.position, nearestNode.position
			# 	else:
			# 		print "no Node", otherLayer.paths[0].nodes
			tolerance += 5
		return False

	def anchorWithNameFromAnchorList(self, anchorName, referenceAnchors):
		for thisAnchor in referenceAnchors:
			if thisAnchor.name == anchorName:
				return thisAnchor
		return None

	def syncAnchorPositionWithBackground( self, theseAnchorNames, thisLayer ):
		# collect background anchors
		otherAnchorDict = {}
		for otherAnchor in thisLayer.background.anchorsTraversingComponents():
			otherAnchorDict[otherAnchor.name] = otherAnchor.position
	
		# move anchors in foreground
		if not otherAnchorDict:
			print("Anchors: could not find any anchors in components.")
			return 0
		else:
			count = 0
			for thisAnchorName in theseAnchorNames:
				otherAnchorPosition = otherAnchorDict[thisAnchorName]
				if otherAnchorPosition:
					thisAnchor = thisLayer.anchors[thisAnchorName]
					thisAnchor.position = otherAnchorPosition
					count += 1
			return count
	
	def alignNodesOnLayer( self, thisLayer ):
		backgroundBackup = thisLayer.background.copy()
		for backgroundComponent in thisLayer.background.components:
			thisLayer.background.decomposeComponent_doAnchors_doHints_(backgroundComponent,False,False)
	
		alignedNodeCount = 0
		selectedNodeCount = 0
		appliedPositions = []
	
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.selected:
					selectedNodeCount += 1
					if self.alignNodeWithNodeInOtherLayer( thisNode, thisLayer.background, alreadyTaken=appliedPositions ):
						alignedNodeCount += 1
						appliedPositions.append( thisNode.position )

		thisLayer.background = backgroundBackup

		anchorsToAlign = []
		numberOfAnchorsMoved = 0
		for thisAnchor in thisLayer.anchors:
			if thisAnchor.selected:
				anchorsToAlign.append(thisAnchor.name)
		if anchorsToAlign:
			numberOfAnchorsMoved = syncAnchorPositionWithBackground( anchorsToAlign, thisLayer )
		
		return selectedNodeCount, alignedNodeCount, numberOfAnchorsMoved
	
	def AlignNodesMain(self, sender):
		thisFont = Glyphs.font # frontmost font
		selectedLayers = thisFont.selectedLayers # active layers of selected glyphs
		selection = selectedLayers[0].selection # node selection in edit mode
		Glyphs.clearLog() # clears log in Macro window

		for thisLayer in selectedLayers:
			thisGlyph = thisLayer.parent
			thisGlyph.beginUndo() # begin undo grouping
			selected, aligned, numberOfAnchorsMoved = self.alignNodesOnLayer( thisLayer )
			print("%s: aligned %i of %i selected nodes" % (thisGlyph.name, aligned, selected))
			print("%s: aligned %i of %i anchors." % (thisGlyph.name, numberOfAnchorsMoved, len(thisLayer.anchors)))
			thisGlyph.endUndo() # end undo grouping

PopulateAllBackgroundswithComponent()