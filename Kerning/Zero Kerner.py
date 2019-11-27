#MenuTitle: Zero Kerner
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports.
"""

import vanilla
from Foundation import NSNotFound

class ZeroKerner( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 190
		windowWidthResize  = 50 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Zero Kerner", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ZeroKerner.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 44), u"Add group kernings with value zero for pairs that are missing in one master but present in others. Helps preserve interpolatable kerning in OTVar exports.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2.5
		
		self.w.limitToCurrentMaster = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Limit to current master only (otherwise, all masters)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.limitToCurrentMaster.getNSButton().setToolTip_("Will apply zero kernings only to the currently selected master. Uncheck if all masters should be zero-kerned.")
		linePos += lineHeight
		
		self.w.reportInMacroWindow = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Detailed report in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportInMacroWindow.getNSButton().setToolTip_("If checked, will write a progress report in the Macro Window (Cmd-Opt-M).")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Zero Kern", sizeStyle='regular', callback=self.ZeroKernerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Zero Kerner' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ZeroKerner.limitToCurrentMaster"] = self.w.limitToCurrentMaster.get()
			Glyphs.defaults["com.mekkablue.ZeroKerner.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.ZeroKerner.limitToCurrentMaster", 0)
			Glyphs.registerDefault("com.mekkablue.ZeroKerner.reportInMacroWindow", 0)
			self.w.limitToCurrentMaster.set( Glyphs.defaults["com.mekkablue.ZeroKerner.limitToCurrentMaster"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.ZeroKerner.reportInMacroWindow"] )
		except:
			return False
			
		return True

	def ZeroKernerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Zero Kerner' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			limitToCurrentMaster = Glyphs.defaults["com.mekkablue.ZeroKerner.limitToCurrentMaster"]
			reportInMacroWindow = Glyphs.defaults["com.mekkablue.ZeroKerner.reportInMacroWindow"]
			self.w.progress.set(0) # set progress indicator to zero
			
			if reportInMacroWindow:
				Glyphs.clearLog()
				Glyphs.showMacroWindow()
				print("Zero Kerner Report for %s" % thisFont.familyName)
				print(thisFont.filepath)
				print()
			
			if len(thisFont.masters) < 2:
				Message(title="Zero Kerner Error", message="Zero Kerner only makes sense if there is more than one master in the font.", OKButton="Ooops")
			else:
				if limitToCurrentMaster:
					masters = (thisFont.selectedFontMaster,)
				else:
					masters = thisFont.masters
				
				masterCountPart = 100.0/len(thisFont.masters)

				for i,otherMaster in enumerate(thisFont.masters):
					masterCount = masterCountPart*i
					self.w.progress.set( masterCount )
					
					theseMasters = [m for m in masters if not m is otherMaster]
					otherMasterKerning = thisFont.kerning[otherMaster.id]
					kerningLength = len(otherMasterKerning)
					
					for j,leftGroup in enumerate(otherMasterKerning):
						kernCount = j*masterCountPart/kerningLength
						self.w.progress.set( masterCount+kernCount )
						
						if leftGroup.startswith("@"):
							for rightGroup in otherMasterKerning[leftGroup]:
								if rightGroup.startswith("@"):
									if otherMasterKerning[leftGroup][rightGroup] != 0:
										for j,thisMaster in enumerate(theseMasters):
						
											masterKerning = thisFont.kerning[thisMaster.id]
											# kernPairCount = len(masterKerning)
											
											if thisFont.kerningForPair(thisMaster.id, leftGroup, rightGroup) >= NSNotFound:
												thisFont.setKerningForPair(thisMaster.id, leftGroup, rightGroup, 0.0)
												if reportInMacroWindow:
													print("  %s, @%s @%s: zeroed" % (thisMaster.name, leftGroup[7:], rightGroup[7:]))
				
				self.w.progress.set(100.0)
				
			
			listOfSelectedLayers = thisFont.selectedLayers # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers: # loop through layers
				thisGlyph = thisLayer.parent
				print(thisGlyph.name, thisLayer.name)
				# output all node coordinates:
				for thisPath in thisLayer.paths:
					for thisNode in thisLayer.nodes:
						print("-- %.1f %.1f" % ( thisNode.x, thisNode.y ))
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Zero Kerner Error: %s" % e)
			import traceback
			print(traceback.format_exc())

ZeroKerner()