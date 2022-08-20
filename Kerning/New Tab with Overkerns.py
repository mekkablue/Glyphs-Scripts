#MenuTitle: New Tab with Overkerned Pairs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Asks a threshold percentage, and opens a new tab with all kern pairs going beyond the width threshold. Option to fix them too.
"""

import vanilla, sys

def roundedDownBy(value, base):
	return base * round(value//base)

class NewTabwithOverkernedPairs( object ):
	prefID = "com.mekkablue.FindOverkerns"
	prefDict = {
		# "prefName": defaultValue,
		"threshold": 40,
		"limitToExportingGlyphs": 1,
		"rounding": 5,
		"allMasters": 0,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 290
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Negative Overkerns in this Master", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, 210, 14), "Open tab with kerns beyond threshold:", sizeStyle='small', selectable=True )
		self.w.threshold = vanilla.EditText( (inset+210, linePos-1, -inset, 19), "40", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.descriptionText2 = vanilla.TextBox( (inset, linePos+2, -inset, 14), "(Max percentage of widths that may be kerned.)", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.roundingText = vanilla.TextBox( (inset, linePos+2, 125, 14), "When fixing, round by:", sizeStyle='small', selectable=True )
		self.w.rounding = vanilla.EditText( (inset+125, linePos-1, 50, 19), "5", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.limitToExportingGlyphs = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Limit to exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.allMasters = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Apply to ⚠️ ALL masters of current font", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.fixButton = vanilla.Button( (-180-inset, -20-inset, -110-inset, -inset), "Fix", sizeStyle='regular', callback=self.NewTabwithOverkernedPairsMain )
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Report", sizeStyle='regular', callback=self.NewTabwithOverkernedPairsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘New Tab with Overkerned Pairs’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set( self.pref(prefName) )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def NewTabwithOverkernedPairsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			shouldFix = sender == self.w.fixButton
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘New Tab with Overkerned Pairs’ could not write preferences.")
			
			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
					print(prefName,"=",self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print("⚠️ Could not set pref ‘%s’, resorting to default value: ‘%s’." % (prefName, fallbackValue))
					setattr(sys.modules[__name__], prefName, fallbackValue)
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = thisFont.filepath
				if filePath:
					report = "%s\n📄 %s" % (filePath.lastPathComponent(), filePath)
				else:
					report = "%s\n⚠️ The font file has not been saved yet." % thisFont.familyName
				print("New Tab with Overkerned Pairs Report for %s" % report)
				print()
			

				thresholdFactor = None
				try:
					thresholdFactor = float( threshold )/100.0
				except:
					Message(title="Value Error", message="The threshold value you entered is invalid", OKButton="Oops")
					return
				
				rounding = int(self.pref("rounding"))
				
				if allMasters:
					theseMasters = thisFont.masters
				else:
					theseMasters = (thisFont.selectedFontMaster,)
					
				overKernCount = 0
				for thisMaster in theseMasters:
					masterKerning = thisFont.kerning[thisMaster.id] # kerning dictionary
					tabText = "" # the text appearing in the new tab
			
					# collect minimum widths for every kerning group:
					leftGroupMinimumWidths = {}
					leftGroupNarrowestGlyphs = {}
					rightGroupMinimumWidths = {}
					rightGroupNarrowestGlyphs = {}
					if limitToExportingGlyphs:
						theseGlyphs = [g for g in thisFont.glyphs if g.export]
					else:
						theseGlyphs = thisFont.glyphs
					for thisGlyph in theseGlyphs:
						thisLayer = thisGlyph.layers[thisMaster.id]
					
						# left side of the glyph (= right side of kern pair)
						if thisGlyph.leftKerningGroup:
							if thisGlyph.leftKerningGroup in leftGroupMinimumWidths.keys():
								if thisLayer.width < leftGroupMinimumWidths[thisGlyph.leftKerningGroup]:
									leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
									leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
							else:
								leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
								leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
							
						# right side of the glyph (= left side of kern pair)
						if thisGlyph.rightKerningGroup:
							if thisGlyph.rightKerningGroup in rightGroupMinimumWidths.keys():
								if thisLayer.width < rightGroupMinimumWidths[thisGlyph.rightKerningGroup]:
									rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
									rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
							else:
								rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
								rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
			
					# go through kern values and collect them in tabText:
					for leftKey in masterKerning.keys():
						for rightKey in masterKerning[leftKey].keys():
							kernValue = masterKerning[leftKey][rightKey]
							if kernValue < 0:
								leftWidth = None
								rightWidth = None
							
								try:
									# collect widths for comparison
									if leftKey[0] == "@":
										# leftKey is a group name like "@MMK_L_y"
										groupName = leftKey[7:]
										leftWidth = rightGroupMinimumWidths[groupName]
										leftGlyphName = rightGroupNarrowestGlyphs[groupName]
									else:
										# leftKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
										leftGlyph = thisFont.glyphForId_(leftKey)
										# exclude if non-exporting and user limited to exporting glyphs:
										if limitToExportingGlyphs and not leftGlyph.export:
											kernValue = 0.0
										leftWidth = leftGlyph.layers[thisMaster.id].width
										leftGlyphName = leftGlyph.name
							
									if rightKey[0] == "@":
										# rightKey is a group name like "@MMK_R_y"
										groupName = rightKey[7:]
										rightWidth = leftGroupMinimumWidths[groupName]
										rightGlyphName = leftGroupNarrowestGlyphs[groupName]
									else:
										# rightKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
										rightGlyph = thisFont.glyphForId_(rightKey)
										# exclude if non-exporting and user limited to exporting glyphs:
										if limitToExportingGlyphs and not rightGlyph.export:
											kernValue = 0.0
										rightWidth = rightGlyph.layers[thisMaster.id].width
										rightGlyphName = rightGlyph.name
							
									# compare widths and collect overkern if it is one:
									# (kernValue of excluded glyphs will be 0.0 and not trigger the if clause)
									maxPossibleKernValue = min(thresholdFactor*leftWidth, thresholdFactor*rightWidth)
									if abs(kernValue) > maxPossibleKernValue:
										overKernCount += 1
										tabText += "/%s/%s  " % (leftGlyphName, rightGlyphName)
										if shouldFix:
											masterKerning[leftKey][rightKey] = -roundedDownBy(maxPossibleKernValue, rounding)
									
								except Exception as e:
									# probably a kerning group name found in the kerning data, but no glyph assigned to it:
									# brings macro window to front and reports warning:
									import traceback
									errormsg = traceback.format_exc()
									for side in ("left","right"):
										if not side in errormsg.lower():
											print(
												"⚠️ Warning: The %s group '%s' found in your kerning data does not appear in any glyph. Clean up your kerning, and run the script again." % (
													side,
													groupName,
											))
											Glyphs.showMacroWindow()
					
					tabText = tabText.strip()
					tabText += "\n\n"
					
				if overKernCount:
					# opens new Edit tab:
					thisFont.newTab( tabText.strip() )
					Message(
						title="Overkerns in %s" % thisFont.familyName,
						message="%s %i overkerns in %i master%s." % (
							"Fixed" if shouldFix else "Found",
							overKernCount,
							len(theseMasters),
							"" if len(theseMasters)==1 else "s",
						),
						OKButton=None,
						)
				else:
					Message(title="No Overkerns Found", message="Could not find any kern pairs beyond the threshold in this master.", OKButton="Phew!")


		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with Overkerned Pairs Error: %s" % e)
			import traceback
			print(traceback.format_exc())

NewTabwithOverkernedPairs()