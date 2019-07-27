#MenuTitle: Garbage Collection
# -*- coding: utf-8 -*-
__doc__="""
Removes annotations, glyph notes, guides, and node names.
"""

import vanilla

class GarbageCollection( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 270
		windowWidthResize  = 50 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Garbage Collection", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.GarbageCollection.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*1.8), u"Removes the following items from the glyphs in the frontmost font:", sizeStyle='small', selectable=True )
		linePos += 1.8*lineHeight
		
		self.w.removeNodeNames = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all node names 🔥❌ in font", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeNodeNames.getNSButton().setToolTip_(u"Deletes node markers, as employed by many schriftlabor scripts to mark problematic spots.")
		linePos += lineHeight
		
		self.w.removeAnnotations = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all annotations in font", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeAnnotations.getNSButton().setToolTip_(u"Deletes annotations created with the Annotation Tool (A), e.g. circles, arrows, and texts.")
		linePos += lineHeight
		
		self.w.removeLocalGuides = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all local (blue) guides in font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeLocalGuides.getNSButton().setToolTip_("Deletes blue guides.")
		linePos += lineHeight
		
		self.w.removeGlobalGuides = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all global (red) guides in font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeGlobalGuides.getNSButton().setToolTip_("Deletes red guides.")
		linePos += lineHeight
		
		self.w.removeGlyphNotes = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all glyph notes in font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeGlyphNotes.getNSButton().setToolTip_("Deletes glyph notes as entered in list view or through the Glyph Note Palette (plug-in).")
		linePos += lineHeight
		
		self.w.currentMasterOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Limit clean-up to current master only", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.currentMasterOnly.getNSButton().setToolTip_("If checked, applies the clean-up to layers of the current font master only. Exception: glyph notes are not master-specific.")
		linePos += lineHeight
		
		self.w.selectedGlyphsOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Limit clean-up to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("If checked, applies the clean-up only to selected glyphs. Otherwise, to all glyphs in the font.")
		linePos += lineHeight
		
		self.guiUpdate()
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Clean", sizeStyle='regular', callback=self.GarbageCollectionMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Garbage Collection' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def guiUpdate(self, sender=None):
		if Glyphs.defaults["com.mekkablue.GarbageCollection.currentMasterOnly"]:
			self.w.removeNodeNames.setTitle(u"Remove all node names 🔥❌ in current master")
			self.w.removeAnnotations.setTitle(u"Remove all annotations in current master")
			self.w.removeLocalGuides.setTitle(u"Remove all local (blue) guides in current master")
			self.w.removeGlobalGuides.setTitle(u"Remove all global (red) guides in current master")
		else:
			self.w.removeNodeNames.setTitle(u"Remove all node names 🔥❌ in font")
			self.w.removeAnnotations.setTitle(u"Remove all annotations in font")
			self.w.removeLocalGuides.setTitle(u"Remove all local (blue) guides in font")
			self.w.removeGlobalGuides.setTitle(u"Remove all global (red) guides in font")
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.GarbageCollection.removeNodeNames"] = self.w.removeNodeNames.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.removeLocalGuides"] = self.w.removeLocalGuides.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlobalGuides"] = self.w.removeGlobalGuides.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.removeAnnotations"] = self.w.removeAnnotations.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlyphNotes"] = self.w.removeGlyphNotes.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.currentMasterOnly"] = self.w.currentMasterOnly.get()
			Glyphs.defaults["com.mekkablue.GarbageCollection.selectedGlyphsOnly"] = self.w.selectedGlyphsOnly.get()
			
			self.guiUpdate(sender=sender)
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.removeNodeNames", 1)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.removeLocalGuides", 0)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.removeGlobalGuides", 0)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.removeAnnotations", 1)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.removeGlyphNotes", 0)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.currentMasterOnly", 0)
			Glyphs.registerDefault("com.mekkablue.GarbageCollection.selectedGlyphsOnly", 0)
			self.w.removeNodeNames.set( Glyphs.defaults["com.mekkablue.GarbageCollection.removeNodeNames"] )
			self.w.removeLocalGuides.set( Glyphs.defaults["com.mekkablue.GarbageCollection.removeLocalGuides"] )
			self.w.removeGlobalGuides.set( Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlobalGuides"] )
			self.w.removeAnnotations.set( Glyphs.defaults["com.mekkablue.GarbageCollection.removeAnnotations"] )
			self.w.removeGlyphNotes.set( Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlyphNotes"] )
			self.w.currentMasterOnly.set( Glyphs.defaults["com.mekkablue.GarbageCollection.currentMasterOnly"] )
			self.w.selectedGlyphsOnly.set( Glyphs.defaults["com.mekkablue.GarbageCollection.selectedGlyphsOnly"] )
			
			self.guiUpdate(sender=sender)
		except:
			return False
			
		return True

	def GarbageCollectionMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print "Note: 'Garbage Collection' could not write preferences."
			
			thisFont = Glyphs.font # frontmost font
			print "Garbage Collection Report for %s" % thisFont.familyName
			print thisFont.filepath
			print
			
			if Glyphs.defaults["com.mekkablue.GarbageCollection.selectedGlyphsOnly"]:
				glyphs = [l.parent for l in thisFont.selectedLayers]
			else:
				glyphs = thisFont.glyphs
			
			# font counters:
			removeNodeNamesFont = 0
			localGuidesFont = 0
			removeAnnotationsFont = 0
			
			for thisGlyph in glyphs:
				# glyph counters:
				removeNodeNamesGlyph = 0
				localGuidesGlyph = 0
				removeAnnotationsGlyph = 0
				
				print u"🔠 Cleaning %s ..." % thisGlyph.name
				for thisLayer in thisGlyph.layers:
					if thisLayer.master == thisFont.selectedFontMaster or not Glyphs.defaults["com.mekkablue.GarbageCollection.currentMasterOnly"]:
						if Glyphs.defaults["com.mekkablue.GarbageCollection.removeNodeNames"]:
							for thisPath in thisLayer.paths:
								for thisNode in thisPath.nodes:
									if thisNode.name:
										removeNodeNamesGlyph += 1
										thisNode.name = None
						if Glyphs.defaults["com.mekkablue.GarbageCollection.removeLocalGuides"]:
							localGuidesGlyph += len(thisLayer.guideLines)
							thisLayer.guideLines = None
						if Glyphs.defaults["com.mekkablue.GarbageCollection.removeAnnotations"]:
							removeAnnotationsGlyph += len(thisLayer.annotations)
							thisLayer.annotations = None
				if Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlyphNotes"]:
					if thisGlyph.note:
						print "  glyph note"
						thisGlyph.note = None
				
				# report:
				if removeNodeNamesGlyph:
					print "  %i node names" % removeNodeNamesGlyph
					removeNodeNamesFont += removeNodeNamesGlyph
				if localGuidesGlyph:
					print "  %i local guides" % localGuidesGlyph
					localGuidesFont += localGuidesGlyph
				if removeAnnotationsGlyph:
					print "  %i annotations" % removeAnnotationsGlyph
					removeAnnotationsFont += removeAnnotationsGlyph
					
				

			if Glyphs.defaults["com.mekkablue.GarbageCollection.removeGlobalGuides"]:
				print u"📏 Removing global guides ..."
				for thisMaster in thisFont.masters:
					if thisMaster == thisFont.selectedFontMaster or not Glyphs.defaults["com.mekkablue.GarbageCollection.currentMasterOnly"]:
						thisMaster.guideLines = None
			
			print u"✅ Done."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Garbage Collection Error: %s" % e
			import traceback
			print traceback.format_exc()

GarbageCollection()