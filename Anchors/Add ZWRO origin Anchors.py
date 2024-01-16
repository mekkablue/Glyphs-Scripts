# MenuTitle: Add ZWRO origin Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Insert *origin anchors for ZWRO in all combining marks of specified scripts.
"""

from AppKit import NSPoint, NSHeight
import vanilla
import sys
from GlyphsApp import Glyphs, GSAnchor, Message


def moveMacroWindowSeparator(pos=20):
	if Glyphs.versionNumber < 4:
		splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
		frame = splitview.frame()
		height = NSHeight(frame)
		splitview.setPosition_ofDividerAtIndex_(height * pos / 100.0, 0)


class AddZWROOriginAnchors(object):
	prefID = "com.mekkablue.AddZWROOriginAnchors"
	prefDict = {
		# "prefName": defaultValue,
		"offset": 0,
		"scripts": "latin, thai",
		"excludeTransformed": 1,
		"excludeComposites": 1,
		"useRSB": 0,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 210
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add ZWRO *origin Anchors",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 100
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Add *origin anchors on right edge of bounding box (or RSB):", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.offsetText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Horizontal offset:", sizeStyle="small", selectable=True)
		self.w.offset = vanilla.EditText((inset + tab, linePos, -inset, 19), "0", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.scriptsText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Marks of scripts:", sizeStyle="small", selectable=True)
		self.w.scripts = vanilla.EditText((inset + tab, linePos, -inset - 25, 19), "latin, thai", callback=self.SavePreferences, sizeStyle="small")
		self.w.updateScripts = vanilla.SquareButton((-inset - 20, linePos + 1, -inset, 18), "↺", sizeStyle="small", callback=self.updateScripts)
		linePos += lineHeight

		self.w.excludeTransformed = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Exclude marks used in transformed components", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.excludeComposites = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Exclude composites", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.useRSB = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Use RSB instead of bounding box", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Apply to all fonts", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Add Anchors", sizeStyle="regular", callback=self.AddZWROOriginAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Add ZWRO origin Anchors’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def updateScripts(self, sender=None):
		scripts = []
		for g in Glyphs.font.glyphs:
			if g.script and g.script not in scripts:
				scripts.append(g.script)
		self.w.scripts.set(", ".join(scripts))
		self.SavePreferences()

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

	def LoadPreferences(self):
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

	def isTransformed(self, componentName, font):
		for glyph in font.glyphs:
			for layer in glyph.layers:
				if layer.isMasterLayer or layer.isSpecialLayer:
					for component in layer.components:
						if component.componentName == componentName:
							if component.transform[:4] != (1.0, 0.0, 0.0, 1.0):
								return True
		return False

	def AddZWROOriginAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Add ZWRO origin Anchors’ could not write preferences.")

			# read prefs:
			for prefName in self.prefDict.keys():
				try:
					setattr(sys.modules[__name__], prefName, self.pref(prefName))
				except:
					fallbackValue = self.prefDict[prefName]
					print(f"⚠️ Could not set pref ‘{prefName}’, resorting to default value: ‘{fallbackValue}’.")
					setattr(sys.modules[__name__], prefName, fallbackValue)

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				if self.pref("allFonts"):
					theseFonts = Glyphs.fonts
				else:
					theseFonts = (thisFont, )

				for thisFont in theseFonts:
					filePath = thisFont.filepath
					if filePath:
						reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
					else:
						reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
					print(f"Add ZWRO origin Anchors Report for {reportName}")
					print()

					scriptNames = [scriptName.strip() for scriptName in self.pref("scripts").strip().split(",")]
					offset = int(self.pref("offset"))

					for glyph in thisFont.glyphs:
						if glyph.category == "Mark" and glyph.subCategory == "Nonspacing":
							if glyph.script in scriptNames or ("latin" in scriptNames and glyph.script is None):
								if self.pref("excludeComposites") and any([layer.components for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]):
									print(f"⚠️ Skipping {glyph.name} because it is a composite and composites are excluded.")
									continue
								if self.pref("excludeTransformed"):
									if self.isTransformed(glyph.name, thisFont):
										print(f"⚠️ Skipping {glyph.name} because it is used in a transformed component.")
										countAnchors = 0
										for layer in glyph.layers:
											originAnchor = layer.anchors["*origin"]
											if originAnchor:
												countAnchors += 1
												del layer.anchors["*origin"]
										if countAnchors:
											print(f"🚫 Removed {countAnchors} existing anchor{'' if countAnchors == 1 else 's'} in all layers of {glyph.name}.")
										continue
								for layer in glyph.layers:
									if layer.isMasterLayer or layer.isSpecialLayer:
										if layer.shapes and not self.pref("useRSB"):
											x = layer.bounds.origin.x + layer.bounds.size.width + offset
											anchorPosition = NSPoint(x, 0)
										else:
											# in empty glyphs, put *origin on RSB:
											anchorPosition = NSPoint(layer.width + offset, 0)
										anchor = GSAnchor("*origin", anchorPosition)
										layer.anchors.append(anchor)
										print(f"⚓️ {glyph.name}, {layer.name}: added {anchor.name} at {int(anchor.position.x)}x 0y")

			# Glyphs.showMacroWindow()
			moveMacroWindowSeparator()
			self.w.close()  # delete if you want window to stay open
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add ZWRO origin Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


AddZWROOriginAnchors()
