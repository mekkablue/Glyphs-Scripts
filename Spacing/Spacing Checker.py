from __future__ import print_function
#MenuTitle: Spacing Checker
# -*- coding: utf-8 -*-
__doc__="""
Look for glyphs with unusual spacings and open them in a new tab.
"""

import vanilla

class SpacingChecker( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 260
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Spacing Checker", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SpacingChecker.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Find glyphs with unusual sidebearings. Open tab with glyphs where:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.asymmetricSBs = vanilla.CheckBox( (inset, linePos, -inset, 20), "LSB & RSB differ more than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.asymmetricDifference = vanilla.EditText( (inset+170, linePos, -inset-35, 19), "50", callback=self.SavePreferences, sizeStyle='small' )
		self.w.asymmetricUpdateButton = vanilla.SquareButton( (-inset-30, linePos+0.5, -inset, 18), u"↺ K", sizeStyle='small', callback=self.updateValues )
		self.w.asymmetricUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase K, presumably the largest difference in most designs.")
		linePos += lineHeight
		
		self.w.largeLSB = vanilla.CheckBox( (inset, linePos, -inset, 20), "LSBs larger than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.lsbThreshold = vanilla.EditText( (inset+110, linePos, -inset-35, 19), "70", callback=self.SavePreferences, sizeStyle='small' )
		self.w.lsbThresholdUpdateButton = vanilla.SquareButton( (-inset-30, linePos+0.5, -inset, 18), u"↺ H", sizeStyle='small', callback=self.updateValues )
		self.w.lsbThresholdUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase H, presumably the largest LSB in most designs.")
		linePos += lineHeight

		self.w.largeRSB = vanilla.CheckBox( (inset, linePos, -inset, 20), "RSBs larger than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.rsbThreshold = vanilla.EditText( (inset+110, linePos, -inset-35, 19), "70", callback=self.SavePreferences, sizeStyle='small' )
		self.w.rsbThresholdUpdateButton = vanilla.SquareButton( (-inset-30, linePos+0.5, -inset, 18), u"↺ H", sizeStyle='small', callback=self.updateValues )
		self.w.rsbThresholdUpdateButton.getNSButton().setToolTip_("Update the entry with the measurements for uppercase H, presumably the largest RSB in most designs.")
		linePos += lineHeight
		
		self.w.whiteGlyphs = vanilla.CheckBox( (inset, linePos, 180, 20), "LSB+RSB make up more than:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.whitePercentage = vanilla.EditText( (inset+180, linePos, -inset-100, 19), "50", callback=self.SavePreferences, sizeStyle='small' )
		self.w.whiteGlyphsText = vanilla.TextBox( (-inset-100, linePos+3, -inset, 14), "% of overall width", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.includeBraceAndBracketLayers = vanilla.CheckBox( (inset, linePos, -inset, 20), "Include brace and bracket layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.allMasters = vanilla.CheckBox( (inset, linePos, -inset, 20), "Look on all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ignoreNonexportingGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Ignore glyphs that do not export", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Open Tab", sizeStyle='regular', callback=self.SpacingCheckerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Spacing Checker' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def enableOrDisableRunButton(self):
		anyOptionSelected = self.w.asymmetricSBs.get() or self.w.largeLSB.get() or self.w.largeRSB.get() or self.w.whiteGlyphs.get()
		self.w.runButton.enable( anyOptionSelected )
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricSBs"] = self.w.asymmetricSBs.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricDifference"] = self.w.asymmetricDifference.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.largeLSB"] = self.w.largeLSB.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.lsbThreshold"] = self.w.lsbThreshold.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.largeRSB"] = self.w.largeRSB.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.rsbThreshold"] = self.w.rsbThreshold.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.whiteGlyphs"] = self.w.whiteGlyphs.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.whitePercentage"] = self.w.whitePercentage.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.allMasters"] = self.w.allMasters.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.includeBraceAndBracketLayers"] = self.w.includeBraceAndBracketLayers.get()
			Glyphs.defaults["com.mekkablue.SpacingChecker.ignoreNonexportingGlyphs"] = self.w.ignoreNonexportingGlyphs.get()
			
			self.enableOrDisableRunButton()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("asymmetricDifference", 90)
			Glyphs.registerDefault("asymmetricSBs", 0)
			Glyphs.registerDefault("largeLSB", 0)
			Glyphs.registerDefault("lsbThreshold", 100)
			Glyphs.registerDefault("largeRSB", 0)
			Glyphs.registerDefault("rsbThreshold", 100)
			Glyphs.registerDefault("whiteGlyphs", 0)
			Glyphs.registerDefault("whitePercentage", 10)
			Glyphs.registerDefault("allMasters", 0)
			Glyphs.registerDefault("includeBraceAndBracketLayers", 1)
			Glyphs.registerDefault("ignoreNonexportingGlyphs", 1)
			
			self.w.asymmetricDifference.set( Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricDifference"] )
			self.w.asymmetricSBs.set( Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricSBs"] )
			self.w.largeLSB.set( Glyphs.defaults["com.mekkablue.SpacingChecker.largeLSB"] )
			self.w.lsbThreshold.set( Glyphs.defaults["com.mekkablue.SpacingChecker.lsbThreshold"] )
			self.w.largeRSB.set( Glyphs.defaults["com.mekkablue.SpacingChecker.largeRSB"] )
			self.w.rsbThreshold.set( Glyphs.defaults["com.mekkablue.SpacingChecker.rsbThreshold"] )
			self.w.whiteGlyphs.set( Glyphs.defaults["com.mekkablue.SpacingChecker.whiteGlyphs"] )
			self.w.whitePercentage.set( Glyphs.defaults["com.mekkablue.SpacingChecker.whitePercentage"] )
			self.w.allMasters.set( Glyphs.defaults["com.mekkablue.SpacingChecker.allMasters"] )
			self.w.includeBraceAndBracketLayers.set( Glyphs.defaults["com.mekkablue.SpacingChecker.includeBraceAndBracketLayers"] )
			self.w.ignoreNonexportingGlyphs.set( Glyphs.defaults["com.mekkablue.SpacingChecker.ignoreNonexportingGlyphs"] )
			
			self.enableOrDisableRunButton()
		except:
			return False
			
		return True
	
	def updateValues(self, sender):
		updatedValue = 0.0 # fallback value
		
		thisFont = Glyphs.font
		if thisFont:
			thisMaster = thisFont.selectedFontMaster
			uppercaseK = thisFont.glyphs["K"]
			uppercaseH = thisFont.glyphs["H"]
			
			if sender == self.w.asymmetricUpdateButton:
				if uppercaseK:
					referenceLayer = uppercaseK.layers[thisMaster.id]
					updatedValue = abs(referenceLayer.LSB - referenceLayer.RSB)
				self.w.asymmetricDifference.set( updatedValue )
			
			if sender == self.w.lsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.LSB
				self.w.lsbThreshold.set( updatedValue )
			
			if sender == self.w.rsbThresholdUpdateButton:
				if uppercaseH:
					referenceLayer = uppercaseH.layers[thisMaster.id]
					updatedValue = referenceLayer.RSB
				self.w.rsbThreshold.set( updatedValue )
			
		self.SavePreferences(sender)
	
	def isLayerAffected(self, thisLayer):
		try:
			if Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricSBs"]:
				try:
					asymmetricDifference = float(Glyphs.defaults["com.mekkablue.SpacingChecker.asymmetricDifference"])
					if abs(thisLayer.LSB-thisLayer.RSB) > asymmetricDifference:
						return True
				except Exception as e:
					raise e
				
			if Glyphs.defaults["com.mekkablue.SpacingChecker.largeLSB"]:
				try:
					lsbThreshold = float(Glyphs.defaults["com.mekkablue.SpacingChecker.lsbThreshold"])
					if thisLayer.LSB > lsbThreshold:
						return True
				except Exception as e:
					raise e
				
			if Glyphs.defaults["com.mekkablue.SpacingChecker.largeRSB"]:
				try:
					rsbThreshold = float(Glyphs.defaults["com.mekkablue.SpacingChecker.rsbThreshold"])
					if thisLayer.RSB > rsbThreshold:
						return True
				except Exception as e:
					raise e
				
			if Glyphs.defaults["com.mekkablue.SpacingChecker.whiteGlyphs"]:
				try:
					if not thisLayer.width > 0.0:
						return False
					else:
						whitePercentage = float(Glyphs.defaults["com.mekkablue.SpacingChecker.whitePercentage"])
						lsb = max(0.0, thisLayer.LSB)
						rsb = max(0.0, thisLayer.RSB)
						percentage = (lsb+rsb)/thisLayer.width
						if percentage > whitePercentage:
							return True
				except Exception as e:
					raise e
			
			return False
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Spacing Checker Error while checking glyph '%s', layer '%s':\n%s" % (thisLayer.parent,thisLayer.name,e))
			import traceback
			print(traceback.format_exc())

	def SpacingCheckerMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			print("Space Checker Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			collectedLayers = []
			braceAndBracketIncluded = Glyphs.defaults["com.mekkablue.SpacingChecker.includeBraceAndBracketLayers"]
			if Glyphs.defaults["com.mekkablue.SpacingChecker.allMasters"]:
				mastersToCheck = thisFont.masters
				print("Searching %i masters..." % len(mastersToCheck))
			else:
				currentMaster = thisFont.selectedFontMaster
				mastersToCheck = (currentMaster,)
				print("Searching master: %s" % currentMaster.name)
				
			print()
			
			ignoreNonexportingGlyphs = Glyphs.defaults["com.mekkablue.SpacingChecker.ignoreNonexportingGlyphs"]
			
			numOfGlyphs = len(thisFont.glyphs)
			for index,thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set( int(100*(float(index)/numOfGlyphs)) )
				if thisGlyph.export or not ignoreNonexportingGlyphs:
					for thisLayer in thisGlyph.layers:
						layerMaster = thisLayer.associatedFontMaster()
						if thisLayer.name and layerMaster in mastersToCheck:
							isMasterLayer = layerMaster.id == thisLayer.layerId
							if isMasterLayer or (braceAndBracketIncluded and thisLayer.isSpecialLayer):
								if self.isLayerAffected(thisLayer):
									collectedLayers.append(thisLayer)
			
			if not collectedLayers:
				Message(title="No Affected Glyphs Found", message="No glyphs found that fulfil the chosen criteria.", OKButton=u"🙌 High Five!")
			else:
				if Glyphs.defaults["com.mekkablue.SpacingChecker.allMasters"]:
					newTab = thisFont.newTab()
					newTab.layers = collectedLayers
				else:
					# enable Cmd+1,2,3,...:
					glyphNames = [l.parent.name for l in collectedLayers]
					tabText = "/" + "/".join(glyphNames)
					thisFont.newTab(tabText)
			if not self.SavePreferences( self ):
				print("Note: 'Spacing Checker' could not write preferences.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Spacing Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SpacingChecker()