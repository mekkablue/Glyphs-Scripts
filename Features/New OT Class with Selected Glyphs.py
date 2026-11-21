# MenuTitle: New OT Class with Selected Glyphs
__doc__ = """
Creates a new OT class containing the selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, GSClass, Message
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut


class OTClassCreator(object):

	def __init__(self):
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow((windowWidth, windowHeight), "Make OT Class from Selected Glyphs")

		self.w.text_otclass = vanilla.TextBox("auto", "OT class name:", sizeStyle='small')
		self.w.class_name = vanilla.EditText("auto", "xxxx", sizeStyle='small', callback=self.buttonCheck)
		self.w.overwrite_check = vanilla.CheckBox("auto", "Overwrite existing class", sizeStyle='small', callback=self.buttonCheck, value=True)
		self.w.keep_window = vanilla.CheckBox("auto", "Keep this window open", sizeStyle='small', callback=None, value=True)
		self.w.class_name_check = vanilla.TextBox("auto", "Class name appears to be ok.", sizeStyle='small')
		self.w.make_button = vanilla.Button("auto", "Create", sizeStyle='small', callback=self.createClass)
		self.w.setDefaultButton(self.w.make_button)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		nsLabel = self.w.text_otclass.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_otclass]-gap-[class_name]-gap-[make_button(>=65)]-inset-|",
				"H:[overwrite_check]-(>=inset)-|",
				"H:[keep_window]-(>=inset)-|",
				"H:|-inset-[class_name_check]-inset-|",
				"V:|-inset-[class_name]-row-[overwrite_check]-checkRow-[keep_window]-row-[class_name_check]-inset-|",
				{"view1": self.w.text_otclass, "attribute1": "centerY", "view2": self.w.class_name, "attribute2": "centerY"},
				{"view1": self.w.make_button, "attribute1": "centerY", "view2": self.w.class_name, "attribute2": "centerY"},
				{"view1": self.w.overwrite_check, "attribute1": "left", "view2": self.w.class_name, "attribute2": "left"},
				{"view1": self.w.keep_window, "attribute1": "left", "view2": self.w.class_name, "attribute2": "left"},
			],
			metrics={"inset": 15, "gap": 8, "row": 8, "checkRow": 5},
		)

		self.w.open()
		self.buttonCheck(self.w.class_name)

	def buttonCheck(self, sender):
		# the sender is either the name field or the overwrite checkbox, so always ask the field:
		myClassName = self.w.class_name.get()
		font = Glyphs.font
		existingClasses = [c.name for c in font.classes] if font else []

		if myClassName in existingClasses:
			if not self.w.overwrite_check.get():
				self.w.make_button.enable(False)
				self.w.class_name_check.set("Class name already exists.")
			else:
				self.w.make_button.enable(True)
				self.w.class_name_check.set("Will overwrite existing class.")
		elif len(myClassName) == 0:
			self.w.make_button.enable(False)
			self.w.class_name_check.set("Class name too short.")
		elif self.checkstring(myClassName):
			self.w.make_button.enable(True)
			self.w.class_name_check.set("Class name appears to be ok.")
		elif myClassName[0] in "0123456789":
			self.w.make_button.enable(False)
			self.w.class_name_check.set("Class name must not start with a figure.")
		else:
			self.w.make_button.enable(False)
			self.w.class_name_check.set("Illegal characters. Only use A-Z, a-z, figures, period, underscore.")

	def checkstring(self, teststring, ok=True):
		allowedchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890._"

		if len(teststring) > 1:
			return self.checkstring(teststring[:-1], ok) and (teststring[-1] in allowedchars)
		else:
			# first char must not be a figure
			return (teststring[-1] in allowedchars and teststring[-1] not in "1234567890")

	def createClass(self, sender):
		Font = Glyphs.font
		if not Font:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		listOfGlyphNames = [x.parent.name for x in Font.selectedLayers]
		listOfClasses = Font.classes
		listOfClassNames = [c.name for c in listOfClasses]

		myClassName = self.w.class_name.get()
		myClassCode = " ".join(listOfGlyphNames)

		if myClassName in listOfClassNames:
			print("Changing class", myClassName, "to these glyphs:", myClassCode)
			Font.classes[myClassName].code = myClassCode

		else:
			print("Creating class", myClassName, "with these glyphs:", myClassCode)
			myNewClass = GSClass()
			myNewClass.name = myClassName
			myNewClass.code = myClassCode
			Font.classes.append(myNewClass)

		if not self.w.keep_window.get():
			self.w.close()


OTClassCreator()
