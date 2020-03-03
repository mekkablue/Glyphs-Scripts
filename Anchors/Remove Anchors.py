#MenuTitle: Remove Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Delete anchors from selected glyphs, or whole font.
"""

import vanilla
allAnchors = "All Anchors"

class AnchorDeleter( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 130
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove Anchors", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AnchorDeleter.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 13, 20
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 80, 14), "Delete anchor", sizeStyle='small' )
		self.w.updateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), u"⟲", sizeStyle='small', callback=self.updateAnchors )
		self.w.updateButton.getNSButton().setToolTip_(u"Scans frontmost font for all available anchors, and updates the pop-up list accordingly. Good idea to do this for every new font you want to process.")
		self.w.anchorPopup = vanilla.PopUpButton( (inset+80, linePos, -inset-25, 17), self.updateAnchors(None), callback=self.SavePreferences, sizeStyle='small' )
		self.w.anchorPopup.getNSPopUpButton().setToolTip_(u"Choose an anchor you want to delete, or choose ‘All Anchors’. Remember to update the list for the current font with the ⟲ update button on the right.")
		linePos += lineHeight
		
		self.w.selectedGlyphsOnly = vanilla.CheckBox( (inset, linePos, -inset, 20), "In selected glyphs only (otherwise all glyphs)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_(u"If checked, the chosen anchor will be deleted in the current glyph selection only. If unchecked, they will be deleted in all glyphs.")
		linePos += lineHeight
		
		self.w.currentMasterOnly = vanilla.CheckBox( (inset, linePos, -inset, 20), u"In current master only (otherwise all masters)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.currentMasterOnly.getNSButton().setToolTip_(u"If checked, will remove anchor only in layers associated with the currently selected font master. If unchecked, in all layers.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.AnchorDeleterMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Delete Anchors' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] = self.w.anchorPopup.get()
			Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedGlyphsOnly"] = self.w.selectedGlyphsOnly.get()
			Glyphs.defaults["com.mekkablue.AnchorDeleter.currentMasterOnly"] = self.w.currentMasterOnly.get()
		except:
			return False
			
		return True

	def LoadPreferences( self, sender=None ):
		try:
			Glyphs.registerDefault("com.mekkablue.AnchorDeleter.anchorPopup", 0)
			Glyphs.registerDefault("com.mekkablue.AnchorDeleter.selectedGlyphsOnly", 0)
			Glyphs.registerDefault("com.mekkablue.AnchorDeleter.currentMasterOnly", 0)
			if self.w.anchorPopup.get() < len(self.w.anchorPopup.getItems()):
				self.w.anchorPopup.set( Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] )
			else:
				self.w.anchorPopup.set( 0 )
			self.w.selectedGlyphsOnly.set( Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedGlyphsOnly"] )
		except:
			return False
			
		return True
	
	def updateAnchors(self, sender):
		collectedAnchorNames = []
		thisFont = Glyphs.font # frontmost font
		if Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedGlyphsOnly"]:
			glyphs = [l.parent for l in thisFont.selectedLayers]
		else:
			glyphs = thisFont.glyphs
		for thisGlyph in glyphs:
			for thisLayer in thisGlyph.layers:
				for thisAnchor in thisLayer.anchors:
					collectedAnchorNames.append( thisAnchor.name )
		uniqueAnchorNames = set(collectedAnchorNames)
		sortedAnchorNames = sorted(list(uniqueAnchorNames)) + [allAnchors]
		try:
			if not Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] < len(uniqueAnchorNames):
				Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"] = 0
			else:
				self.SavePreferences()
		except:
			pass # exit gracefully
		
		if sender == self.w.updateButton:
			self.w.anchorPopup.setItems(sortedAnchorNames)
		else:
			return sortedAnchorNames

	def AnchorDeleterMain( self, sender=None ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Remove Anchors' could not write preferences.")
			
			Glyphs.clearLog()
			thisFont = Glyphs.font # frontmost font
			print("Report for %s:" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
				print()
			
			anchorPopupIndex = Glyphs.defaults["com.mekkablue.AnchorDeleter.anchorPopup"]
			anchorsInPopup = self.w.anchorPopup.getItems()
			anchorName = anchorsInPopup[anchorPopupIndex]
			selectedGlyphsOnly = Glyphs.defaults["com.mekkablue.AnchorDeleter.selectedGlyphsOnly"]
			
			print(
				"Deleting %s %s:\n" % (
					anchorName.lower() if anchorName==allAnchors else anchorName,
					"in selected glyphs" if selectedGlyphsOnly else "throughout the font",
				))
			
			if not anchorName:
				errorMsg = "⚠️ Could not determine selected anchor name. Reset the list, make a new choice, and try again, please."
				print(errorMsg)
				Message(title="Remove Anchors Error", message=errorMsg, OKButton=None)
			else:
				currentMasterOnly = Glyphs.defaults["com.mekkablue.AnchorDeleter.currentMasterOnly"]
				currentMaster = thisFont.selectedFontMaster

				if selectedGlyphsOnly:
					glyphs = [l.parent for l in thisFont.selectedLayers]
				else:
					glyphs = thisFont.glyphs
				
				totalAnchorCount = 0
				for thisGlyph in glyphs:
					layerCount = 0
					deletedAnchorCount = 0
					for thisLayer in thisGlyph.layers:
						if (not currentMasterOnly) or (thisLayer.associatedFontMaster==currentMaster):
							layerCount += 1
							if anchorName==allAnchors:
								deletedAnchorCount += len(thisLayer.anchors)
								thisLayer.anchors = None
							else:
								if thisLayer.anchors[anchorName]:
									deletedAnchorCount += 1
									del thisLayer.anchors[anchorName]
					
					# report:
					print("🅰️ %s: deleted %i anchor%s on %i layer%s" % (
						thisGlyph.name,
						deletedAnchorCount,
						"" if deletedAnchorCount==1 else "s",
						layerCount,
						"" if layerCount==1 else "s",
						))
					
					# statistics:
					totalAnchorCount += deletedAnchorCount
				
				# final report
				msg="Deleted %i anchor%s in %i glyph%s." % (
					totalAnchorCount,
					"" if totalAnchorCount==1 else "s",
					len(glyphs),
					"" if len(glyphs)==1 else "s",
				)
				print("\n🔠 %s Done."%msg)
				Message(title="Anchors Removed", message="%s Detailed report in Macro Window."%msg, OKButton=None)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Anchor Deleter Error: %s" % e)
			import traceback
			print(traceback.format_exc())

AnchorDeleter()