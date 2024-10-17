# MenuTitle: Add ZWRO origin Anchors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Insert *origin anchors for ZWRO in all combining marks of specified scripts.
"""

from AppKit import NSPoint, NSHeight
import vanilla
from GlyphsApp import Glyphs, GSAnchor, Message
from mekkablue import mekkaObject, UpdateButton


def moveMacroWindowSeparator(pos=20):
	if Glyphs.versionNumber < 4:
		splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
		frame = splitview.frame()
		height = NSHeight(frame)
		splitview.setPosition_ofDividerAtIndex_(height * pos / 100.0, 0)


positions = (
	"right sidebearing",  # 0
	"right bbox edge",    # 1
	"bbox center",        # 2
	"width center",       # 3
	"left bbox edge",     # 4
	"left sidebearing",   # 5
)


class AddZWROOriginAnchors(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"where": 1,  # right bbox edge
		"offset": 0,
		"scripts": "latin, thai",
		"excludeTransformed": 1,
		"excludeComposites": 1,
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add ZWRO *origin Anchors",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 95
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, 125, 14), "Add *origin anchors at", sizeStyle="small", selectable=True)
		self.w.where = vanilla.PopUpButton((inset + 125, linePos, -inset, 17), positions, sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.offsetText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Horizontal offset", sizeStyle="small", selectable=True)
		self.w.offset = vanilla.EditText((inset + tab, linePos, -inset, 19), "0", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.scriptsText = vanilla.TextBox((inset, linePos + 2, tab, 14), "Marks of scripts", sizeStyle="small", selectable=True)
		self.w.scripts = vanilla.EditText((inset + tab, linePos, -inset - 22, 19), "latin, thai", callback=self.SavePreferences, sizeStyle="small")
		self.w.updateScripts = UpdateButton((-inset - 16, linePos - 1, -inset, 18), callback=self.updateScripts)
		linePos += lineHeight

		self.w.excludeTransformed = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Exclude marks used in transformed components", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.excludeComposites = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Exclude composites", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Apply to all fonts", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Add Anchors", callback=self.AddZWROOriginAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateScripts(self, sender=None):
		scripts = []
		for g in Glyphs.font.glyphs:
			if g.script and g.script not in scripts:
				scripts.append(g.script)
		self.w.scripts.set(", ".join(scripts))
		self.SavePreferences()

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
			self.SavePreferences()

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
					offset = self.prefInt("offset")
					where = self.prefInt("where")

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
										if layer.shapes:
											if where == 0:
												# "right sidebearing", # 0
												x = layer.width
											elif where == 1:
												# "right bbox edge",   # 1
												x = layer.bounds.origin.x + layer.bounds.size.width
											elif where == 2:
												# "bbox center",       # 2
												x = layer.bounds.origin.x + layer.bounds.size.width / 2
											elif where == 3:
												# "width center",      # 3
												x = layer.width / 2
											elif where == 4:
												# "left bbox edge",    # 4
												x = layer.bounds.origin.x
											else:
												# "left sidebearing",  # 5
												x = 0
											x += offset
											anchorPosition = NSPoint(x, 0)
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
