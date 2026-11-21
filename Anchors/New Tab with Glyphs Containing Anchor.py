# MenuTitle: New Tab with Glyphs Containing Anchor
__doc__ = """
Opens a new tab with all glyphs containing a specific anchor.
"""

import vanilla
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton, fontFileName, match


basicAnchors = (
	"top", "bottom", "center", "topleft", "topright", "ogonek",
	"_top", "_bottom", "_center", "_topleft", "_topright", "_ogonek",
)  # fmt: skip


class NewTabWithAnchor(mekkaObject):
	prefDict = {
		"anchorName": "ogonek",
		"scope": 0,
		"predict": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		windowWidthResize = 1000  # user can make the window this much wider
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"New Tab with Anchor",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.text_1 = vanilla.TextBox("auto", "Look for anchor:", sizeStyle="small")
		self.w.anchorName = vanilla.ComboBox("auto", list(basicAnchors), callback=self.SavePreferences, sizeStyle="small")
		self.w.anchorName.getNSComboBox().setNumberOfVisibleItems_(20)
		tooltip = "The name of the anchor to look for. Pick one from the list or type a name. Use * and ? as wildcards."
		self.w.text_1.setToolTip(tooltip)
		self.w.anchorName.setToolTip(tooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.updateAnchorList)
		self.w.updateButton.setToolTip("Fill the list with all anchors found in the frontmost font.")
		self.w.text_2 = vanilla.TextBox("auto", "and open a tab with all glyphs containing it.", sizeStyle="small")

		tooltip = "Which masters of which fonts to look at."
		self.w.scopeText = vanilla.TextBox("auto", "Apply to:", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton(
			"auto",
			("current master of current font", "⚠️ ALL masters of current font", "⚠️ ALL masters of ⚠️ ALL open fonts"),
			sizeStyle="small",
			callback=self.SavePreferences,
		)
		self.w.scopeText.setToolTip(tooltip)
		self.w.scope.setToolTip(tooltip)
		self.w.predict = vanilla.CheckBox("auto", "Predict", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.predict.setToolTip("Count the matching glyphs as you change the anchor name or scope, and show the number after this checkbox. Can be slow in big fonts and with many open fonts.")
		self.w.predictionText = vanilla.TextBox("auto", "Will find – glyphs.", sizeStyle="small")
		self.w.predictionText.getNSTextField().setTextColor_(NSColor.secondaryLabelColor())
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.secondaryLabelColor())

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.NewTabWithAnchorMain)
		self.w.runButton.setToolTip("Open a tab with all glyphs containing the anchor.")
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels: right-aligned, same width
		labelNames = ("text_1", "scopeText")
		widestLabel = "text_1"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[anchorName]-gap-[updateButton]-inset-|",
				"H:|-inset-[text_2]-(>=inset)-|",
				"H:|-inset-[scopeText]-gap-[scope]-inset-|",
				"H:|-inset-[predict]-gap-[predictionText]-(>=inset)-|",
				"H:|-inset-[status]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[anchorName]-row-[text_2]-row-[scope]-inset-[predict]-inset-[runButton]-inset-|",
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
				{"view1": self.w.scopeText, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.predictionText, "attribute1": "centerY", "view2": self.w.predict, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in width only. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes, with the height Auto Layout asks for:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		contentHeight = nsWindow.contentView().fittingSize().height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, contentHeight))

	def updateUI(self, sender=None):
		self.w.runButton.setTitle("Open Tabs" if self.prefInt("scope") == 2 else "Open Tab")
		self.w.predictionText.set(self.predictionText() if self.prefBool("predict") else "Will find – glyphs.")

	def predictionText(self):
		anchorName = self.w.anchorName.get()
		if not anchorName or not Glyphs.font:
			return "Will find – glyphs."
		scope = self.prefInt("scope")
		fonts = Glyphs.fonts if scope == 2 else (Glyphs.font, )
		total = 0
		for thisFont in fonts:
			for thisGlyph in self.glyphsWithAnchor(thisFont, anchorName, allMasters=scope > 0, verbose=False):
				total += 1
		return f"Will find {total} glyph{'' if total == 1 else 's'}."

	def setStatus(self, text):
		self.w.status.set(text)
		self.w.status.getNSTextField().displayIfNeeded()

	def updateAnchorList(self, sender=None):
		font = Glyphs.font
		if not font:
			self.setStatus("❌ No font open.")
			return
		self.setStatus(f"🛠️ Reading anchors of {len(font.glyphs)} glyphs…")
		anchorNames = set()
		for glyph in font.glyphs:
			for layer in glyph.layers:
				for anchor in layer.anchors:
					anchorNames.add(anchor.name)
		# basic anchors first, then the other anchors of the font, sorted:
		extraNames = sorted(anchorNames.difference(basicAnchors))
		foundBasicNames = [name for name in basicAnchors if name in anchorNames]
		self.w.anchorName.setItems(foundBasicNames + extraNames)
		self.setStatus(f"✅ Found {len(anchorNames)} anchors in the font.")

	def layerContainsAnchor(self, thisLayer, anchorName, verbose=True):
		for anchor in thisLayer.anchors:
			if match(anchorName, anchor.name):
				if verbose:
					print(f"\t🔠 Found {anchor.name} in {thisLayer.parent.name}, on layer ‘{thisLayer.name}’")
				return True
		return False

	def glyphsWithAnchor(self, thisFont, anchorName, allMasters, verbose=True):
		masterIds = [m.id for m in thisFont.masters] if allMasters else [thisFont.selectedFontMaster.id]
		for thisGlyph in thisFont.glyphs:
			if verbose:
				self.setStatus(f"🔠 {thisGlyph.name}")
			for masterId in masterIds:
				if self.layerContainsAnchor(thisGlyph.layers[masterId], anchorName, verbose):
					yield thisGlyph
					break

	def errMsg(self, errorMessage):
		self.setStatus(f"❌ {errorMessage}")
		message = f"The script 'New Tab with Anchor' encountered the following error: {errorMessage}"
		print(f"❌ {message}")
		Message(title="New Tab with Anchor Error", message=message, OKButton=None)

	def openTabForFont(self, thisFont, anchorName, allMasters):
		print(f"‘New Tab with Glyphs Containing Anchor’ Report for {fontFileName(thisFont)}")
		self.setStatus(f"🛠️ Looking for {anchorName} in {len(thisFont.glyphs)} glyphs…")
		glyphNames = [g.name for g in self.glyphsWithAnchor(thisFont, anchorName, allMasters)]
		if glyphNames:
			# create string with slash-escaped names:
			thisFont.newTab("/" + "/".join(glyphNames))
		else:
			print(f"\t⚠️ No glyph with anchor ‘{anchorName}’ found.")
		return len(glyphNames)

	def NewTabWithAnchorMain(self, sender):
		if not Glyphs.font:
			self.errMsg("No font open. Please open a font and try again.")
			return

		try:
			self.SavePreferences()
			anchorName = self.pref("anchorName")
			scope = self.prefInt("scope")

			if not anchorName:
				self.errMsg("No anchor name specified. Please enter an anchor name before pressing the button.")
				return

			fonts = Glyphs.fonts if scope == 2 else (Glyphs.font, )
			total = 0
			for thisFont in fonts:
				total += self.openTabForFont(thisFont, anchorName, allMasters=scope > 0)

			if total:
				self.setStatus(f"✅ Found {total} glyphs with {anchorName}.")
			else:
				self.setStatus(f"⚠️ No glyph with anchor {anchorName}.")
				Message(
					title="Could not find anchor",
					message=f"No glyph with anchor ‘{anchorName}’ found.",
					OKButton=None,
				)
		except Exception as e:
			self.errMsg(e)
			import traceback
			print(traceback.format_exc())


Glyphs.clearLog()  # clears macro window log
NewTabWithAnchor()
