#MenuTitle: Remove PS Hints
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes PS Hints, selectively or completely.
"""

import vanilla

class RemovePSHints( object ):
	wheres = (
		"current layer of selected glyphs",
		"all layers of selected glyphs",
		"this master",
		"the complete font",
		)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 170
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove PS Hints", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RemovePSHints.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, 160, 14), u"Remove the following hints in", sizeStyle='small', selectable=True )
		self.w.where = vanilla.PopUpButton( (inset+160, linePos, -inset, 17), self.wheres, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.horizontalStemHints = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Horizontal Stem Hints", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.verticalStemHints = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Vertical Stem Hints", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.ghostHints = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Ghost Hints", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-130-inset, -20-inset, -inset, -inset), "Remove Hints", sizeStyle='regular', callback=self.RemovePSHintsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove PS Hints' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RemovePSHints.horizontalStemHints"] = self.w.horizontalStemHints.get()
			Glyphs.defaults["com.mekkablue.RemovePSHints.verticalStemHints"] = self.w.verticalStemHints.get()
			Glyphs.defaults["com.mekkablue.RemovePSHints.ghostHints"] = self.w.ghostHints.get()
			Glyphs.defaults["com.mekkablue.RemovePSHints.where"] = self.w.where.get()
			
			buttonEnable = Glyphs.defaults["com.mekkablue.RemovePSHints.horizontalStemHints"] or Glyphs.defaults["com.mekkablue.RemovePSHints.verticalStemHints"] or Glyphs.defaults["com.mekkablue.RemovePSHints.ghostHints"]
			self.w.runButton.enable(onOff=buttonEnable)
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RemovePSHints.horizontalStemHints", 1)
			Glyphs.registerDefault("com.mekkablue.RemovePSHints.verticalStemHints", 1)
			Glyphs.registerDefault("com.mekkablue.RemovePSHints.ghostHints", 1)
			Glyphs.registerDefault("com.mekkablue.RemovePSHints.where", 2)
			self.w.horizontalStemHints.set( Glyphs.defaults["com.mekkablue.RemovePSHints.horizontalStemHints"] )
			self.w.verticalStemHints.set( Glyphs.defaults["com.mekkablue.RemovePSHints.verticalStemHints"] )
			self.w.ghostHints.set( Glyphs.defaults["com.mekkablue.RemovePSHints.ghostHints"] )
			self.w.where.set( Glyphs.defaults["com.mekkablue.RemovePSHints.where"] )
		except:
			return False
			
		return True
	
	def removeHintsFromLayer(self,layer,horizontalStemHints,verticalStemHints,ghostHints):
		delCount = 0
		for i in reversed(range(len(layer.hints))):
			h = layer.hints[i]
			if h.isPostScript():
				if horizontalStemHints and h.horizontal and h.type==STEM:
					del layer.hints[i]
					delCount += 1
				elif verticalStemHints and not h.horizontal and h.type==STEM:
					del layer.hints[i]
					delCount += 1
				elif ghostHints and h.type in (BOTTOMGHOST,TOPGHOST):
					del layer.hints[i]
					delCount += 1
		return delCount

	def RemovePSHintsMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Remove PS Hints' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Remove PS Hints Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			horizontalStemHints = Glyphs.defaults["com.mekkablue.RemovePSHints.horizontalStemHints"]
			verticalStemHints = Glyphs.defaults["com.mekkablue.RemovePSHints.verticalStemHints"]
			ghostHints = Glyphs.defaults["com.mekkablue.RemovePSHints.ghostHints"]
			where = Glyphs.defaults["com.mekkablue.RemovePSHints.where"]
			
			layers = None
			deletedHintsCount = 0
			if where==0:
				# Current Layer of Selected Glyphs
				objectList = set(thisFont.selectedLayers)
				count = len(objectList)
				for i,l in enumerate(objectList):
					self.w.progress.set(i/count*100)
					deletedHintsCount += self.removeHintsFromLayer(l,horizontalStemHints,verticalStemHints,ghostHints)
			elif where==1:
				# All Layers of Selected Glyphs
				objectList = set(thisFont.selectedLayers)
				count = len(objectList)
				for i,l in enumerate(objectList):
					self.w.progress.set(i/count*100)
					g = l.parent
					for ll in g.layers:
						deletedHintsCount += self.removeHintsFromLayer(ll,horizontalStemHints,verticalStemHints,ghostHints)
			elif where==2:
				# this Master
				masterID = thisFont.selectedFontMaster.id
				objectList = thisFont.glyphs
				count = len(objectList)
				for i,g in enumerate(objectList):
					self.w.progress.set(i/count*100)
					for l in g.layers:
						if l.associatedMasterId == masterID:
							deletedHintsCount += self.removeHintsFromLayer(l,horizontalStemHints,verticalStemHints,ghostHints)
			else:
				# the Complete Font
				objectList = thisFont.glyphs
				count = len(objectList)
				for i,g in enumerate(objectList):
					self.w.progress.set(i/count*100)
					for l in g.layers:
						deletedHintsCount += self.removeHintsFromLayer(l,horizontalStemHints,verticalStemHints,ghostHints)
			
			# complete progress bar:
			self.w.progress.set(100)
			
			# Floating notification:
			Glyphs.showNotification( 
				u"Removed %i hint%s" % ( 
					deletedHintsCount, 
					"" if deletedHintsCount==1 else "s",
					),
				u"Font: %s" % (thisFont.familyName),
				)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove PS Hints Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemovePSHints()