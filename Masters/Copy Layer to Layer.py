#MenuTitle: Copy Layer to Layer
# -*- coding: utf-8 -*-
__doc__="""
Copies one master to another master's or background in selected glyphs.
"""

import GlyphsApp
import vanilla
import math

def getComponentScaleX_scaleY_rotation( thisComponent ):
		a = thisComponent.transform[0]
		b = thisComponent.transform[1]
		c = thisComponent.transform[2]
		d = thisComponent.transform[3]

		scale_x = math.sqrt(math.pow(a,2)+math.pow(b,2))
		scale_y = math.sqrt(math.pow(c,2)+math.pow(d,2))
		if (b<0 and c<0):
			scale_y = scale_y * -1

		rotation = math.atan2(b, a) * (180/math.pi)

		return [scale_x, scale_y, rotation]


class CopyLayerToLayer( object ):

	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 280
		windowHeight = 220
		windowWidthResize  = 120 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Copy layer to layer", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CopyLayerToLayer.mainwindow" # stores last window position and size
		)

		self.w.text_1 = vanilla.TextBox((15, 12+2, 120, 14), "Copy paths from", sizeStyle='small')
		self.w.fontSource = vanilla.PopUpButton((120, 12, -15, 17), self.GetFontNames(), sizeStyle='small', callback=self.FontChangeCallback)
		self.w.masterSource = vanilla.PopUpButton((120, 12+20, -15, 17), self.GetMasterNames("source"), sizeStyle='small', callback=self.MasterChangeCallback)

		self.w.text_2 = vanilla.TextBox((15, 56+2, 120, 14), "into selection of", sizeStyle='small')
		self.w.fontTarget = vanilla.PopUpButton((120, 56, -15, 17), self.GetFontNames(), sizeStyle='small', callback=self.FontChangeCallback)
		self.w.masterTarget = vanilla.PopUpButton((120, 56+20, -15, 17), self.GetMasterNames("target"), sizeStyle='small', callback=self.MasterChangeCallback)

		self.w.includePaths = vanilla.CheckBox((15+150+15, 100+2, 160, 20), "Include paths", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.includeComponents = vanilla.CheckBox((15, 100+2, 160, 20), "Include components", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.includeAnchors = vanilla.CheckBox((15, 100+20, -100, 20), "Include anchors", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.includeMetrics = vanilla.CheckBox((15, 100+38, -100, 20), "Include metrics", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.keepWindowOpen = vanilla.CheckBox((15, 100+56, -100, 20), "Keep window open", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.copyBackground = vanilla.CheckBox((15, 100+74, -100, 20), "Background instead", sizeStyle='small', callback=self.SavePreferences, value=False)

		self.w.copybutton = vanilla.Button((-80, -30, -15, -10), "Copy", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.copybutton )

		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Copy Layer to Layer' could not load preferences. Will resort to defaults."

		self.w.open()
		self.w.makeKey()
		self.w.masterTarget.set(1)

	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includePaths"] = self.w.includePaths.get()
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeComponents"] = self.w.includeComponents.get()
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeAnchors"] = self.w.includeAnchors.get()
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeMetrics"] = self.w.includeMetrics.get()
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.keepWindowOpen"] = self.w.keepWindowOpen.get()
			Glyphs.defaults["com.mekkablue.CopyLayerToLayer.copyBackground"] = self.w.copyBackground.get()
		except:
			return False

		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.CopyLayerToLayer.includePaths" : "1",
					"com.mekkablue.CopyLayerToLayer.includeComponents" : "1",
					"com.mekkablue.CopyLayerToLayer.includeAnchors" : "1",
					"com.mekkablue.CopyLayerToLayer.includeMetrics" : "1",
					"com.mekkablue.CopyLayerToLayer.keepWindowOpen" : "1",
					"com.mekkablue.CopyLayerToLayer.copyBackground" : "0"
				}
			)
			self.w.includePaths.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includePaths"] )
			self.w.includeComponents.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeComponents"] )
			self.w.includeAnchors.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeAnchors"] )
			self.w.includeMetrics.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.includeMetrics"] )
			self.w.keepWindowOpen.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.keepWindowOpen"] )
			self.w.copyBackground.set( Glyphs.defaults["com.mekkablue.CopyLayerToLayer.copyBackground"] )
		except:
			return False

		return True

	def GetFontNames( self ):
		"""Collects names of Open Fonts to populate the menus in the GUI."""
		myFontList = []
		# The active font is at index=0, so the default selection should be the active font.
		for fontIndex in range( len( Glyphs.fonts ) ):
			thisFont = Glyphs.fonts[fontIndex]
			myFontList.append( '%i: %s' % (fontIndex, thisFont.familyName) )
		return myFontList

	def GetMasterNames( self, font ):
		"""Collects names of masters to populate the submenus in the GUI."""
		if font == "target":
			fontIndex = self.w.fontTarget.get()
		else:
			fontIndex = self.w.fontSource.get()

		thisFont = Glyphs.fonts[fontIndex]
		myMasterList = []
		for masterIndex in range( len( thisFont.masters ) ):
			thisMaster = thisFont.masters[masterIndex]
			myMasterList.append( '%i: %s' % (masterIndex, thisMaster.name) )
		return myMasterList

	def ValidateInput( self, sender ):
		"""Disables the button if source and target are the same."""
		if self.w.fontSource.get() == self.w.fontTarget.get() and self.w.masterSource.get() == self.w.masterTarget.get():
			self.w.copybutton.enable( False )
		else:
			self.w.copybutton.enable( True )

	def MasterChangeCallback( self, sender ):
		"""Just call ValidateInput."""
		self.ValidateInput(None)

	def FontChangeCallback( self, sender ):
		"""Update masters menus when font input changes."""
		if sender == self.w.fontSource:
			# Refresh source
			self.w.masterSource.setItems(self.GetMasterNames("source"))
		else:
			# Refresh target
			self.w.masterTarget.setItems(self.GetMasterNames("target"))
		self.ValidateInput(None)

	def copyPathsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all paths from sourceLayer to targetLayer"""
		numberOfPathsInSource  = len( sourceLayer.paths )
		numberOfPathsInTarget  = len( targetLayer.paths )

		if numberOfPathsInTarget != 0:
			print "- Deleting %i paths in target layer" % numberOfPathsInTarget
			targetLayer.paths = []

		if numberOfPathsInSource > 0:
			print "- Copying paths"
			for thisPath in sourceLayer.paths:
				newPath = thisPath.copy()
				targetLayer.paths.append( newPath )
				
	def copyHintsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all hints, corner and cap components from one layer to the next."""
		numberOfHintsInSource = len( sourceLayer.hints )
		numberOfHintsInTarget  = len( targetLayer.hints )

		if numberOfHintsInTarget != 0:
			print "- Deleting %i hints, caps and corners in target layer" % numberOfHintsInTarget
			targetLayer.hints = []

		if numberOfHintsInSource > 0:
			print "- Copying hints, caps and corners"
			for thisHint in sourceLayer.hints:
				newHint = thisHint.copy()
				targetLayer.hints.append( newHint )

	def copyComponentsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all components from sourceLayer to targetLayer."""
		numberOfComponentsInSource = len( sourceLayer.components )
		numberOfComponentsInTarget = len( targetLayer.components )

		if numberOfComponentsInTarget != 0:
			print "- Deleting %i components in target layer" % numberOfComponentsInTarget
			targetLayer.components = []

		if numberOfComponentsInSource > 0:
			print "- Copying components:"
			for thisComp in sourceLayer.components:
				newComp = thisComp.copy()
				print "   Component: %s" % ( thisComp.componentName )
				targetLayer.components.append( newComp )

	def copyAnchorsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all anchors from sourceLayer to targetLayer."""
		numberOfAnchorsInSource = len( sourceLayer.anchors )
		numberOfAnchorsInTarget = len( targetLayer.anchors )

		if numberOfAnchorsInTarget != 0:
			print "- Deleting %i anchors in target layer" % numberOfAnchorsInTarget
			targetLayer.setAnchors_(None)

		if numberOfAnchorsInSource > 0:
			print "- Copying anchors from source layer:"
			for thisAnchor in sourceLayer.anchors:
				newAnchor = thisAnchor.copy()
				targetLayer.anchors.append( newAnchor )
				print "   %s (%i, %i)" % ( thisAnchor.name, thisAnchor.position.x, thisAnchor.position.y )

	def copyMetricsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies width of sourceLayer to targetLayer."""
		sourceWidth = sourceLayer.width
		if targetLayer.width != sourceWidth:
			targetLayer.width = sourceWidth
			print "- Copying width (%.1f)" % sourceWidth
		else:
			print "- Width not changed (already was %.1f)" % sourceWidth

	def buttonCallback( self, sender ):
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print "Copy Layer to Layer Protocol:"

		# This should be the active selection, not necessarily the selection on the inputted fonts
		Font = Layer.parent.parent
		selectedGlyphs = [ x.parent for x in Font.selectedLayers ]
		indexOfSourceFont = self.w.fontSource.get()
		indexOfTargetFont = self.w.fontTarget.get()
		indexOfSourceMaster = self.w.masterSource.get()
		indexOfTargetMaster = self.w.masterTarget.get()
		pathsYesOrNo  = self.w.includePaths.get()
		componentsYesOrNo  = self.w.includeComponents.get()
		anchorsYesOrNo  = self.w.includeAnchors.get()
		metricsYesOrNo  = self.w.includeMetrics.get()
		copyBackground = self.w.copyBackground.get()

		for thisGlyph in selectedGlyphs:
			try:
				print "\nProcessing %s..." % thisGlyph.name
				sourceFont = Glyphs.fonts[ indexOfSourceFont ]
				sourceGlyph = sourceFont.glyphs[ thisGlyph.name ]
				sourcelayer = sourceGlyph.layers[ indexOfSourceMaster ]

				targetFont = Glyphs.fonts[ indexOfTargetFont ]
				targetGlyph = targetFont.glyphs[ thisGlyph.name ]
				if copyBackground == 1:
					targetlayer = targetGlyph.layers[ indexOfTargetMaster ].background
				else:
					targetlayer = targetGlyph.layers[ indexOfTargetMaster ]

				sourceFont.disableUpdateInterface()
				targetFont.disableUpdateInterface()

				# Copy paths, components, anchors, and metrics:
				if pathsYesOrNo:
					self.copyPathsFromLayerToLayer( sourcelayer, targetlayer )
				if componentsYesOrNo:
					self.copyComponentsFromLayerToLayer( sourcelayer, targetlayer )
				if anchorsYesOrNo:
					self.copyAnchorsFromLayerToLayer( sourcelayer, targetlayer )
				if metricsYesOrNo and not copyBackground:
					self.copyMetricsFromLayerToLayer( sourcelayer, targetlayer )
				
				# copy hints, caps and corners if either paths or components are copied:
				if componentsYesOrNo or pathsYesOrNo:
					self.copyHintsFromLayerToLayer( sourcelayer, targetlayer )

				sourceFont.enableUpdateInterface()
				targetFont.enableUpdateInterface()

			except Exception, e:
				print e

		if not self.w.keepWindowOpen.get():
			self.w.close()

CopyLayerToLayer()
