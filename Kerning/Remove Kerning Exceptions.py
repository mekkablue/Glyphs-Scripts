#MenuTitle: Remove Kerning Exceptions
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes all kernings glyph-glyph, group-glyph, and glyph-group; only keeps group-group kerning.
"""

import vanilla

class RemoveKerningExceptions(object):
	prefID = "com.mekkablue.RemoveKerningExceptions"
	prefDict = {
		# "prefName": defaultValue,
		"glyphGlyph": 1,
		"glyphGroup": 1,
		"groupGlyph": 1,
		"keepGrouplessKerning": 0,
		"removeOnMasters": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 180
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Remove Kerning Exceptions", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="%s.mainwindow" % self.prefID # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.glyphGlyph = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove 🅰️🅰️ glyph-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.glyphGroup = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove 🅰️🔠 glyph-to-group pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.groupGlyph = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove 🔠🅰️ group-to-glyph pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight
		self.w.keepGrouplessKerning = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Keep kerning for groupless glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.removeOnMastersText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Remove on:", sizeStyle='small', selectable=True)
		self.w.removeOnMasters = vanilla.PopUpButton(
			(inset + 70, linePos, -inset, 17), ("current master", "⚠️ all masters of current font", "⚠️ all masters of ⚠️ all open fonts"),
			sizeStyle='small',
			callback=self.SavePreferences
			)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Remove", sizeStyle='regular', callback=self.RemoveKerningExceptionsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Remove Kerning Exceptions' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateGUI(self, sender=None):
		anyOptionIsSelected = self.w.glyphGlyph.get() or self.w.glyphGroup.get() or self.w.groupGlyph.get()
		self.w.runButton.enable(anyOptionIsSelected)

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
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
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def RemoveKerningExceptionsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Remove Kerning Exceptions' could not write preferences.")

			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires at least one font. Open a font and run the script again.", OKButton=None)
			else:
				for prefName in self.prefDict.keys():
					try:
						setattr(sys.modules[__name__], prefName, self.pref(prefName))
					except:
						fallbackValue = self.prefDict[prefName]
						print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
						setattr(sys.modules[__name__], prefName, fallbackValue)

				if removeOnMasters == 2:
					fonts = Glyphs.fonts
					allMasters = True
				else:
					fonts = (thisFont, )
					if removeOnMasters == 0:
						allMasters = False
					else:
						allMasters = True

				for thisFont in fonts:
					print("\nRemoving kerning exceptions in: %s" % thisFont.familyName)
					if thisFont.filepath:
						print("📄 %s" % thisFont.filepath)
					else:
						print("⚠️ The font file has not been saved yet.")

					totalCount = 0
					for thisMaster in thisFont.masters:
						if allMasters or thisMaster == thisFont.selectedFontMaster:
							pairsToBeRemoved = []
							for leftSide in thisFont.kerning[thisMaster.id].keys():
								leftSideIsGlyph = not leftSide.startswith("@")
								leftHasNoGroup = leftSideIsGlyph and not thisFont.glyphForId_(leftSide).rightKerningGroup
								leftMayBeDeleted = not (leftHasNoGroup and keepGrouplessKerning)
								
								for rightSide in thisFont.kerning[thisMaster.id][leftSide].keys():
									rightSideIsGlyph = not rightSide.startswith("@")
									rightHasNoGroup = rightSideIsGlyph and not thisFont.glyphForId_(rightSide).leftKerningGroup
									rightMayBeDeleted = not (rightHasNoGroup and keepGrouplessKerning)

									removeGlyphGlyph = leftSideIsGlyph and rightSideIsGlyph and glyphGlyph and leftMayBeDeleted and rightMayBeDeleted
									removeGlyphGroup = leftSideIsGlyph and not rightSideIsGlyph and glyphGroup and leftMayBeDeleted
									removeGroupGlyph = not leftSideIsGlyph and rightSideIsGlyph and groupGlyph and rightMayBeDeleted
									
									if removeGroupGlyph or removeGlyphGroup or removeGlyphGlyph:
										pairsToBeRemoved.append((leftSide, rightSide))
							countOfDeletions = len(pairsToBeRemoved)
							totalCount += countOfDeletions
							print("🚫 Removing %i pairs in master ‘%s’..." % (countOfDeletions, thisMaster.name))
							for pair in pairsToBeRemoved:
								left, right = pair
								if not left.startswith("@"):
									left = thisFont.glyphForId_(left).name
								if not right.startswith("@"):
									right = thisFont.glyphForId_(right).name
								thisFont.removeKerningForPair(thisMaster.id, left, right)

			# Final report:
			Glyphs.showNotification(
				"Removed %i Exceptions" % (totalCount),
				"Processed %i font%s. Details in Macro Window" % (
					len(fonts),
					"" if len(fonts) != 1 else "s",
					),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Kerning Exceptions Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RemoveKerningExceptions()
