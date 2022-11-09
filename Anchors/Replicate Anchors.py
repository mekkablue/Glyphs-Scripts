#MenuTitle: Replicate Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-add anchors to selected glyphs. Specify a source glyph to replicate the anchors from.
"""

import vanilla, sys

class ReplicateAnchors(object):
	prefID = "com.mekkablue.ReplicateAnchors"
	prefDict = {
		# "prefName": defaultValue,
		"keepWindowOpen": 0,
		"sourceGlyphName": "A",
		"deleteAllExistingAnchors": 0,
		"overwriteExistingAnchors": 1,
		}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 180
		windowWidthResize = 300 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Replicate Anchors", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Replicate anchors in all selected glyphs:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.sourceGlyphNameText = vanilla.TextBox((inset, linePos + 2, 80, 14), "Source glyph:", sizeStyle='small', selectable=True)
		self.w.sourceGlyphName = vanilla.ComboBox((inset + 80, linePos - 1, -inset, 19), [g.name for g in Glyphs.font.glyphs], sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.overwriteExistingAnchors = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Overwrite existing anchors", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.deleteAllExistingAnchors = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Delete all existing anchors", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight

		self.w.keepWindowOpen = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Keep Window Open", value=False, callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Replicate", sizeStyle='regular', callback=self.ReplicateAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Replicate Anchors’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def updateGUI(self, sender=None):
		self.w.overwriteExistingAnchors.enable(not self.w.deleteAllExistingAnchors.get())

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			self.updateGUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def ReplicateAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Replicate Anchors’ could not write preferences.")

			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
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
				print("Replicate Anchors Report for %s" % report)
				print()

				sourceGlyph = thisFont.glyphs[sourceGlyphName]
				if not sourceGlyph:
					Message(
						title="Script Error",
						message="No glyph with name ‘%s’ found in font ‘%s’" % (sourceGlyphName, report[:report.find("\n")]),
						OKButton=None,
						)
				else:
					theseGlyphs = [l.parent for l in thisFont.selectedLayers if l.parent != sourceGlyph]
					for thisGlyph in theseGlyphs:
						layerCount = 0
						anchorCount = 0
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								layerCount += 1
								if deleteAllExistingAnchors:
									thisLayer.anchors = None
								masterID = thisLayer.master.id
								sourceLayer = sourceGlyph.layers[masterID]
								if sourceLayer:
									for thisAnchor in sourceLayer.anchors:
										if overwriteExistingAnchors or not thisLayer.anchors[thisAnchor.name]:
											anchorCount += 1
											newAnchor = thisAnchor.copy()
											thisLayer.anchors.append(newAnchor)
						print("🔠 replicated %i anchors of %s in %i layers of %s" % (
							anchorCount,
							sourceGlyphName,
							layerCount,
							thisGlyph.name,
							))

					if not keepWindowOpen:
						self.w.close()

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Replicate Anchors is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Replicate Anchors Error: %s" % e)
			import traceback
			print(traceback.format_exc())

ReplicateAnchors()
