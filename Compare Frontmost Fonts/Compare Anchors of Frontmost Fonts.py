#MenuTitle: Compare Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Compares anchor structure and anchor heights between the two frontmost fonts.
"""

import vanilla

class CompareAnchorsOfFrontmostFonts( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 360
		windowHeight = 280
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Compare Anchors of Frontmost Fonts", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CompareAnchorsOfFrontmostFonts.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 28), u"Lists all differences in anchor structures and positions in a detailed report in the Macro Window.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.reportAnchorHeights = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Also report differences in anchor heights", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportAnchorHeights.getNSButton().setToolTip_("Lists anchors in corresponding glyphs if their y coordinates differ more than the threshold set below. Otherwise, only report anchor structures.")
		linePos += lineHeight
		
		self.w.anchorHeightToleranceText = vanilla.TextBox( (inset*2, linePos+2, 120, 14), u"Deviation tolerance:", sizeStyle='small', selectable=True )
		self.w.anchorHeightTolerance = vanilla.EditText( (inset*2+120, linePos, -inset, 19), "0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.anchorHeightTolerance.getNSTextField().setToolTip_(u"Will not report if the difference in y coordinates is less or same as the given tolerance. Use this if e.g. your x-height is different in your italic. Set to zero or leave blank for exact match.")
		linePos += lineHeight
		
		self.w.ignoreExitEntry = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Ignore exit and entry anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreExitEntry.getNSButton().setToolTip_("Will skip cursive attachment anchors (#)exit and (#)entry.")
		linePos += lineHeight
		
		self.w.ignoreHashtaggedAnchors = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Ignore #hashtagged anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreHashtaggedAnchors.getNSButton().setToolTip_("Will skip anchors that start with # or _#.")
		linePos += lineHeight
		
		self.w.reportOnlyTopBottomCenter = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Report only top, bottom, center and corresponding anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportOnlyTopBottomCenter.getNSButton().setToolTip_("Only reports default mark attachment anchors top, _top, bottom, _bottom, center and _center. Ignores other anchors such as ogonek or topright. This option makes the ignore options above obsolete.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Also report if glyph is set to not export. Recommended because non-exporting glyphs may appear as components in other glyphs.")
		linePos += lineHeight

		self.w.openTabAndSelectAnchors = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Open tabs with affected glyph layers and preselect anchors", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTabAndSelectAnchors.getNSButton().setToolTip_("Opens the affected glyph layers in a tab per font, resets the selection, and selects the affected anchors for immediate editing. To take advantage of the selection, do not double click a glyph for editing (the click resets the selection), but open them with the Esc key or by switching to the Edit tool.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Compare", sizeStyle='regular', callback=self.CompareAnchorsOfFrontmostFontsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Compare Anchors of Frontmost Fonts' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def updateGUI(self, sender=None):
		try:
			onlyTopBottomSetting = bool(self.w.reportOnlyTopBottomCenter.get())
			ignoreSetting = not onlyTopBottomSetting
			self.w.ignoreExitEntry.enable( ignoreSetting )
			self.w.ignoreHashtaggedAnchors.enable( ignoreSetting )
		except Exception as e:
			print(u"Error: Could not update UI. You can ignore this warning, but let Rainer know.")
			print(e)
			import traceback
			print(traceback.format_exc())
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportAnchorHeights"] = self.w.reportAnchorHeights.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.anchorHeightTolerance"] = self.w.anchorHeightTolerance.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreExitEntry"] = self.w.ignoreExitEntry.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreHashtaggedAnchors"] = self.w.ignoreHashtaggedAnchors.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportOnlyTopBottomCenter"] = self.w.reportOnlyTopBottomCenter.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"] = self.w.openTabAndSelectAnchors.get()
			self.updateGUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.reportAnchorHeights", 1)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.anchorHeightTolerance", 0)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreExitEntry", 0)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreHashtaggedAnchors", 0)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.reportOnlyTopBottomCenter", 0)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.includeNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors", 1)
			self.w.reportAnchorHeights.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportAnchorHeights"] )
			self.w.anchorHeightTolerance.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.anchorHeightTolerance"] )
			self.w.ignoreExitEntry.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreExitEntry"] )
			self.w.ignoreHashtaggedAnchors.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreHashtaggedAnchors"] )
			self.w.reportOnlyTopBottomCenter.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportOnlyTopBottomCenter"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.includeNonExporting"] )
			self.w.openTabAndSelectAnchors.set( Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"] )
			self.updateGUI()
		except:
			return False
			
		return True
		
	def selectAnchorsInLayer(self, anchorNames, layer, resetSelection=True):
		if resetSelection:
			layer.selection = None
		if anchorNames:
			for anchorName in anchorNames:
				thisAnchor = layer.anchors[anchorName]
				if thisAnchor:
					thisAnchor.selected = True

	def CompareAnchorsOfFrontmostFontsMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Compare Anchors of Frontmost Fonts' could not write preferences.")
			
			# query prefs:
			reportOnlyTopBottomCenter = Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportOnlyTopBottomCenter"]
			ignoreExitEntry = Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreExitEntry"]
			ignoreHashtaggedAnchors = Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.ignoreHashtaggedAnchors"]
			reportAnchorHeights = Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.reportAnchorHeights"]
			
			if len(Glyphs.fonts) < 2:
				Message(title="Compare Error", message="You need to have at least two fonts open for comparing.", OKButton="Ooops")	
			else:
				# brings macro window to front and clears its log:
				Glyphs.clearLog()
				# Glyphs.showMacroWindow()
				
				thisFont = Glyphs.font # frontmost font
				otherFont = Glyphs.fonts[1] # second font
				thisFilePath, otherFilePath = thisFont.filepath, otherFont.filepath
				thisFileName, otherFileName = thisFont.filepath.lastPathComponent(), otherFont.filepath.lastPathComponent(), 
				print("Compare Anchors of Frontmost Fonts Report for:\n  (1) %s: %s\n      %s\n  (2) %s: %s\n      %s" % (
					thisFont.familyName, thisFilePath, thisFileName, 
					otherFont.familyName, otherFilePath, otherFileName, 
					))
				print()
				
				try:
					tolerance = abs(float(Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.anchorHeightTolerance"]))
				except:
					tolerance = 0.0
				if reportAnchorHeights:
					print("Anchor height tolerance: %.1f units" % tolerance)
					print()
				
				theseIDs = [m.id for m in thisFont.masters]
				otherIDs = [m.id for m in otherFont.masters]
				masters = zip(theseIDs, otherIDs)
				
				if len(theseIDs) != len(otherIDs):
					print(u"⚠️ Different number of masters in (1) %s and (2) %s" % (thisFileName, otherFileName))
					print()
				
				skippedGlyphNames = []
				affectedGlyphNames = []
				for i, thisGlyph in enumerate(thisFont.glyphs):
					self.w.progress.set( i/len(thisFont.glyphs) )
					otherGlyph = otherFont.glyphs[thisGlyph.name]
					if not otherGlyph:
						print(u"⚠️ Glyph %s missing in (2) %s" % (thisGlyph.name, otherFileName))
					else:
						if not (thisGlyph.export or Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.includeNonExporting"]):
							skippedGlyphNames.append(thisGlyph.name) 
							if otherGlyph.export:
								print(u"😬 Glyph %s exports in (2) %s, but not in (1) %s. Skipping." % (thisGlyph.name, otherFileName, thisFileName))
						else:
							if not (otherGlyph.export or Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.includeNonExporting"]):
								print(u"😬 Glyph %s exports in (1) %s, but not in (2) %s. Skipping." % (thisGlyph.name, thisFileName, otherFileName))
								skippedGlyphNames.append(thisGlyph.name) 
							else:
								
								for idSet in masters:
									thisID, otherID = idSet
									thisLayer, otherLayer = thisGlyph.layers[thisID], otherGlyph.layers[otherID]
									if Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"]:
										self.selectAnchorsInLayer(None, thisLayer, resetSelection=True)
										self.selectAnchorsInLayer(None, otherLayer, resetSelection=True)

									theseAnchors = sorted([a.name for a in thisLayer.anchors])
									otherAnchors = sorted([a.name for a in otherLayer.anchors])
							
									# clean up compare lists if requested:
									for anchorList in (theseAnchors, otherAnchors):
										for i in range(len(anchorList))[::-1]:
											currentAnchor = anchorList[i]
											if reportOnlyTopBottomCenter:
												# keep only top/bottom/center:
												if not currentAnchor in ("top","bottom","center","_top","_bottom","_center"):
													del anchorList[i]
											else:
												# determine exit and entry anchors:
												anchorIsExitOrEntry = False
												for anchorname in ("exit","entry"):
													if currentAnchor.endswith(anchorname) and len(currentAnchor) in (len(anchorname), len(anchorname)+1):
														anchorIsExitOrEntry = True
														
												# determine hashtagged anchors:
												anchorIsHashtagged = currentAnchor.startswith("#") or currentAnchor.startswith("_#")
												
												# remove if affected:
												if (ignoreExitEntry and anchorIsExitOrEntry) or (ignoreHashtaggedAnchors and anchorIsHashtagged):
													del anchorList[i]

									if theseAnchors != otherAnchors:
										missingInOtherAnchors = [a for a in theseAnchors if not a in otherAnchors]
										missingInTheseAnchors = [a for a in otherAnchors if not a in theseAnchors]
										
										if missingInTheseAnchors:
											print(u"🚫 %s (%s): missing anchor%s %s in (1) %s" % (
												thisGlyph.name, thisLayer.name,
												"" if len(missingInTheseAnchors)==1 else "s",
												", ".join(["'%s'"%a for a in missingInTheseAnchors]),
												thisFileName,
											))
											if Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"]:
												self.selectAnchorsInLayer(missingInTheseAnchors, otherLayer, resetSelection=False)
											affectedGlyphNames.append(otherGlyph.name)
												
										if missingInOtherAnchors:
											print(u"🚫 %s (%s): missing anchor%s %s in (2) %s" % (
												otherGlyph.name, otherLayer.name,
												"" if len(missingInOtherAnchors)==1 else "s",
												", ".join(["'%s'"%a for a in missingInOtherAnchors]),
												otherFileName,
											))
											if Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"]:
												self.selectAnchorsInLayer(missingInOtherAnchors, thisLayer, resetSelection=False)
											affectedGlyphNames.append(thisGlyph.name)
											
									if reportAnchorHeights:
										differingAnchors = []
										for thisAnchorName in theseAnchors:
											if thisAnchorName in otherAnchors:
												thisAnchor = thisLayer.anchors[thisAnchorName]
												otherAnchor = otherLayer.anchors[thisAnchorName]
												if thisAnchor and otherAnchor: # just to make sure
													heightDifference = abs(thisAnchor.position.y - otherAnchor.position.y)
													if not heightDifference <= tolerance:
														differingAnchors.append(thisAnchor.name)
										
										if differingAnchors:
											print(u"↕️ %s: %s deviate%s in: (1) %s, (2) %s" % (
												thisGlyph.name,
												", ".join(["'%s'" % a for a in differingAnchors]),
												"s" if len(differingAnchors)==1 else "", 
												thisLayer.name, otherLayer.name,
											))
											if Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"]:
												self.selectAnchorsInLayer( differingAnchors, thisLayer, resetSelection=False )
												self.selectAnchorsInLayer( differingAnchors, otherLayer, resetSelection=False )
											affectedGlyphNames.append(thisGlyph.name)
				
				# open tab or macro window:
				affectedGlyphNames = set(affectedGlyphNames)
				if affectedGlyphNames:
					tabString = "/"+"/".join(affectedGlyphNames)
					print("\nFound %i affected glyphs:\n%s" % ( len(affectedGlyphNames), tabString))

					if Glyphs.defaults["com.mekkablue.CompareAnchorsOfFrontmostFonts.openTabAndSelectAnchors"]:
						# opens new Edit tab:
						thisFont.newTab( tabString )
						otherFont.newTab( tabString )
					else:
						# brings macro window to front:
						Glyphs.showMacroWindow()
						
				if skippedGlyphNames:
					print("\nSkipped %i glyphs:\n%s" % ( len(skippedGlyphNames), ", ".join(skippedGlyphNames) ))
				
				self.w.progress.set(100)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compare Anchors of Frontmost Fonts Error: %s" % e)
			import traceback
			print(traceback.format_exc())

CompareAnchorsOfFrontmostFonts()