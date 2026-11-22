# MenuTitle: New OT Class with Selected Glyphs
__doc__ = """
Creates a new OT class containing the selected glyphs.
"""

import vanilla
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, GSClass, Message
from mekkablue import mekkaObject, makeWindowResizable


class OTClassCreator(mekkaObject):
	prefDict = {
		"otClassName": "xxxx",
		"overwrite": True,
		"keepOpen": True,
	}

	def __init__(self):
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Make OT Class from Selected Glyphs",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		self.w.classNameLabel = vanilla.TextBox("auto", "OT class name:", sizeStyle="small")
		self.w.otClassName = vanilla.EditText("auto", "xxxx", sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "Name of the new OT class, without the at sign. Use only letters, figures, period and underscore, and do not start with a figure."
		self.w.classNameLabel.setToolTip(tooltipText)
		self.w.otClassName.setToolTip(tooltipText)
		self.w.overwrite = vanilla.CheckBox("auto", "Overwrite existing class", sizeStyle="small", callback=self.SavePreferences, value=True)
		self.w.overwrite.setToolTip("If checked, replaces the glyphs of an existing class with the same name. Otherwise a name that is already taken cannot be used.")
		self.w.keepOpen = vanilla.CheckBox("auto", "Keep this window open", sizeStyle="small", callback=self.SavePreferences, value=True)
		self.w.keepOpen.setToolTip("Keeps this window open after the class is created, so you can create more classes.")
		self.w.classNameCheck = vanilla.TextBox("auto", "Class name appears to be ok.", sizeStyle="small")
		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())
		self.w.status.setToolTip("Shows the progress and the result of the run.")
		self.w.runButton = vanilla.Button("auto", "Create", sizeStyle="small", callback=self.createClass)
		self.w.runButton.setToolTip("Creates the OT class with the selected glyphs.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		nsLabel = self.w.classNameLabel.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[classNameLabel]-gap-[otClassName]-gap-[runButton(>=65)]-inset-|",
				"H:[overwrite]-(>=inset)-|",
				"H:[keepOpen]-(>=inset)-|",
				"H:|-inset-[classNameCheck]-inset-|",
				"H:|-inset-[status]-inset-|",
				"V:|-inset-[otClassName]-row-[overwrite]-checkRow-[keepOpen]-row-[classNameCheck]-checkRow-[status]-inset-|",
				{"view1": self.w.classNameLabel, "attribute1": "centerY", "view2": self.w.otClassName, "attribute2": "centerY"},
				{"view1": self.w.runButton, "attribute1": "centerY", "view2": self.w.otClassName, "attribute2": "centerY"},
				{"view1": self.w.overwrite, "attribute1": "left", "view2": self.w.otClassName, "attribute2": "left"},
				{"view1": self.w.keepOpen, "attribute1": "left", "view2": self.w.otClassName, "attribute2": "left"},
			],
			metrics={"inset": 15, "gap": 8, "row": 8, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# validates the class name and enables the button accordingly
		myClassName = self.w.otClassName.get()
		font = Glyphs.font
		existingClasses = [c.name for c in font.classes] if font else []

		if myClassName in existingClasses:
			if not self.w.overwrite.get():
				self.w.runButton.enable(False)
				self.w.classNameCheck.set("Class name already exists.")
			else:
				self.w.runButton.enable(True)
				self.w.classNameCheck.set("Will overwrite existing class.")
		elif len(myClassName) == 0:
			self.w.runButton.enable(False)
			self.w.classNameCheck.set("Class name too short.")
		elif self.checkString(myClassName):
			self.w.runButton.enable(True)
			self.w.classNameCheck.set("Class name appears to be ok.")
		elif myClassName[0] in "0123456789":
			self.w.runButton.enable(False)
			self.w.classNameCheck.set("Class name must not start with a figure.")
		else:
			self.w.runButton.enable(False)
			self.w.classNameCheck.set("Illegal characters. Only use A-Z, a-z, figures, period, underscore.")

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)

	def checkString(self, testString, ok=True):
		allowedChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890._"

		if len(testString) > 1:
			return self.checkString(testString[:-1], ok) and (testString[-1] in allowedChars)
		else:
			# first char must not be a figure
			return (testString[-1] in allowedChars and testString[-1] not in "1234567890")

	def createClass(self, sender):
		font = Glyphs.font
		if not font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			self.setStatus("⚠️ No font open.")
			return

		glyphNames = [x.parent.name for x in font.selectedLayers]
		classNames = [c.name for c in font.classes]

		newClassName = self.w.otClassName.get()
		classCode = " ".join(glyphNames)
		self.setStatus(f"🛠️ Processing {len(glyphNames)} glyphs…")

		if newClassName in classNames:
			print("Changing class", newClassName, "to these glyphs:", classCode)
			font.classes[newClassName].code = classCode
			self.setStatus(f"✅ Updated class @{newClassName} with {len(glyphNames)} glyphs.")

		else:
			print("Creating class", newClassName, "with these glyphs:", classCode)
			newClass = GSClass()
			newClass.name = newClassName
			newClass.code = classCode
			font.classes.append(newClass)
			self.setStatus(f"✅ Created class @{newClassName} with {len(glyphNames)} glyphs.")

		if not self.w.keepOpen.get():
			self.w.close()


OTClassCreator()
