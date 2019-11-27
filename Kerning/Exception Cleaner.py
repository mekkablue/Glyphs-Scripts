#MenuTitle: Exception Cleaner
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Compares every exception to the group kerning available for the same pair. If the difference is below a threshold, remove the kerning exception.
"""

import vanilla

class DeleteExceptionsTooCloseToGroupKerning( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 430
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Exception Cleaner", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		inset, line, lineheight = 15, 10, 22
		
		self.w.text_1 = vanilla.TextBox( (inset, line, -inset, lineheight*2), "Delete all kerning exceptions in the current master if they are less than the threshold value away from their corresponding group-to-group kerning:", sizeStyle='small' )
		line += lineheight*1.8
		
		self.w.text_2 = vanilla.TextBox( (inset, line+3, 200, lineheight), "Required minimum kern difference:", sizeStyle='small' )
		self.w.threshold = vanilla.EditText( (inset+200, line, -15, 20), "10", sizeStyle = 'small', callback=self.SavePreferences)
		self.w.threshold.getNSTextField().setToolTip_(u"A kern exception must be at least this number of units different from its corresponding group kern pair, otherwise it will be deleted.")
		line += lineheight
		
		self.w.selectedGlyphsOnly = vanilla.CheckBox( (inset, line, -inset, lineheight), "Only consider pairs where at least one glyph is currently selected", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_(u"If enabled, respects your current glyph selection. Will only process kern pairs if one or both of the involved glyphs are in your selection.")
		line += lineheight
		
		self.w.reportInMacroWindow = vanilla.CheckBox( (inset, line, -inset, lineheight), "Report in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportInMacroWindow.getNSButton().setToolTip_(u"Opens the Macro Window wth a detailed report of the proceedings. Recommended for double checking.")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Run", sizeStyle='regular', callback=self.DeleteExceptionsTooCloseToGroupKerningMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Exception Cleaner' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.selectedGlyphsOnly"] = self.w.selectedGlyphsOnly.get()
			Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.threshold"] = int(self.w.threshold.get())
			Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.selectedGlyphsOnly", 0)
			Glyphs.registerDefault("com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.threshold", 10)
			Glyphs.registerDefault("com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.reportInMacroWindow", 0)
			
			self.w.selectedGlyphsOnly.set( Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.selectedGlyphsOnly"] )
			self.w.threshold.set( Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.threshold"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.reportInMacroWindow"] )
		except:
			return False
			
		return True

	def DeleteExceptionsTooCloseToGroupKerningMain( self, sender ):
		try:
			if not self.SavePreferences( self ):
				print("Note: 'Exception Cleaner' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			thisMaster = thisFont.selectedFontMaster
			thisMasterID = thisMaster.id
			
			shouldReport = Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.reportInMacroWindow"]
			onlySelectedGlyphs = Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.selectedGlyphsOnly"]
			threshold = int(Glyphs.defaults["com.mekkablue.DeleteExceptionsTooCloseToGroupKerning.threshold"])
			
			if onlySelectedGlyphs:
				selection = thisFont.selectedLayers
				if selection:
					selectedGlyphs = [l.parent for l in selection]
					selectedLeftGlyphGroups = [g.rightKerningGroup for g in selectedGlyphs]
					selectedRightGlyphGroups = [g.leftKerningGroup for g in selectedGlyphs]
				else:
					Message(title="Selection Error", message="You specified you want to process only selected glyphs, but no glyphs appear to be selected in the frontmost font.", OKButton=u"😬 Oops")	
					return
			else:
				selectedGlyphs = ()
				selectedLeftGlyphGroups = ()
				selectedRightGlyphGroups = ()
			
			if shouldReport:
				# brings macro window to front and clears its log:
				Glyphs.clearLog()
				Glyphs.showMacroWindow()
				print("Font: %s" % thisFont.familyName)
				print("Path: %s" % (thisFont.filepath if thisFont.filepath else "(unsaved)"))
				print("Master: %s" % thisMaster.name)
				print()


			# collect unnecessary kerning exceptions:
			unnecessaryKernPairs = []
			for leftSide in thisFont.kerning[thisMasterID]:
				if leftSide.startswith("@"):
					# group on the left side
					
					leftGlyphGroup = leftSide.replace("@MMK_L_","")
					leftGlyphGroupMMK = leftSide
					
					for rightSide in thisFont.kerning[thisMasterID][leftSide]:
						
						if not rightSide.startswith("@"):
							# right side is exception:
							rightGlyph = thisFont.glyphForId_(rightSide)
							
							if onlySelectedGlyphs:
								okToContinue = (leftGlyphGroup in selectedLeftGlyphGroups) or (rightGlyph in selectedGlyphs)
							else:
								okToContinue = True
							
							if okToContinue:
								if not rightGlyph:
									# found orphaned kerning, report and abort:
									if shouldReport:
										print("- Warning: could not find glyph for ID %s, consider cleaning up kerning" % rightSide)
								else:
									rightGlyphGroup = rightGlyph.leftKerningGroup
								
									if not rightGlyphGroup:
										# no corresponding kerning group, report and abort:
										if shouldReport:
											print("- Note: Glyph '%s' has no left group; skipping." % rightGlyph.name)
									else:
										rightGlyphGroupMMK = "@MMK_R_%s" % rightGlyphGroup
										exceptionKerning = thisFont.kerning[thisMasterID][leftSide][rightSide]
										groupKerning = thisFont.kerningForPair( thisMasterID, leftGlyphGroupMMK, rightGlyphGroupMMK)
										if groupKerning > 100000: # NSNotFound
											groupKerning = 0
										if abs(exceptionKerning-groupKerning) < threshold:
											if shouldReport:
												print("- Found unnecessary exception @%s-%s: %i vs. @%s-@%s: %i" % (
													leftGlyphGroup,
													rightGlyph.name,
													exceptionKerning,
													leftGlyphGroup,
													rightGlyphGroup,
													groupKerning,
												))
											unnecessaryKernPairs.append(
												("@%s"%leftGlyphGroup, rightGlyph.name)
											)
									
				else:
					# left side is exception
					leftGlyph = thisFont.glyphForId_(leftSide)
					okToContinue = (not onlySelectedGlyphs or leftGlyph in selectedGlyphs)
					if not leftGlyph:
						# found orphaned kerning, report and abort:
						if shouldReport and okToContinue:
							print("- Warning: could not find glyph for ID %s, consider cleaning up kerning" % leftSide)
							
					elif leftGlyph.export:
						# only proceed if the glyph is set to export:
						leftGlyphGroup = leftGlyph.rightKerningGroup
						
						if not leftGlyphGroup:
							# no corresponding kerning group, report and abort:
							if shouldReport and okToContinue:
								print("- Note: Glyph '%s' has no right group; skipping." % leftGlyph.name)
								
						else:
							# step through exceptions:
							leftGlyphGroupMMK = "@MMK_L_%s" % leftGlyphGroup
							
							for rightSide in thisFont.kerning[thisMasterID][leftSide]:
								if rightSide.startswith("@"):
									# exception-group:
									rightGlyph = None
									rightGlyphGroupMMK = rightSide
									rightGlyphGroup = rightSide.replace("@MMK_R_", "")
									okToContinue = okToContinue or (not onlySelectedGlyphs or rightGlyphGroup in selectedRightGlyphGroups)
								else:
									# exception-exception:
									rightGlyph = thisFont.glyphForId_(rightSide)
									rightGlyphGroup = rightGlyph.leftKerningGroup
									rightGlyphGroupMMK = "@MMK_R_%s" % rightGlyphGroup
									okToContinue = okToContinue or (not onlySelectedGlyphs or rightGlyph in selectedGlyphs)
								
								if okToContinue:
									exceptionKerning = thisFont.kerning[thisMasterID][leftSide][rightSide]
									groupKerning = thisFont.kerningForPair( thisMasterID, leftGlyphGroupMMK, rightGlyphGroupMMK)
									if groupKerning > 100000: # NSNotFound
										groupKerning = 0
								
									if abs(exceptionKerning-groupKerning) < threshold:
										if rightGlyph:
											rightSideName = rightGlyph.name
										else:
											rightSideName = "@%s"%rightGlyphGroup
										if shouldReport:
											print("- Found unnecessary exception %s-%s: %i vs. @%s-@%s: %i" % (
												leftGlyph.name,
												rightSideName,
												exceptionKerning,
												leftGlyphGroup,
												rightGlyphGroup,
												groupKerning,
											))
										unnecessaryKernPairs.append(
											(leftGlyph.name, rightSideName)
										)
			
			if not unnecessaryKernPairs:
				Message(title="No unnecessary exceptions found", message="Found no kerning exceptions that are less than %i off the group kerning."%threshold, OKButton="Hurrah!")
			else:
				for kernPair in unnecessaryKernPairs:
					leftSide, rightSide = kernPair
					if shouldReport:
						print("- Removing: %s-%s" % (leftSide, rightSide))
						
					if leftSide.startswith("@") and not leftSide.startswith("@MMK_L_"):
						leftSide = "@MMK_L_%s" % leftSide[1:]
					if rightSide.startswith("@") and not rightSide.startswith("@MMK_R_"):
						rightSide = "@MMK_R_%s" % rightSide[1:]
						
					thisFont.removeKerningForPair( thisMasterID, leftSide, rightSide )

				numberOfDeletedPairs = len(unnecessaryKernPairs)
				report=u"Deleted %i kerning exception%s in font: ‘%s’, master: ‘%s’." % (
					numberOfDeletedPairs, 
					"s" if numberOfDeletedPairs!=1 else "",
					thisFont.familyName, 
					thisMaster.name,
					)
				Message(title="Removed unnecessary exceptions", message=report, OKButton=None)
				if shouldReport:
					print()
					print(report)
				
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("'Exception Cleaner' Error: %s" % e)
			import traceback
			print(traceback.format_exc())

DeleteExceptionsTooCloseToGroupKerning()