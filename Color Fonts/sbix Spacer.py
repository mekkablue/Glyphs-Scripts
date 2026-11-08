# MenuTitle: sbix Spacer
__doc__ = """
Batch-set sbix positions and glyph widths.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSAffineTransform,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSRect,
	NSSize,
)
from Foundation import NSNumberFormatter, NSPoint


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


class sbixSpacer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"allGlyphs": 0,
		"allMasters": 0,
		"insertMarkers": 1,
		"verticalShift": 0,
		"verticalShiftValue": -100,
		"resetWidths": 0,
		"preferredSizeForWidth": 128,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"sbix Spacer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.insertMarkers = vanilla.CheckBox("auto", "Reset master layer and insert markers for sbix bounds", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.resetWidths = vanilla.CheckBox("auto", "Reset sidebearings to image widths", value=True, callback=self.SavePreferences, sizeStyle='small')

		tooltipText = "Size of the iColor layer (e.g. 128 for ‘iColor 128’) used as reference for the width."
		self.w.preferredSizeForWidthText = vanilla.TextBox("auto", "Preferred iColor size for width reference", sizeStyle='small', selectable=True)
		self.w.preferredSizeForWidth = SteppingEditText("auto", "128", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=1))
		self.w.preferredSizeForWidthText.setToolTip(tooltipText)
		self.w.preferredSizeForWidth.setToolTip(tooltipText)

		tooltipText = "Shift the master layer vertically by this many units."
		self.w.verticalShift = vanilla.CheckBox("auto", "Vertical sbix shift", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.verticalShiftValue = SteppingEditText("auto", "-100", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter())
		self.w.verticalShift.setToolTip(tooltipText)
		self.w.verticalShiftValue.setToolTip(tooltipText)

		self.w.allGlyphs = vanilla.CheckBox("auto", "Include all iColor glyphs in font (ignore glyph selection)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allMasters = vanilla.CheckBox("auto", "Include all masters (otherwise only current master)", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Buttons:
		self.w.help = vanilla.HelpButton("auto", callback=self.openURL)

		self.w.runButton = vanilla.Button("auto", "Apply", callback=self.sbixSpacerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		nsLabel = self.w.preferredSizeForWidthText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[insertMarkers]-(>=inset)-|",
				"H:|-inset-[resetWidths]-(>=inset)-|",
				"H:|-inset-[preferredSizeForWidthText]-gap-[preferredSizeForWidth(60)]-(>=inset)-|",
				"H:|-inset-[verticalShift]-(>=gap)-[verticalShiftValue(60)]-(>=inset)-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[help]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[insertMarkers]-checkRow-[resetWidths]-row-[preferredSizeForWidth]-row-[verticalShiftValue]-row-[allGlyphs]-checkRow-[allMasters]-inset-[runButton]-inset-|",
				"V:[help]-inset-|",
				{"view1": self.w.preferredSizeForWidthText, "attribute1": "centerY", "view2": self.w.preferredSizeForWidth, "attribute2": "centerY"},
				{"view1": self.w.verticalShift, "attribute1": "centerY", "view2": self.w.verticalShiftValue, "attribute2": "centerY"},
				{"view1": self.w.verticalShiftValue, "attribute1": "leading", "view2": self.w.preferredSizeForWidth, "attribute2": "leading"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def openURL(self, sender=None):
		URL = "https://glyphsapp.com/tutorials/creating-an-apple-color-font"
		import webbrowser
		webbrowser.open(URL)

	def updateUI(self, sender=None):
		self.w.preferredSizeForWidth.enable(self.w.resetWidths.get() or self.w.insertMarkers.get())
		self.w.verticalShiftValue.enable(self.w.verticalShift.get())
		self.w.runButton.enable(self.w.insertMarkers.get() or self.w.verticalShift.get() or self.w.resetWidths.get())

	def addMarkers(self, layer=None, bounds=None):
		if layer and bounds:
			markerPositions = (
				bounds.origin,
				NSPoint(bounds.origin.x + bounds.size.width, bounds.origin.y + bounds.size.height),
			)
			factors = (1, -1)
			for position, factor in zip(markerPositions, factors):
				# draw rectangle:
				pen = layer.getPen()
				pen.moveTo(position)
				pen.lineTo((position.x + factor, position.y))
				pen.lineTo((position.x, position.y + factor))
				pen.closePath()
				pen.endPath()

	def sbixSpacerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print(f"sbix Spacer Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				# query user settings:
				insertMarkers = self.pref("insertMarkers")
				verticalShift = self.pref("verticalShift")
				verticalShiftValue = self.prefInt("verticalShiftValue")
				resetWidths = self.pref("resetWidths")
				preferredSizeForWidth = self.prefInt("preferredSizeForWidth")
				allGlyphs = self.pref("allGlyphs")
				allMasters = self.pref("allMasters")

				if allGlyphs:
					glyphs = thisFont.glyphs
				else:
					glyphs = [layer.parent for layer in thisFont.selectedLayers]

				if allMasters:
					masters = thisFont.masters
				else:
					masters = (thisFont.selectedFontMaster, )

				for glyph in glyphs:
					for master in masters:
						masterLayer = glyph.layers[master.id]
						layers = [layer for layer in glyph.layers if layer.master == master and layer != masterLayer]
						isSbixGlyph = False
						for layer in layers:
							if layer.isSpecialLayer and layer.name.startswith("iColor "):
								isSbixGlyph = True
								break

						if isSbixGlyph:
							print(f"🔠 {glyph.name}")
							if resetWidths or insertMarkers:
								preferredLayerName = f"iColor {preferredSizeForWidth}"
								preferredLayer = None
								for layer in layers:
									if layer.name == preferredLayerName or (layer.name.startswith("iColor ") and preferredLayer is None):
										preferredLayer = layer
								if preferredLayer:
									if preferredLayer.backgroundImage:
										origin = preferredLayer.backgroundImage.position
										size = preferredLayer.backgroundImage.image.size()
										if size and size.width > 1 and size.height > 1:
											preferredLayerSize = int(preferredLayer.name.split(" ")[1])
											scaledSize = NSSize(thisFont.upm * size.width / preferredLayerSize, thisFont.upm * size.height / preferredLayerSize)
											if insertMarkers:
												print("  Inserting markers")
												masterLayer.clear()
												bounds = NSRect(origin, scaledSize)
												self.addMarkers(masterLayer, bounds)
											if resetWidths:
												print(f"  Resetting width to {size.width}")
												masterLayer.width = scaledSize.width

							if verticalShift:
								print(f"  Shifting master layer {verticalShiftValue} units")
								shiftTransform = NSAffineTransform.transform()
								shiftTransform.translateXBy_yBy_(0, verticalShiftValue)
								shiftMatrix = shiftTransform.transformStruct()  # returns the 6-float tuple
								masterLayer.applyTransform(shiftMatrix)

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"sbix Spacer Error: {e}")
			import traceback
			print(traceback.format_exc())


sbixSpacer()
