# MenuTitle: Anchor Mover
__doc__ = """
Batch-process anchor positions in selected glyphs (GUI).
"""

import vanilla
import math
import objc
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSWindowStyleMaskResizable
from Foundation import NSPoint, NSSize
from GlyphsApp import Glyphs, GSOFFCURVE, Message, GSMetricsTypexHeight, GSMetricsTypeItalicAngle, GSMetricsTypeAscender, GSMetricsTypeCapHeight, GSMetricsTypeDescender, GSMetricsTypeMidHeight, GSMetricsTypeBodyHeight, GSMetricsTypeSlantHeight, GSMetricsTypeBaseline
from mekkablue import mekkaObject, UpdateButton
from mekkablue.geometry import transform, italicize


def highestNodeInLayer(layer):
	highest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if highest is None or highest.y < n.y:
					highest = n
	return highest


def lowestNodeInLayer(layer):
	lowest = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if lowest is None or lowest.y > n.y:
					lowest = n
	return lowest


def rightmostNodeInLayer(layer):
	rightmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if rightmost is None or rightmost.x < n.x:
					rightmost = n
	return rightmost


def leftmostNodeInLayer(layer):
	leftmost = None
	for p in layer.paths:
		for n in p.nodes:
			if n.type != GSOFFCURVE:
				if leftmost is None or leftmost.x > n.x:
					leftmost = n
	return leftmost


listHorizontal = (
	("current position", "copyAnchor.x"),
	("LSB", "0.0"),
	("RSB", "copyLayer.width"),
	("center", "copyLayer.width // 2.0"),
	("bbox left edge", "copyLayer.fastBounds().origin.x"),
	("bbox center", "copyLayer.fastBounds().origin.x + copyLayer.fastBounds().size.width // 2.0"),
	("bbox right edge", "copyLayer.fastBounds().origin.x + copyLayer.fastBounds().size.width"),
	("highest node", "highestNodeInLayer(copyLayer).x"),
	("lowest node", "lowestNodeInLayer(copyLayer).x"),
)

listVertical = (
	("current position", "copyAnchor.y"),
	("ascender", "selectedAscender"),
	("cap height", "selectedCapheight"),
	("mid height", "selectedMidHeight"),
	("body height", "selectedBodyHeight"),
	("x-height/smallcap height", "selectedXheight"),
	("slant height", "selectedSlantHeight"),
	("half ascender", "selectedAscender // 2.0"),
	("half cap height", "selectedCapheight // 2.0"),
	("half mid height", "selectedMidHeight // 2.0"),
	("half body height", "selectedBodyHeight // 2.0"),
	("half x-height/smallcap height", "halfXHeight"),
	("baseline", "selectedBaseline"),
	("descender", "selectedDescender"),
	("bbox top", "copyLayer.fastBounds().origin.y + copyLayer.fastBounds().size.height"),
	("bbox center", "copyLayer.fastBounds().origin.y + (copyLayer.fastBounds().size.height // 2.0)"),
	("bbox bottom", "copyLayer.fastBounds().origin.y"),
	("leftmost node", "leftmostNodeInLayer(copyLayer).y"),
	("rightmost node", "rightmostNodeInLayer(copyLayer).y"),
)


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def italicSkew(x, y, angle=10.0):
	"""Skews x/y along the x-axis and returns skewed x value."""
	newAngle = (angle / 180.0) * math.pi
	return x + y * math.tan(newAngle)


