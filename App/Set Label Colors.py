# MenuTitle: Set Label Colors
__doc__ = """
Override the label colors for glyphs and layers.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentCenter,
)
from Foundation import NSColor, NSArchiver, NSUnarchiver, NSMutableArray
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class SetLabelColors(mekkaObject):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Set Glyph Label Colors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		components = (("red", "R"), ("green", "G"), ("blue", "B"), ("alpha", "A"))
		rules = []

		# column headers:
		for name, letter in components:
			header = vanilla.TextBox("auto", letter, sizeStyle="small", selectable=False)
			header.getNSTextField().setAlignment_(NSTextAlignmentCenter)
			setattr(self.w, f"{name}Text", header)

		# one row per label color: color dot and four fields
		for i in range(1, 13):
			dot = vanilla.TextBox("auto", "◼︎", sizeStyle="small")
			dot.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			dot.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
			setattr(self.w, f"color{i:02d}", dot)
			dot.setToolTip(f"Preview of label color {i}.")
			for name, _ in components:
				field = vanilla.EditText("auto", "0.5", sizeStyle="small", callback=self.textFieldAction)
				field.setToolTip(f"{name.capitalize()} of label color {i}, from 0 to 1.")
				setattr(self.w, f"{name}{i:02d}", field)

			rules.append(f"H:|-inset-[color{i:02d}]-gap-[red{i:02d}(48)]-gap-[green{i:02d}(48)]-gap-[blue{i:02d}(48)]-gap-[alpha{i:02d}(48)]-inset-|")
			for viewName in (f"color{i:02d}", f"green{i:02d}", f"blue{i:02d}", f"alpha{i:02d}"):
				rules.append({"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, f"red{i:02d}"), "attribute2": "centerY"})

		# headers sit above their columns:
		for name, _ in components:
			rules.append({"view1": getattr(self.w, f"{name}Text"), "attribute1": "centerX", "view2": getattr(self.w, f"{name}01"), "attribute2": "centerX"})

		# buttons that apply the value of the last line to all lines:
		tooltip = "Type in a value in the LAST line and click this button to apply it to all lines."
		for name, _ in components:
			button = vanilla.SquareButton("auto", "↑ ALL", sizeStyle="mini", callback=self.setAll)
			button.setToolTip(tooltip)
			setattr(self.w, f"{name[0]}All", button)
			rules.append({"view1": button, "attribute1": "left", "view2": getattr(self.w, f"{name}12"), "attribute2": "left"})
			rules.append({"view1": button, "attribute1": "width", "view2": getattr(self.w, f"{name}12"), "attribute2": "width"})
			if name != "red":
				rules.append({"view1": button, "attribute1": "centerY", "view2": self.w.rAll, "attribute2": "centerY"})

		# Run Button:
		self.w.resetButton = vanilla.Button("auto", "Reset", callback=self.resetColors)
		self.w.resetButton.setToolTip("Restores the default label colors.")
		self.w.runButton = vanilla.Button("auto", "Set", callback=self.SetLabelColorsMain)
		self.w.runButton.setToolTip("Applies the colors. Glyphs needs a restart for them to take effect.")
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# one vertical chain, with the red column as its backbone:
		redFields = "-row-".join(f"[red{i:02d}]" for i in range(1, 13))
		rules += [
			"H:|-(>=inset)-[resetButton(>=70)]-gap-[runButton(>=70)]-inset-|",
			f"V:|-gap-[redText]-headerGap-{redFields}-allGap-[rAll]-inset-[runButton]-inset-|",
			"V:[resetButton]-inset-|",
		]
		for name, _ in components[1:]:
			rules.append({"view1": getattr(self.w, f"{name}Text"), "attribute1": "centerY", "view2": self.w.redText, "attribute2": "centerY"})

		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 3, "headerGap": 4, "allGap": 6})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def resetColors(self, sender=None):
		Glyphs.defaults["LabelColors"] = None
		self.LoadPreferences()
		Glyphs.showNotification("Set Label Colors", "Label colors reset. Glyphs needs a restart for changes to take effect.")

	def currentlyStoredColors(self, sender=None):
		# reset to defaults if nothing stored:

		labelColorDatas = Glyphs.defaults["LabelColors"]
		if labelColorDatas:
			labelColors = []
			for colorData in labelColorDatas:
				color = NSUnarchiver.unarchiveObjectWithData_(colorData)
				labelColors.append(color)
		else:
			labelColors = [
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.85, 0.26, 0.06, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.99, 0.62, 0.11, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.65, 0.48, 0.20, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.97, 0.90, 0.00, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.67, 0.95, 0.38, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.04, 0.57, 0.04, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.06, 0.60, 0.98, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.00, 0.20, 0.88, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.50, 0.09, 0.79, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.98, 0.36, 0.67, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.75, 0.75, 0.75, 1.0),
				NSColor.colorWithDeviceRed_green_blue_alpha_(0.25, 0.25, 0.25, 1.0),
			]
		return labelColors

	def setAll(self, sender=None):
		names = {
			self.w.rAll: "red",
			self.w.gAll: "green",
			self.w.bAll: "blue",
			self.w.aAll: "alpha",
		}
		name = names.get(sender)
		if name:
			originalValue = getattr(self.w, f"{name}12").get()
			for i in range(1, 12):
				getattr(self.w, f"{name}{i:02d}").set(originalValue)
		self.updateColorDots()

	def textFieldAction(self, sender=None):
		self.updateColorDots()

	def updateColorDots(self):
		# sets the dots
		for i in range(12):
			labelColor = self.labelColorFromUIAtIndex(i)
			if labelColor is None:
				continue  # incomplete input while typing: keep the dot as it is
			getattr(self.w, f"color{i + 1:02d}").getNSTextField().setTextColor_(labelColor)

	def uiAttributeKeys(self, index):
		index += 1  # the labels start at 1
		color = f"color{index:02d}"
		r = f"red{index:02d}"
		g = f"green{index:02d}"
		b = f"blue{index:02d}"
		a = f"alpha{index:02d}"
		return color, r, g, b, a

	def labelColorFromUIAtIndex(self, idx):
		"""Returns the NSColor entered in the UI, or None if one of the four values is not a number."""
		_, rName, gName, bName, aName = self.uiAttributeKeys(idx)
		try:
			red, green, blue, alpha = (max(0.0, min(1.0, float(getattr(self.w, name).get().replace(",", ".")))) for name in (rName, gName, bName, aName))
		except ValueError:
			return None
		return NSColor.colorWithDeviceRed_green_blue_alpha_(red, green, blue, alpha)

	def labelColorArchivesFromUI(self):
		"""Returns the archived colors from the UI, or None if any of the 12 colors is incomplete."""
		labelColors = NSMutableArray.new()
		for i in range(12):
			labelColor = self.labelColorFromUIAtIndex(i)
			if labelColor is None:
				return None
			colorData = NSArchiver.archivedDataWithRootObject_(labelColor)
			labelColors.addObject_(colorData)
		return labelColors

	def LoadPreferences(self):
		try:
			labelColors = self.currentlyStoredColors()
			for i, color in enumerate(labelColors):
				r = color.redComponent()
				g = color.greenComponent()
				b = color.blueComponent()
				a = color.alphaComponent()

				colorName, rName, gName, bName, aName = self.uiAttributeKeys(i)
				getattr(self.w, rName).set("%.2f" % r)
				getattr(self.w, gName).set("%.2f" % g)
				getattr(self.w, bName).set("%.2f" % b)
				getattr(self.w, aName).set("%.2f" % a)
				getattr(self.w, colorName).getNSTextField().setTextColor_(color)
			return True
		except Exception:
			import traceback
			print(traceback.format_exc())
			return False

	def SetLabelColorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			labelColors = self.labelColorArchivesFromUI()
			if labelColors is None:
				Message(title="Invalid Color Value", message="⚠️ All fields must contain numbers between 0 and 1.", OKButton=None)
				return
			Glyphs.defaults["LabelColors"] = labelColors

			Message(title="New Label Colors Set", message="✅ The new label colors have been set.\n⚠️ Glyphs needs a restart for changes to take effect.", OKButton=None)
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Set Label Colors Error: {e}")
			import traceback
			print(traceback.format_exc())


SetLabelColors()
