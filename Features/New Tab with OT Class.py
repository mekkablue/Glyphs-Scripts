# MenuTitle: New Tab with OT Class
__doc__ = """
Open a new tab with all glyphs contained in a specific OpenType class.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut


class NewTabWithOTClass(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"New Tab with OT Class",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		self.w.text = vanilla.TextBox("auto", "Pick an OT class", sizeStyle='small')
		self.w.classMenu = vanilla.PopUpButton("auto", self.currentFontClasses(None), callback=None, sizeStyle='small')
		self.w.updateButton = UpdateButton("auto", callback=self.populateClassMenu)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "New Tab", callback=self.NewTabWithOTClassMain)
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the popup takes the leftover width:
		nsLabel = self.w.text.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		self.w.classMenu.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text]-gap-[classMenu(>=80)]-gap-[updateButton]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[runButton]-inset-|",
				{"view1": self.w.text, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.classMenu, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": 12, "gap": 8},
		)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def currentFontClasses(self, sender):
		self.font = Glyphs.font
		if not self.font:
			return []
		classNames = [c.name for c in self.font.classes]
		return classNames

	def populateClassMenu(self, sender):
		otClasses = self.currentFontClasses(None)
		self.w.classMenu.setItems(otClasses)
		if self.w.classMenu.getItems():
			self.w.classMenu.set(0)

	def NewTabWithOTClassMain(self, sender):
		try:
			classNames = self.w.classMenu.getItems()
			if not classNames or not self.font:
				Message(
					title="No OT Class Found",
					message=u"Found no class to open in a new tab. Please activate a font, press the ↺ update button, and pick a class from the menu.",
					OKButton=None
				)
			else:
				selectedClass = classNames[self.w.classMenu.get()]
				for thisClass in self.font.classes:
					if thisClass.name == selectedClass:
						glyphNames = thisClass.code.split()
						escapedGlyphNames = "/" + "/".join(glyphNames)
						self.font.newTab(escapedGlyphNames)
				self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("New Tab with OT Class Error: %s" % e)
			import traceback
			print(traceback.format_exc())


NewTabWithOTClass()
