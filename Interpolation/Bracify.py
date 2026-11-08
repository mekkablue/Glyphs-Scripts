# MenuTitle: Bracify
__doc__ = """
Turn font masters into brace layers of certain glyphs. A.k.a. Sparsify.
"""

from copy import copy as copy
import objc
import vanilla
from AppKit import NSFont, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from Foundation import NSNumberFormatter
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, reportFontName, UpdateButton


def braceLayerAndAxisDictForGlyphAndMaster(glyph, master):
	# layer:
	mID = master.id
	braceLayer = copy(glyph.layers[mID])
	# coords:
	font = glyph.parent
	coordinates = master.axes
	axisIDs = [a.id for a in font.axes]
	axisDict = dict(zip(axisIDs, coordinates))
	return braceLayer, axisDict


def addBraceLayerToGlyph(braceLayer, axisDict, glyph, associatedMaster):
	braceLayer.parent = glyph
	braceLayer.associatedMasterId = associatedMaster.id
	braceLayer.attributes["coordinates"] = axisDict
	glyph.layers.append(braceLayer)


def layerIsSuperfluous(layer, threshold=2):
	originalLayer = copy(layer)
	originalLayer.parent = layer.parent
	layer.reinterpolate()

	# compare widths:
	if abs(layer.width - originalLayer.width) > threshold:
		layer = originalLayer
		return False

	# compare anchors:
	for anchor in layer.anchors:
		xDiff = abs(anchor.position.x - originalLayer.anchors[anchor.name].position.x)
		yDiff = abs(anchor.position.y - originalLayer.anchors[anchor.name].position.y)
		if xDiff > threshold or yDiff > threshold:
			layer = originalLayer
			return False

	# compare point coordinates:
	for pi, path in enumerate(layer.paths):
		originalPath = originalLayer.paths[pi]
		for ni, node in enumerate(path.nodes):
			originalNode = originalPath.nodes[ni]
			xDiff = abs(originalNode.x - node.x)
			yDiff = abs(originalNode.y - node.y)
			if xDiff > threshold and yDiff > threshold:
				layer = originalLayer
				return False

	layer = originalLayer
	return True


def nonSuperfluousLayersInMaster(font, master, threshold):
	glyphNameList = []
	for glyph in font.glyphs:
		layer = glyph.layers[master.id]
		if layer.paths and not layerIsSuperfluous(layer, threshold):
			glyphNameList.append(glyph.name)
	return glyphNameList


def masterList(font):
	listOfMasters = []
	if font:
		for i, m in enumerate(font.masters):
			entry = f"{i}: {m.name} (ID: {m.id})"
			listOfMasters.append(entry)
	return listOfMasters


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


