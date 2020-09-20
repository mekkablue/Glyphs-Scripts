#MenuTitle: Remove TT Hints
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes a user-specified set of TT instructions throughout the current font, the selected master and/or the selected glyphs.
"""

import vanilla

class RemoveTTHints( object ):
	wheres = (
		"current layer of selected glyphs",
		"all layers of selected glyphs",
		"this master",
		"the complete font",
		)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 270
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Remove TT Hints", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RemoveTTHints.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		column = 160
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, 160, 14), u"Remove the following hints in", sizeStyle='small', selectable=True )
		self.w.where = vanilla.PopUpButton( (inset+160, linePos, -inset, 17), self.wheres, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		self.w.hStems = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Stem", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vStems = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Stem", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.hAnchors = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Anchor", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vAnchors = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Anchor", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.hAlign = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Align", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vAlign = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Align", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.hInterpolate = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Interpolate", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vInterpolate = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Interpolate", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.hDiagonal = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Diagonal", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vDiagonal = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Diagonal", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.hDelta = vanilla.CheckBox( (inset, linePos, column, 20), u"⬍ H Delta", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.vDelta = vanilla.CheckBox( (inset+column, linePos, -inset, 20), u"⬌ V Delta", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += int(lineHeight*1.2)
		
		self.w.hON = vanilla.SquareButton( (inset, linePos, 40, 18), u"H on", sizeStyle='small', callback=self.update )
		self.w.hOFF = vanilla.SquareButton( (inset+40, linePos, 40, 18), u"H off", sizeStyle='small', callback=self.update )
		
		self.w.vON = vanilla.SquareButton( (inset+column, linePos, 40, 18), u"V on", sizeStyle='small', callback=self.update )
		self.w.vOFF = vanilla.SquareButton( (inset+column+40, linePos, 40, 18), u"V off", sizeStyle='small', callback=self.update )
		linePos += int(lineHeight*1.2)
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveTTHintsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove TT Hints' could not load preferences. Will resort to defaults")
		
		self.update()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def update(self, sender=None, savePrefs=True):
		if sender: # any button
			onOff = 0
			if sender in (self.w.hON, self.w.vON):
				onOff=1
		
			if sender in (self.w.hON, self.w.hOFF):
				self.w.hStems.set(onOff)
				self.w.hAnchors.set(onOff)
				self.w.hAlign.set(onOff)
				self.w.hInterpolate.set(onOff)
				self.w.hDiagonal.set(onOff)
				self.w.hDelta.set(onOff)
			
			if sender in (self.w.vON, self.w.vOFF):
				self.w.vStems.set(onOff)
				self.w.vAnchors.set(onOff)
				self.w.vAlign.set(onOff)
				self.w.vInterpolate.set(onOff)
				self.w.vDiagonal.set(onOff)
				self.w.vDelta.set(onOff)
		
		onOff = (
			self.w.hStems.get() or
			self.w.hAnchors.get() or
			self.w.hAlign.get() or
			self.w.hInterpolate.get() or
			self.w.hDiagonal.get() or
			self.w.hDelta.get() or
			self.w.vStems.get() or
			self.w.vAnchors.get() or
			self.w.vAlign.get() or
			self.w.vInterpolate.get() or
			self.w.vDiagonal.get() or
			self.w.vDelta.get()
		)
		self.w.runButton.enable(onOff)
		
		if savePrefs:
			self.SavePreferences(update=False)
			
		
	def SavePreferences( self, sender=None, update=True ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.RemoveTTHints.where"] = self.w.where.get()

			Glyphs.defaults["com.mekkablue.RemoveTTHints.hStems"] = self.w.hStems.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.hAnchors"] = self.w.hAnchors.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.hAlign"] = self.w.hAlign.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.hInterpolate"] = self.w.hInterpolate.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.hDiagonal"] = self.w.hDiagonal.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.hDelta"] = self.w.hDelta.get()
			
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vStems"] = self.w.vStems.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vAnchors"] = self.w.vAnchors.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vAlign"] = self.w.vAlign.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vInterpolate"] = self.w.vInterpolate.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vDiagonal"] = self.w.vDiagonal.get()
			Glyphs.defaults["com.mekkablue.RemoveTTHints.vDelta"] = self.w.vDelta.get()
			
			if update:
				self.update()
				
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.where", 0)

			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hStems", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hAnchors", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hAlign", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hInterpolate", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hDiagonal", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.hDelta", 0)

			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vStems", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vAnchors", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vAlign", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vInterpolate", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vDiagonal", 0)
			Glyphs.registerDefault("com.mekkablue.RemoveTTHints.vDelta", 0)
			
			# load previously written prefs:
			self.w.where.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.where"] )

			self.w.hStems.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hStems"] )
			self.w.hAnchors.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hAnchors"] )
			self.w.hAlign.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hAlign"] )
			self.w.hInterpolate.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hInterpolate"] )
			self.w.hDiagonal.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hDiagonal"] )
			self.w.hDelta.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.hDelta"] )

			self.w.vStems.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vStems"] )
			self.w.vAnchors.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vAnchors"] )
			self.w.vAlign.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vAlign"] )
			self.w.vInterpolate.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vInterpolate"] )
			self.w.vDiagonal.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vDiagonal"] )
			self.w.vDelta.set( Glyphs.defaults["com.mekkablue.RemoveTTHints.vDelta"] )
			
			self.update()
			
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def removeHintsFromLayer(self,layer):
		delCount = 0
		for i in reversed(range(len(layer.hints))):
			h = layer.hints[i]
			if h.isTrueType():
				if h.type == TTSTEM and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hStems"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTANCHOR and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hAnchors"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTALIGN and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hAlign"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTINTERPOLATE and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hInterpolate"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDIAGONAL and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hDiagonal"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDELTA and h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.hDelta"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTSTEM and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vStems"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTANCHOR and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vAnchors"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTALIGN and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vAlign"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTINTERPOLATE and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vInterpolate"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDIAGONAL and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vDiagonal"]:
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDELTA and not h.horizontal and Glyphs.defaults["com.mekkablue.RemoveTTHints.vDelta"]:
					del layer.hints[i]
					delCount += 1
		
		if delCount:
			print("- Removed %i instruction%s from %s, layer ‘%s’" % (
				delCount,
				"" if delCount==1 else "s",
				layer.parent.name,
				layer.name,
				))
		return delCount
	
	def RemoveTTHintsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Remove TT Hints' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Remove TT Hints Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
				
				where = Glyphs.defaults["com.mekkablue.RemoveTTHints.where"]
				
				layers = None
				deletedHintsCount = 0
				if where==0:
					# Current Layer of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i,l in enumerate(objectList):
						self.w.progress.set(i/count*100)
						deletedHintsCount += self.removeHintsFromLayer(l)
				elif where==1:
					# All Layers of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i,l in enumerate(objectList):
						self.w.progress.set(i/count*100)
						g = l.parent
						for ll in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(ll)
				elif where==2:
					# this Master
					masterID = thisFont.selectedFontMaster.id
					objectList = thisFont.glyphs
					count = len(objectList)
					for i,g in enumerate(objectList):
						self.w.progress.set(i/count*100)
						for l in g.layers:
							if l.associatedMasterId == masterID:
								deletedHintsCount += self.removeHintsFromLayer(l)
				else:
					# the Complete Font
					objectList = thisFont.glyphs
					count = len(objectList)
					for i,g in enumerate(objectList):
						self.w.progress.set(i/count*100)
						for l in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(l)
				
				# Complete progress bar:
				self.w.progress.set(100)
				
				# Final report:
				totalCountMsg = "Removed %i instruction%s" % ( 
					deletedHintsCount, 
					"" if deletedHintsCount==1 else "s",
					)
					
				Glyphs.showNotification( 
					totalCountMsg,
					"Font: %s" % (thisFont.familyName),
					)
				
				print("%sTOTAL: %s"%(
					"\n" if deletedHintsCount else "",
					totalCountMsg,
					))
				
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove TT Hints Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveTTHints()