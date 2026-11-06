# MenuTitle: Add ZWRO *origin Anchors
__doc__ = """
Insert *origin anchors for ZWRO in all combining marks of specified scripts.
"""

from AppKit import (
	NSPoint, NSTextAlignmentRight, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut,
	NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical,
)
import vanilla
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, newAnchorWithName, UpdateButton, reportFontName, setMacroDivider


def moveMacroWindowSeparator(pos=20):
	setMacroDivider(pos / 100.0)


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
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Add *origin Anchors to Combining Marks",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.whereText = vanilla.TextBox("auto", "Add *origin anchors at", sizeStyle="small", selectable=True)
		self.w.where = vanilla.PopUpButton("auto", positions, sizeStyle="small", callback=self.SavePreferences)
		tooltip = "Where on the baseline you want the *origin anchor to go in each combining mark. Typically, in marks for an RTL script, you want it to be on the left; and in LTR marks, you want it to be on the right side of the shape."
		self.w.whereText.setToolTip(tooltip)
		self.w.where.setToolTip(tooltip)

		self.w.offsetText = vanilla.TextBox("auto", "Horizontal offset", sizeStyle="small", selectable=True)
		self.w.offset = vanilla.EditText("auto", "0", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "The number entered here will be added to the calculated position. Negative numbers for moving to the left, positive numbers for moving the anchor further to the right."
		self.w.offsetText.setToolTip(tooltip)
		self.w.offset.setToolTip(tooltip)

		self.w.scriptsText = vanilla.TextBox("auto", "Marks of scripts", sizeStyle="small", selectable=True)
		self.w.scripts = vanilla.EditText("auto", "latin, thai", callback=self.SavePreferences, sizeStyle="small")
		self.w.scripts.getNSTextField().setPlaceholderString_("latin, thai")
		self.w.updateScripts = UpdateButton("auto", callback=self.updateScripts)
		tooltip = "Comma-separated list of scripts, e.g. ‘latin, thai’. Only marks whose script will match one listed here will be processed. Leave empty for ALL combining marks. Click the ⟳ button to populate with all scripts in the frontmost font."
		self.w.scriptsText.setToolTip(tooltip)
		self.w.scripts.setToolTip(tooltip)
		self.w.updateScripts.setToolTip(tooltip)

		self.w.excludeTransformed = vanilla.CheckBox("auto", "Exclude marks used in transformed components", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeTransformed.setToolTip("Do not add *origin anchors to marks that themselves are being used as scaled, slanted or rotated components inside other glyphs. Leave this on unless you know what you are doing, and you will be doing an insane amount of testing.")

		self.w.excludeComposites = vanilla.CheckBox("auto", "Exclude composites", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.excludeComposites.setToolTip("Ignore marks that contain components.")

		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ Apply to ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allFonts.setToolTip("If checked, will process all fonts currently open. Otherwise only the frontmost font.")
		self.w.openTab = vanilla.CheckBox("auto", "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("Will open a tab with all processed marks in every font processed.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Add Anchors", callback=self.AddZWROOriginAnchorsMain)
		self.w.setDefaultButton(self.w.runButton)

		# Labels: right-aligned, all as wide as the widest one
		labelNames = ("whereText", "offsetText", "scriptsText")
		widestLabel = "whereText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# checkboxes default to stretching vertically; let the window take its height from the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[whereText]-gap-[where]-inset-|",
				"H:|-inset-[offsetText]-gap-[offset]-inset-|",
				"H:|-inset-[scriptsText]-gap-[scripts]-gap-[updateScripts]-inset-|",
				"H:|-inset-[excludeTransformed]-(>=inset)-|",
				"H:|-inset-[excludeComposites]-(>=inset)-|",
				"H:|-inset-[allFonts]-gap-[openTab]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[where]-row-[offset]-row-[scripts]-row-[excludeTransformed]-checkRow-[excludeComposites]-checkRow-[allFonts]-inset-[runButton]-inset-|",
				{"view1": self.w.whereText, "attribute1": "centerY", "view2": self.w.where, "attribute2": "centerY"},
				{"view1": self.w.offsetText, "attribute1": "centerY", "view2": self.w.offset, "attribute2": "centerY"},
				{"view1": self.w.scriptsText, "attribute1": "centerY", "view2": self.w.scripts, "attribute2": "centerY"},
				{"view1": self.w.updateScripts, "attribute1": "centerY", "view2": self.w.scripts, "attribute2": "centerY"},
				{"view1": self.w.openTab, "attribute1": "centerY", "view2": self.w.allFonts, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": 15, "gap": 8, "row": 6, "checkRow": 5},
		)

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
				reportName = reportFontName(thisFont)
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
								anchor = newAnchorWithName("*origin", anchorPosition)
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