class Bracify(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"masterToRemove": 1,
		"associateMaster": 0,
		"threshold": 3,
		"braceGlyphs": "",
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 460
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Bracify",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.masterToRemoveText = vanilla.TextBox("auto", "Remove font master:", sizeStyle="small", selectable=True)
		self.w.masterToRemove = vanilla.PopUpButton("auto", masterList(Glyphs.font), sizeStyle="small", callback=self.SavePreferences)

		self.w.associateMasterText = vanilla.TextBox("auto", "Associate with master:", sizeStyle="small", selectable=True)
		self.w.associateMaster = vanilla.PopUpButton("auto", masterList(Glyphs.font), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.UpdateForCurrentFont)

		tooltipText = "Used by the Guess button: a glyph is added to the list if removing the master would move its points, anchors or width by more than this many units."
		self.w.thresholdText = vanilla.TextBox("auto", "Coordinate threshold for guessing:", sizeStyle="small", selectable=True)
		self.w.thresholdText.setToolTip(tooltipText)
		thresholdFormatter = NSNumberFormatter.alloc().init()
		thresholdFormatter.setAllowsFloats_(False)
		thresholdFormatter.setMinimum_(0)
		self.w.threshold = SteppingEditText("auto", "3", callback=self.SavePreferences, sizeStyle="small", formatter=thresholdFormatter)
		self.w.threshold.setToolTip(tooltipText)

		self.w.braceGlyphsText = vanilla.TextBox("auto", "Add master layer as brace layer to these glyphs:", sizeStyle="small", selectable=True)

		self.w.braceGlyphs = vanilla.TextEditor("auto", text="", callback=self.SavePreferences, checksSpelling=False)
		self.w.braceGlyphs.setToolTip("Comma-separated list of glyph names. Use the Guess button to add the glyphs that would change too much (more than the threshold) if they didn’t keep a brace layer after master removal.")
		self.w.braceGlyphs.getNSScrollView().setHasVerticalScroller_(1)
		self.w.braceGlyphs.getNSScrollView().setHasHorizontalScroller_(0)
		self.w.braceGlyphs.getNSScrollView().setRulersVisible_(0)
		textView = self.w.braceGlyphs.getNSTextView()
		legibleFont = NSFont.controlContentFontOfSize_(NSFont.systemFontSize())
		textView.setFont_(legibleFont)
		textView.setHorizontallyResizable_(0)
		textView.setVerticallyResizable_(1)
		textView.setAutomaticDataDetectionEnabled_(0)
		textView.setAutomaticLinkDetectionEnabled_(0)
		textView.setDisplaysLinkToolTips_(0)
		textSize = textView.minSize()
		textView.setMinSize_(textSize)

		self.w.guessButton = vanilla.Button("auto", "Guess", callback=self.BracifyGuess)
		self.w.openTabButton = vanilla.Button("auto", "Open Tab", callback=self.OpenTab)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove Master", callback=self.BracifyMain)
		self.w.setDefaultButton(self.w.runButton)

		# labels: right-aligned, all with the width of the widest one
		labelNames = ("masterToRemoveText", "associateMasterText", "thresholdText")
		widestLabel = "thresholdText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		def sameAttribute(attribute, viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, referenceName), "attribute2": attribute}

		rules = [
			"H:|-inset-[masterToRemoveText]-gap-[masterToRemove]-inset-|",
			"H:|-inset-[associateMasterText]-gap-[associateMaster]-gap-[updateButton(24)]-inset-|",
			"H:|-inset-[thresholdText]-gap-[threshold(50)]-(>=inset)-|",
			"H:|-inset-[braceGlyphsText]-inset-|",
			"H:|-inset-[braceGlyphs]-inset-|",
			"H:|-inset-[guessButton(>=70)]-gap-[openTabButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
			"V:|-inset-[masterToRemove]-row-[associateMaster]-row-[threshold]-section-[braceGlyphsText]-gap-[braceGlyphs(140)]-inset-[runButton]-inset-|",
			"V:[guessButton]-inset-|",
			"V:[openTabButton]-inset-|",
			sameAttribute("centerY", "masterToRemoveText", "masterToRemove"),
			sameAttribute("centerY", "associateMasterText", "associateMaster"),
			sameAttribute("centerY", "updateButton", "associateMaster"),
			sameAttribute("centerY", "thresholdText", "threshold"),
		] + [
			sameAttribute("width", labelName, widestLabel) for labelName in labelNames if labelName != widestLabel
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 6, "section": 12})

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.pref("masterToRemove") != self.pref("associateMaster") and self.pref("braceGlyphs"))

	def UpdateForCurrentFont(self, sender=None):
		font = Glyphs.font
		self.w.associateMaster.setItems(masterList(font))
		self.w.masterToRemove.setItems(masterList(font))
		self.LoadPreferences()

	def OpenTab(self, sender=None):
		font = Glyphs.font
		self.SavePreferences()
		glyphNames = self.pref("braceGlyphs").strip()
		glyphNameList = glyphNames.split(",")
		tabString = ""
		warningGlyphs = []
		for glyphName in glyphNameList:
			glyphName = glyphName.strip()
			if font.glyphs[glyphName]:
				tabString += f"/{glyphName}"
			else:
				warningGlyphs.append(glyphName)
		if warningGlyphs:
			Message(
				title=f"Glyphs Missing in {font.familyName}",
				message=f"{len(warningGlyphs)} glyph{' is' if len(warningGlyphs) == 1 else 's are'} not in the frontmost font: {', '.join(warningGlyphs)}.",
				OKButton=None,
			)
		font.newTab(tabString)

	def BracifyGuess(self, sender=None):
		font = Glyphs.font
		masterIndex = self.prefInt("masterToRemove")
		master = font.masters[masterIndex]
		threshold = self.prefInt("threshold")
		glyphNameList = nonSuperfluousLayersInMaster(font, master, threshold=threshold)
		glyphNameText = ", ".join(glyphNameList)
		self.w.braceGlyphs.set(glyphNameText)
		self.SavePreferences()

	def BracifyMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(
					title="No Font Open",
					message="The script requires a font with at least three masters. Open a font and run the script again.",
					OKButton=None,
				)
				return

			if len(font.masters) < 3:
				Message(
					title="Not Enough Masters",
					message="This script does not make sense for fonts with less than three masters.",
					OKButton=None,
				)
				return

			reportName = reportFontName(font)
			print(f"Bracify Report for {reportName}")
			print()

			associateMaster = self.prefInt("associateMaster")
			masterToRemove = self.prefInt("masterToRemove")
			master = font.masters[masterToRemove]
			masterName = master.name

			glyphNames = self.pref("braceGlyphs").strip()
			glyphNameList = glyphNames.split(",")
			print(f"💚 Building brace layers for {len(glyphNameList)} glyph{'' if len(glyphNameList) == 1 else 's'}: {glyphNames}.\n")

			for glyphName in glyphNameList:
				glyphName = glyphName.strip()
				glyph = font.glyphs[glyphName]
				if not glyph:
					print(f"⚠️ No glyph with name ‘{glyphName}’, skipping.")
					continue
				braceLayer, axisDict = braceLayerAndAxisDictForGlyphAndMaster(glyph, master)
				addBraceLayerToGlyph(braceLayer, axisDict, glyph, font.masters[associateMaster])
				print(f"✅ Added brace layer: {glyphName}.")

			font.removeFontMaster_(master)
			print(f"\n🚀 Removed master: {masterName}.")

			tab = font.currentTab
			if not tab:
				tab = font.newTab()
			tab.text = "/" + "/".join(glyphNameList)
			print("✅ Done.")

			self.w.close()  # delete if you want window to stay open

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Bracify Error: {e}")
			import traceback
			print(traceback.format_exc())


Bracify()
