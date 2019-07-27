#MenuTitle: Alignment Manager
# -*- coding: utf-8 -*-
__doc__="""
Manage Automatic Alignment for (multiple) selected glyphs.
"""

import vanilla

class AutoAlignmentManager( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 160
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Alignment Manager", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AutoAlignmentManager.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Manage component alignment in selected glyphs:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.includeAllGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include all glyphs, i.e., ignore glyph selection", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllGlyphs.getNSButton().setToolTip_("No matter what your glyph selection is, will enable/disable component alignment for ALL glyphs in the font.")
		linePos += lineHeight
		
		self.w.includeAllLayers = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include all masters and special layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllLayers.getNSButton().setToolTip_("If enabled, will enable/disable automatic alignment not only for the currently selected masters/layers, but for ALL master layers, brace layers and bracket layers of selected glyphs. Will still ignore backup layers (the ones with a timestamp in their names).")
		linePos += lineHeight
		
		self.w.ignoreFirstComponent = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Ignore first component", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreFirstComponent.getNSButton().setToolTip_("If enabled, will exclude the first component (usually the base letter) from toggling auto-alignment. This can be useful if you want to keep the diacritic marks aligned to the base, but still move the base. Or if you want to keep the base letter aligned, and place the marks freely.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.enableButton = vanilla.Button( (-110-inset, -20-inset, -inset, -inset), u"✅ Enable", sizeStyle='regular', callback=self.AutoAlignmentManagerMain )
		self.w.disableButton = vanilla.Button( (-230-inset, -20-inset, -120-inset, -inset), u"🚫 Disable", sizeStyle='regular', callback=self.AutoAlignmentManagerMain )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Auto Alignment Manager' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllGlyphs"] = self.w.includeAllGlyphs.get()
			Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllLayers"] = self.w.includeAllLayers.get()
			Glyphs.defaults["com.mekkablue.AutoAlignmentManager.ignoreFirstComponent"] = self.w.ignoreFirstComponent.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.AutoAlignmentManager.includeAllGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.AutoAlignmentManager.includeAllLayers", 1)
			Glyphs.registerDefault("com.mekkablue.AutoAlignmentManager.ignoreFirstComponent", 0)
			self.w.includeAllGlyphs.set( Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllGlyphs"] )
			self.w.includeAllLayers.set( Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllLayers"] )
			self.w.ignoreFirstComponent.set( Glyphs.defaults["com.mekkablue.AutoAlignmentManager.ignoreFirstComponent"] )
		except:
			return False
			
		return True
	
	def enableOrDisableLayer( self, thisLayer, excludeFirstComponent=False, sender=None ):
		if thisLayer.components:
			for i,thisComponent in enumerate(thisLayer.components):
				if (i>0) or (not excludeFirstComponent):
					print i
					if sender is self.w.enableButton:
						thisComponent.setDisableAlignment_(False)
						print "\tEnabling alignment on: %s" % thisLayer.name
					elif sender is self.w.disableButton:
						thisComponent.setDisableAlignment_(True)
						print "\tDisabling alignment on: %s" % thisLayer.name
					else:
						return False
		return True
	
	def AutoAlignmentManagerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print "Note: 'Auto Alignment Manager' could not write preferences."
			
			thisFont = Glyphs.font # frontmost font
			Glyphs.clearLog()
			print "Auto Alignment Manager Report for %s" % thisFont.familyName
			print thisFont.filepath
			print
			
			

			includeAllLayers = Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllLayers"]
			excludeFirstComponent = Glyphs.defaults["com.mekkablue.AutoAlignmentManager.ignoreFirstComponent"]
			currentMasterID = thisFont.selectedFontMaster.id
			
			if includeAllLayers:
				if Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllGlyphs"]:
					selectedGlyphs = thisFont.glyphs
				else:
					selectedGlyphs = [l.parent for l in thisFont.selectedLayers]
					
				for thisGlyph in selectedGlyphs:
					print "Processing: %s" % thisGlyph.name
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							if not self.enableOrDisableLayer( thisLayer, excludeFirstComponent=excludeFirstComponent, sender=sender ):
								print u"⚠️ Error setting alignment."
			else:
				if Glyphs.defaults["com.mekkablue.AutoAlignmentManager.includeAllGlyphs"]:
					layersToBeProcessed = [g.layers[currentMasterID] for g in thisFont.glyphs]
				else:
					# just the visible layer selection (may be non-master, non-special layer too):
					layersToBeProcessed = thisFont.selectedLayers
				
				for thisLayer in layersToBeProcessed:
					print "Processing: %s" % thisLayer.parent.name
					if not self.enableOrDisableLayer( thisLayer, excludeFirstComponent=excludeFirstComponent, sender=sender ):
						print u"⚠️ Error setting alignment."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Auto Alignment Manager Error: %s" % e
			import traceback
			print traceback.format_exc()

AutoAlignmentManager()