class AnchorMover2(mekkaObject):
	prefDict = {
		"anchorName": "",
		"hTarget": 0.0,
		"hChange": 0.0,
		"vTarget": 0.0,
		"vChange": 0.0,
		"italic": True,
		"allMasters": False,
		"verbose": False,
	}

	def __init__(self):
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Anchor Mover",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		inset = 15
		anchorTooltip = "Name of the anchor to move, e.g. top or bottom. The menu lists the anchors of the selected glyphs; click the refresh button to update it."
		horizontalTooltip = "Horizontal target position of the anchor, before the offset in the field to the right is added."
		verticalTooltip = "Vertical target position of the anchor, before the offset in the field to the right is added."
		offsetTooltip = "Offset added to the target position (units). Can be negative."

		self.w.text_1 = vanilla.TextBox("auto", "Move anchor", sizeStyle="small")
		self.w.text_1.setToolTip(anchorTooltip)
		self.w.anchorName = vanilla.ComboBox("auto", self.GetAnchorNames(), sizeStyle="small", callback=self.SavePreferences)
		self.w.anchorName.setToolTip(anchorTooltip)
		self.w.button = UpdateButton("auto", callback=self.SetAnchorNames)
		self.w.button.setToolTip("Refresh the anchor names from the selected glyphs.")
		self.w.text_2 = vanilla.TextBox("auto", "in selected glyphs", sizeStyle="small")

		self.w.hText_1 = vanilla.TextBox("auto", "↔")
		self.w.hText_2 = vanilla.TextBox("auto", "to", sizeStyle="small")
		self.w.hTarget = vanilla.PopUpButton("auto", [x[0] for x in listHorizontal], sizeStyle="small", callback=self.SavePreferences)
		self.w.hTarget.setToolTip(horizontalTooltip)
		self.w.hText_3 = vanilla.TextBox("auto", "+", sizeStyle="small")
		self.w.hChange = SteppingEditText("auto", "0.0", sizeStyle="small", callback=self.SavePreferences)
		self.w.hChange.setToolTip(offsetTooltip)

		self.w.vText_1 = vanilla.TextBox("auto", "↕")
		self.w.vText_2 = vanilla.TextBox("auto", "to", sizeStyle="small")
		self.w.vTarget = vanilla.PopUpButton("auto", [y[0] for y in listVertical], sizeStyle="small", callback=self.SavePreferences)
		self.w.vTarget.setToolTip(verticalTooltip)
		self.w.vText_3 = vanilla.TextBox("auto", "+", sizeStyle="small")
		self.w.vChange = SteppingEditText("auto", "0.0", sizeStyle="small", callback=self.SavePreferences)
		self.w.vChange.setToolTip(offsetTooltip)

		self.w.italic = vanilla.CheckBox("auto", "Respect italic angle", value=True, sizeStyle="small", callback=self.SavePreferences)
		self.w.italic.setToolTip("Measure positions along the italic angle of the layer, so the anchor keeps its slant.")
		self.w.allMasters = vanilla.CheckBox("auto", "All masters and special layers", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allMasters.setToolTip("Otherwise only the current masters (the selected layers) are processed.")
		self.w.verbose = vanilla.CheckBox("auto", "Log in Macro window", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Reports every step in the Macro window. Slow, use for tracking errors.")

		self.w.moveButton = vanilla.Button("auto", "Move", callback=self.MoveCallback)
		self.w.moveButton.setToolTip("Move the anchors in the selected glyphs.")
		self.w.setDefaultButton(self.w.moveButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels hug their text, flexible controls take the leftover width
		for labelName in ("text_1", "text_2", "hText_1", "hText_2", "hText_3", "vText_1", "vText_2", "vText_3"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# popups may shrink below the width of their longest item
		for popupName in ("hTarget", "vTarget"):
			getattr(self.w, popupName).getNSPopUpButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[anchorName(>=75)]-gap-[button]-gap-[text_2]-inset-|",
				"H:|-inset-[hText_1]-gap-[hText_2]-gap-[hTarget(>=67)]-gap-[hText_3]-gap-[hChange(48)]-inset-|",
				"H:|-inset-[vText_1]-gap-[vText_2]-gap-[vTarget(>=67)]-gap-[vText_3]-gap-[vChange(48)]-inset-|",
				"H:|-inset-[italic]-(>=inset)-|",
				"H:|-inset-[allMasters]-(>=inset)-|",
				"H:|-inset-[verbose]-(>=inset)-|",
				"H:|-(>=inset)-[moveButton(>=70)]-inset-|",
				"V:|-gap-[anchorName]-row-[hTarget]-row-[vTarget]-row-[italic]-checkRow-[allMasters]-checkRow-[verbose]-inset-[moveButton]-inset-|",
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
				{"view1": self.w.button, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
				{"view1": self.w.text_2, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
				{"view1": self.w.hText_1, "attribute1": "centerY", "view2": self.w.hTarget, "attribute2": "centerY"},
				{"view1": self.w.hText_2, "attribute1": "centerY", "view2": self.w.hTarget, "attribute2": "centerY"},
				{"view1": self.w.hText_3, "attribute1": "centerY", "view2": self.w.hTarget, "attribute2": "centerY"},
				{"view1": self.w.hChange, "attribute1": "centerY", "view2": self.w.hTarget, "attribute2": "centerY"},
				{"view1": self.w.vText_1, "attribute1": "centerY", "view2": self.w.vTarget, "attribute2": "centerY"},
				{"view1": self.w.vText_2, "attribute1": "centerY", "view2": self.w.vTarget, "attribute2": "centerY"},
				{"view1": self.w.vText_3, "attribute1": "centerY", "view2": self.w.vTarget, "attribute2": "centerY"},
				{"view1": self.w.vChange, "attribute1": "centerY", "view2": self.w.vTarget, "attribute2": "centerY"},
				{"view1": self.w.vText_1, "attribute1": "width", "view2": self.w.hText_1, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		self.LoadPreferences()

		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: lock the content height Auto Layout arrived at
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentHeight = nsWindow.contentView().frame().size.height
		nsWindow.setContentMinSize_(NSSize(220, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(900, contentHeight))

	def MoveCallback(self, sender):
		# brings macro window to front and clears its log:
		Glyphs.clearLog()

		thisFont = Glyphs.font
		selectedLayers = thisFont.selectedLayers
		anchorName = self.pref("anchorName")
		horizontalIndex = self.prefInt("hTarget")
		horizontalChange = self.prefFloat("hChange")
		verticalIndex = self.prefInt("vTarget")
		verticalChange = self.prefFloat("vChange")
		allMasters = self.pref("allMasters")
		respectItalic = self.pref("italic")
		verbose = self.pref("verbose")

		evalCodeH = listHorizontal[horizontalIndex][1]
		evalCodeV = listVertical[verticalIndex][1]

		if not selectedLayers:
			if verbose:
				print("No glyphs selected.")
			Message(title="No Glyphs Selected", message="Could not move anchors. No glyphs were selected.", OKButton=None)
		else:
			if verbose:
				print("Processing %i glyph%s..." % (
					len(selectedLayers),
					"" if len(selectedLayers) == 1 else "s",
				))
			thisFont.disableUpdateInterface()
			try:
				for selectedLayer in selectedLayers:
					selectedGlyph = selectedLayer.glyph()
					if not selectedGlyph:
						continue
					if verbose:
						print(f"\n🔠 {selectedGlyph.name}")
					if allMasters:
						originalLayers = tuple([layer for layer in selectedGlyph.layers if layer.isMasterLayer or layer.isSpecialLayer])
					else:
						originalLayers = (selectedLayer, )

					for originalLayer in originalLayers:
						selectedAscender = originalLayer.metricForType_(GSMetricsTypeAscender)
						selectedCapheight = originalLayer.metricForType_(GSMetricsTypeCapHeight)
						selectedDescender = originalLayer.metricForType_(GSMetricsTypeDescender)
						selectedXheight = originalLayer.metricForType_(GSMetricsTypexHeight)
						if selectedXheight == 0.0:  # bug in Glyphs 3.3?
							selectedXheight = originalLayer.associatedFontMaster().xHeight
						halfXHeight = selectedXheight * 0.5
						selectedMidHeight = originalLayer.metricForType_(GSMetricsTypeMidHeight)
						selectedBodyHeight = originalLayer.metricForType_(GSMetricsTypeBodyHeight)
						selectedSlantHeight = originalLayer.metricForType_(GSMetricsTypeSlantHeight)
						selectedBaseline = originalLayer.metricForType_(GSMetricsTypeBaseline)
						italicAngle = originalLayer.metricForType_(GSMetricsTypeItalicAngle)

						if len(originalLayer.anchors) == 0:
							if verbose:
								print(f"⚠️ no anchors on layer ‘{originalLayer.name}’.")
							continue

						thisGlyph = originalLayer.parent

						# create a layer copy that can be slanted backwards if necessary
						copyLayer = originalLayer.copyDecomposedLayer()
						copyLayer.decomposeCorners()
						# thisGlyph.beginUndo()  # undo grouping causes crashes

						try:
							if italicAngle and respectItalic:
								# slant the layer copy backwards
								moveDown = transform(shiftY=-halfXHeight).transformStruct()
								skewBack = transform(skew=-italicAngle).transformStruct()
								moveUp = transform(shiftY=halfXHeight).transformStruct()
								copyLayer.applyTransform(moveDown)
								copyLayer.applyTransform(skewBack)
								copyLayer.applyTransform(moveUp)

							for copyAnchor in copyLayer.anchors:
								if copyAnchor.name != anchorName:
									continue

								oldAnchorX = copyAnchor.x
								oldAnchorY = copyAnchor.y
								xMove = eval(evalCodeH) + horizontalChange
								yMove = eval(evalCodeV) + verticalChange

								# Ignore moves relative to bbox if there are no paths:
								if not copyLayer.paths:
									if "bounds" in evalCodeH:
										xMove = oldAnchorX

									if "bounds" in evalCodeV:
										yMove = oldAnchorY

								# Only move if the calculated position differs from the original one:
								originalAnchor = originalLayer.anchors[anchorName]
								if int(oldAnchorX) != int(xMove) or int(oldAnchorY) != int(yMove):
									if italicAngle and respectItalic:
										# skew back
										originalAnchor.position = italicize(NSPoint(xMove, yMove), italicAngle, halfXHeight)
									else:
										originalAnchor.position = NSPoint(xMove, yMove)
									if verbose:
										print(f"⚓️ {anchorName} → {originalAnchor.x}, {originalAnchor.y} in layer: {originalLayer.name}.")
								elif verbose:
									print(f"⚓️ {anchorName} anchor unchanged in {originalLayer.name}.")

						except Exception as e:
							print(f"ERROR: Failed to move anchor in {thisGlyph.name}.")
							print(e)
							import traceback
							print(traceback.format_exc())

			except Exception as e:
				raise e
			finally:
				thisFont.enableUpdateInterface()
		print("Done.")

	def GetAnchorNames(self):
		myAnchorList = []
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		try:
			for thisLayer in selectedLayers:
				anchorNames = list(thisLayer.anchors.keys())  # hack to avoid traceback
				for thisAnchorName in anchorNames:
					if thisAnchorName not in myAnchorList:
						myAnchorList.append(thisAnchorName)
		except:
			print("Error: Cannot collect anchor names from the current selection.")

		return sorted(myAnchorList)

	def SetAnchorNames(self, sender):
		anchorList = self.GetAnchorNames()
		self.w.anchorName.setItems(anchorList)


AnchorMover2()
