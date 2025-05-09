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
		"openTab": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 180
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add *origin Anchors to Combining Marks",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab = 12, 15, 22, 95
		self.w.whereText = vanilla.TextBox((inset, linePos+1, 125, 14), "Add *origin anchors at", sizeStyle="small", selectable=True)
		self.w.where = vanilla.PopUpButton((inset+125, linePos-1, -inset, 17), positions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Where on the baseline you want the *origin anchor to go in each combining mark. Typically, in marks for an RTL script, you want it to be on the left; and in LTR marks, you want it to be on the right side of the shape."
		self.w.whereText.getNSTextField().setToolTip_(tooltip)
		self.w.where.getNSPopUpButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.offsetText = vanilla.TextBox((inset, linePos+2, tab, 14), "Horizontal offset", sizeStyle="small", selectable=True)
		self.w.offset = vanilla.EditText((inset+tab, linePos-1, -inset, 19), "0", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "The number entered here will be added to the calculated position. Negative numbers for moving to the left, positive numbers for moving the anchor further to the right."
		self.w.offsetText.getNSTextField().setToolTip_(tooltip)
		self.w.offset.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.scriptsText = vanilla.TextBox((inset, linePos+2, tab, 14), "Marks of scripts", sizeStyle="small", selectable=True)
		self.w.scripts = vanilla.EditText((inset+tab, linePos-1, -inset-22, 19), "latin, thai", callback=self.SavePreferences, sizeStyle="small")
		self.w.updateScripts = UpdateButton((-inset-16, linePos-2, -inset, 18), callback=self.updateScripts)
		tooltip = "Comma-separated list of scripts, e.g. ‘latin, thai’. Only marks whose script will match one listed here will be processed. Leave empty for ALL combining marks. Click the ⟳ button to populate with all scripts in the frontmost font."
		self.w.scriptsText.getNSTextField().setToolTip_(tooltip)
		self.w.scripts.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.excludeTransformed = vanilla.CheckBox((inset+2, linePos-1, -inset, 20), "Exclude marks used in transformed components", value=True, callback=self.SavePreferences, sizeStyle="small")
		tooltip = "Do not add *origin anchors to marks that themselves are being used as scaled, slanted or rotated components inside other glyphs. Leave this on unless you know what you are doing, and you will be doing an insane amount of testing."
		self.w.excludeTransformed.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.excludeComposites = vanilla.CheckBox((inset+2, linePos-1, -inset, 20), "Exclude composites", value=True, callback=self.SavePreferences, sizeStyle="small")
		tooltip = "Ignore marks that contain components."
		self.w.excludeComposites.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset+2, linePos-1, 150, 20), "⚠️ Apply to ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.getNSButton().setToolTip_("If checked, will process all fonts currently open. Otherwise only the frontmost font.")
		self.w.openTab = vanilla.CheckBox((inset+150, linePos-1, -inset, 20), "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.getNSButton().setToolTip_("Will open a tab with all processed marks in every font processed.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120-inset, -20-inset, -inset, -inset), "Add Anchors", callback=self.AddZWROOriginAnchorsMain)
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
				return

			openTab = bool(self.pref("openTab"))
			excludeComposites = bool(self.pref("excludeComposites"))
			excludeTransformed = bool(self.pref("excludeTransformed"))
			
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

				scriptNames = [scriptName.strip() for scriptName in self.pref("scripts").split(",") if scriptName.strip()]
				offset = self.prefInt("offset")
				where = self.prefInt("where")
				glyphsForTab = []

				for glyph in thisFont.glyphs:
					if glyph.category != "Mark" or glyph.subCategory != "Nonspacing":
						continue
					addToTab = False
					if glyph.script in scriptNames or ("latin" in scriptNames and glyph.script is None) or not scriptNames:
						if excludeComposites and any([layer.components for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]):
							print(f"⚠️ Skipping {glyph.name} because it is a composite and composites are excluded.")
							continue

						if excludeTransformed:
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
								addToTab = True
								x = 0  # default where = 5; left sidebearing
								if where == 0:
									# "right sidebearing", # 0
									x = layer.width
								elif where == 1:
									# "right bbox edge",   # 1
									if layer.shapes:
										x = layer.bounds.origin.x + layer.bounds.size.width
								elif where == 2:
									# "bbox center",       # 2
									if layer.shapes:
										x = layer.bounds.origin.x + layer.bounds.size.width / 2
								elif where == 3:
									# "width center",      # 3
									x = layer.width / 2
								elif where == 4:
									# "left bbox edge",    # 4
									if layer.shapes:
										x = layer.bounds.origin.x
								x += offset
								anchorPosition = NSPoint(x, 0)
								anchor = GSAnchor("*origin", anchorPosition)
								layer.anchors.append(anchor)
								print(f"⚓️ {glyph.name}, {layer.name}: added {anchor.name} at {int(anchor.position.x)}x 0y")

					if addToTab:
						glyphsForTab.append(glyph.name)

				if glyphsForTab:
					thisFont.newTab("/" + "/".join(glyphsForTab))

			# Glyphs.showMacroWindow()
			moveMacroWindowSeparator()
			self.w.close()
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Add ZWRO origin Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


AddZWROOriginAnchors()
