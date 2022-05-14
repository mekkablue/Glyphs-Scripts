#MenuTitle: Garbage Collection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes annotations, glyph notes, guides, and node names.
"""

import vanilla

class GarbageCollection( object ):
	prefID = "com.mekkablue.GarbageCollection"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 310
		windowHeight = 380
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
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*1.8), u"Removes the following items from the glyphs in the frontmost font:", sizeStyle='small', selectable=True )
		linePos += 1.8*lineHeight
		
		self.w.removeNodeNames = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all node names 🔥❌👌🏻 in font", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeNodeNames.getNSButton().setToolTip_(u"Deletes node markers, as employed by many mekkablue scripts to mark problematic spots.")
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
		
		self.w.removeColors = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Remove all glyph and layer colors in font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.removeColors.getNSButton().setToolTip_("Resets all glyph and layer colors to none.")
		linePos += lineHeight
		
		self.w.line1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 6
		
		self.w.currentMasterOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Limit clean-up to current master only", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.currentMasterOnly.getNSButton().setToolTip_("If checked, applies the clean-up to layers of the current font master only. Exception: glyph notes are not master-specific.")
		linePos += lineHeight
		
		self.w.selectedGlyphsOnly = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Limit clean-up to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("If checked, applies the clean-up only to selected glyphs. Otherwise, to all glyphs in the font.")
		linePos += lineHeight
		
		self.w.line2 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 6
		
		self.w.userDataText = vanilla.TextBox( (inset, linePos+2, 115, 14), "Remove userData in", sizeStyle='small', selectable=True )
		self.w.userDataFont = vanilla.CheckBox( (inset+115, linePos-1, 43, 20), "font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.userDataMasters = vanilla.CheckBox( (inset+115+43, linePos-1, 63, 20), "masters", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.userDataInstances = vanilla.CheckBox( (inset+115+43+63, linePos-1, 75, 20), "instances", value=False, callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Remove userData from the frontmost font, its masters, and/or instances. Attention: will NOT respect the ‘Limit’ settings above."
		self.w.userDataText.getNSTextField().setToolTip_(tooltip)
		self.w.userDataFont.getNSButton().setToolTip_(tooltip)
		self.w.userDataMasters.getNSButton().setToolTip_(tooltip)
		self.w.userDataInstances.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight
		
		self.w.userDataGlyphs = vanilla.CheckBox( (inset+115, linePos-1, 58, 20), "glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.userDataLayers = vanilla.CheckBox( (inset+115+58, linePos-1, -inset, 20), "layers", value=False, callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Remove userData from glyphs and/or layers. Will respect the ‘Limit’ settings above."
		self.w.userDataGlyphs.getNSButton().setToolTip_(tooltip)
		self.w.userDataLayers.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight
		
		self.w.userDataKeysText = vanilla.TextBox( (inset, linePos+3, 92, 14), "…only keys with:", sizeStyle='small', selectable=True )
		self.w.userDataKeys = vanilla.EditText( (inset+92, linePos, -inset, 19), "UFO, fontlab, public", callback=self.SavePreferences, sizeStyle='small' )
		tooltip = "Comma-separated list of search strings for userData keys to delete. Leave empty to remove all."
		self.w.userDataKeysText.getNSTextField().setToolTip_(tooltip)
		self.w.userDataKeys.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight+3
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		self.w.statusText = vanilla.TextBox( (inset, -17-inset, -80-inset, 14), u"", sizeStyle='small', selectable=False )
		
		self.guiUpdate()
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Clean", sizeStyle='regular', callback=self.GarbageCollectionMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print( "Note: 'Garbage Collection' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def guiUpdate(self, sender=None):
		if self.pref("currentMasterOnly"):
			self.w.removeNodeNames.setTitle(u"Remove all node names 🔥❌👌🏻💚🔷 in current master")
			self.w.removeAnnotations.setTitle(u"Remove all annotations in current master")
			self.w.removeLocalGuides.setTitle(u"Remove all local (blue) guides in current master")
			self.w.removeGlobalGuides.setTitle(u"Remove all global (red) guides in current master")
			self.w.removeColors.setTitle(u"Remove glyph colors in font, layer colors in master")
		else:
			self.w.removeNodeNames.setTitle(u"Remove all node names 🔥❌👌🏻💚🔷 in font")
			self.w.removeAnnotations.setTitle(u"Remove all annotations in font")
			self.w.removeLocalGuides.setTitle(u"Remove all local (blue) guides in font")
			self.w.removeGlobalGuides.setTitle(u"Remove all global (red) guides in font")
			self.w.removeColors.setTitle(u"Remove all glyph and layer colors in font")
		
		anyUserDataOn = self.pref("userDataGlyphs") or self.pref("userDataLayers") or self.pref("userDataInstances") or self.pref("userDataMasters") or self.pref("userDataFont")
		self.w.userDataKeys.enable(anyUserDataOn)
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults[ self.domain("removeNodeNames") ] = self.w.removeNodeNames.get()
			Glyphs.defaults[ self.domain("removeLocalGuides") ] = self.w.removeLocalGuides.get()
			Glyphs.defaults[ self.domain("removeGlobalGuides") ] = self.w.removeGlobalGuides.get()
			Glyphs.defaults[ self.domain("removeAnnotations") ] = self.w.removeAnnotations.get()
			Glyphs.defaults[ self.domain("removeGlyphNotes") ] = self.w.removeGlyphNotes.get()
			Glyphs.defaults[ self.domain("removeColors") ] = self.w.removeColors.get()

			Glyphs.defaults[ self.domain("userDataFont") ] = self.w.userDataFont.get()
			Glyphs.defaults[ self.domain("userDataMasters") ] = self.w.userDataMasters.get()
			Glyphs.defaults[ self.domain("userDataInstances") ] = self.w.userDataInstances.get()
			Glyphs.defaults[ self.domain("userDataGlyphs") ] = self.w.userDataGlyphs.get()
			Glyphs.defaults[ self.domain("userDataLayers") ] = self.w.userDataLayers.get()
			Glyphs.defaults[ self.domain("userDataKeys") ] = self.w.userDataKeys.get()

			Glyphs.defaults[ self.domain("currentMasterOnly") ] = self.w.currentMasterOnly.get()
			Glyphs.defaults[ self.domain("selectedGlyphsOnly") ] = self.w.selectedGlyphsOnly.get()
			
			self.guiUpdate(sender=sender)
		except:
			return False
			
		return True

	def LoadPreferences( self, sender=None ):
		try:
			Glyphs.registerDefault(self.domain("removeNodeNames"), 1)
			Glyphs.registerDefault(self.domain("removeLocalGuides"), 0)
			Glyphs.registerDefault(self.domain("removeGlobalGuides"), 0)
			Glyphs.registerDefault(self.domain("removeAnnotations"), 1)
			Glyphs.registerDefault(self.domain("removeGlyphNotes"), 0)
			Glyphs.registerDefault(self.domain("removeColors"), 0)
			
			Glyphs.registerDefault(self.domain("userDataFont"), 0)
			Glyphs.registerDefault(self.domain("userDataMasters"), 0)
			Glyphs.registerDefault(self.domain("userDataInstances"), 0)
			Glyphs.registerDefault(self.domain("userDataGlyphs"), 0)
			Glyphs.registerDefault(self.domain("userDataLayers"), 0)
			Glyphs.registerDefault(self.domain("userDataKeys"), "UFO, fontlab, public")
			
			Glyphs.registerDefault(self.domain("currentMasterOnly"), 0)
			Glyphs.registerDefault(self.domain("selectedGlyphsOnly"), 0)
			
			self.w.removeNodeNames.set(self.pref("removeNodeNames"))
			self.w.removeLocalGuides.set(self.pref("removeLocalGuides"))
			self.w.removeGlobalGuides.set(self.pref("removeGlobalGuides"))
			self.w.removeAnnotations.set(self.pref("removeAnnotations"))
			self.w.removeGlyphNotes.set(self.pref("removeGlyphNotes"))
			self.w.removeColors.set(self.pref("removeColors"))
			
			self.w.userDataFont.set(self.pref("userDataFont"))
			self.w.userDataMasters.set(self.pref("userDataMasters"))
			self.w.userDataInstances.set(self.pref("userDataInstances"))
			self.w.userDataGlyphs.set(self.pref("userDataGlyphs"))
			self.w.userDataLayers.set(self.pref("userDataLayers"))
			self.w.userDataKeys.set(self.pref("userDataKeys"))
			
			self.w.currentMasterOnly.set(self.pref("currentMasterOnly"))
			self.w.selectedGlyphsOnly.set(self.pref("selectedGlyphsOnly"))
			
			self.guiUpdate(sender=sender)
		except:
			return False
			
		return True
	
	def log(self, msg):
		try:
			print(msg)
			self.w.statusText.set(msg)
		except Exception as e:
			import traceback
			print(traceback.format_exc())
	
	def shouldBeRemoved(self, keyName, searchFor):
		if not searchFor:
			return True
		for searchText in searchFor:
			if searchText in keyName:
				return True
		return False
		
	def GarbageCollectionMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print( "Note: 'Garbage Collection' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			thisFont.disableUpdateInterface() # suppresses UI updates in Font View

			print("Garbage Collection Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			if self.pref("selectedGlyphsOnly"):
				glyphs = [l.parent for l in thisFont.selectedLayers]
			else:
				glyphs = thisFont.glyphs
			
			# query user settings:
			currentMasterOnly = self.pref("currentMasterOnly")
			removeNodeNames = self.pref("removeNodeNames")
			removeLocalGuides = self.pref("removeLocalGuides")
			removeAnnotations = self.pref("removeAnnotations")
			removeGlyphNotes = self.pref("removeGlyphNotes")
			removeColors = self.pref("removeColors")
			userDataGlyphs = self.pref("userDataGlyphs")
			userDataLayers = self.pref("userDataLayers")
			userDataKeys = [k.strip() for k in self.pref("userDataKeys").split(",")]
			
			# font counters:
			removeNodeNamesFont = 0
			localGuidesFont = 0
			removeAnnotationsFont = 0
			
			
			for i,thisGlyph in enumerate(glyphs):
				# update progress bar:
				self.w.progress.set(int(100*i/len(glyphs)))
				
				# glyph counters:
				removeNodeNamesGlyph = 0
				localGuidesGlyph = 0
				removeAnnotationsGlyph = 0
				
				self.log( u"🔠 Cleaning %s ..." % thisGlyph.name)
				
				# layer clean-up:
				for thisLayer in thisGlyph.layers:
					if thisLayer.master == thisFont.selectedFontMaster or not currentMasterOnly:
						if removeNodeNames:
							for thisPath in thisLayer.paths:
								for thisNode in thisPath.nodes:
									if thisNode.name:
										removeNodeNamesGlyph += 1
										thisNode.name = None
						if removeLocalGuides:
							localGuidesGlyph += len(thisLayer.guideLines)
							thisLayer.guideLines = None
						if removeAnnotations:
							removeAnnotationsGlyph += len(thisLayer.annotations)
							thisLayer.annotations = None
						if removeColors:
							thisLayer.color = None
						if userDataLayers:
							if thisLayer.userData:
								keysToRemove = [k for k in thisLayer.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
								for keyToRemove in keysToRemove:
									thisLayer.removeUserDataForKey_(keyToRemove)
				
				# glyph clean-up:
				if removeGlyphNotes:
					if thisGlyph.note:
						print( "  glyph note")
						thisGlyph.note = None
				if removeColors:
					thisGlyph.color = None
				if userDataGlyphs:
					if thisGlyph.userData:
						keysToRemove = [k for k in thisGlyph.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
						for keyToRemove in keysToRemove:
							thisGlyph.removeUserDataForKey_(keyToRemove)

				# report:
				if removeNodeNamesGlyph:
					print("  %i node names" % removeNodeNamesGlyph)
					removeNodeNamesFont += removeNodeNamesGlyph
				if localGuidesGlyph:
					print("  %i local guides" % localGuidesGlyph)
					localGuidesFont += localGuidesGlyph
				if removeAnnotationsGlyph:
					print("  %i annotations" % removeAnnotationsGlyph)
					removeAnnotationsFont += removeAnnotationsGlyph
			
			# Remove global guides:
			if self.pref("removeGlobalGuides"):
				self.log(u"📏 Removing global guides ...")
				for thisMaster in thisFont.masters:
					if thisMaster == thisFont.selectedFontMaster or not currentMasterOnly:
						thisMaster.guideLines = None
			
			# User Data:
			if self.pref("userDataFont"):
				self.log("🧑🏽‍💻📄 Cleaning font.userData")
				if thisFont.userData:
					keysToRemove = [k for k in thisFont.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
					if len(keysToRemove)>0:
						print("   %i font.userData entr%s%s%s" %(
							len(keysToRemove),
							"y" if len(keysToRemove)==1 else "ies",
							": " if len(keysToRemove)>0 else "",
							", ".join(keysToRemove) if keysToRemove else "",
						))
						for keyToRemove in keysToRemove:
							thisFont.removeUserDataForKey_(keyToRemove)
					
			if self.pref("userDataMasters"):
				for thisMaster in thisFont.masters:
					self.log("🧑🏽‍💻Ⓜ️ Cleaning master.userData: %s" % thisMaster.name)
					if thisMaster.userData:
						keysToRemove = [k for k in thisMaster.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
						if len(keysToRemove)>0:
							print("   %i master.userData entr%s: %s" %(
								len(keysToRemove),
								"y" if len(keysToRemove)==1 else "ies",
								", ".join(keysToRemove) if keysToRemove else "",
							))
							for keyToRemove in keysToRemove:
								thisMaster.removeUserDataForKey_(keyToRemove)
					
			if self.pref("userDataInstances"):
				for thisInstance in thisFont.instances:
					self.log("🧑🏽‍💻ℹ️ Cleaning instance.userData: %s" % thisInstance.name)
					if thisInstance.userData:
						keysToRemove = [k for k in thisInstance.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
						if len(keysToRemove)>0:
							print("   %i instance.userData entr%s: %s" %(
								len(keysToRemove),
								"y" if len(keysToRemove)==1 else "ies",
								", ".join(keysToRemove) if keysToRemove else "",
							))
							for keyToRemove in keysToRemove:
								thisInstance.removeUserDataForKey_(keyToRemove)
			
			# full progress bar:
			self.w.progress.set(100)
			
			self.log(u"✅ Done. Log in Macro Window.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Garbage Collection Error: %s" % e)
			import traceback
			print(traceback.format_exc())
		finally:
			thisFont.enableUpdateInterface() # re-enables UI updates in Font View

GarbageCollection()