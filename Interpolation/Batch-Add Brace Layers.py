# MenuTitle: Batch-Add Brace Layers
__doc__ = """
Batch-insert intermediate layers (‘brace layers’) in selected glyphs. (Glyphs 2: Batch-insert brace or bracket layers in selected glyphs.)
"""

from copy import copy
from vanilla import FloatingWindow, EditText, TextBox, CheckBox, Button  # type: ignore
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, GSLayer, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityWindowSizeStayPut,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize


class InsertSpecialLayersV3(mekkaObject):
	prefDict = {
		"intermediateCoordinates": "wght=400, wdth=100",
		"keepExistingBrace": 1,
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Add Brace Layers",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = TextBox("auto", "Add intermediate (‘brace’) layers to selected glyphs:", sizeStyle="small", selectable=True)

		self.w.intermediateCoordinates = EditText("auto", self.pref("intermediateCoordinates"), callback=self.SavePreferences, sizeStyle="small")
		self.w.intermediateCoordinates.getNSTextField().setPlaceholderString_("wght=400, wdth=100")
		self.w.intermediateCoordinates.setToolTip("Axis coordinates of the new intermediate layer: comma-separated list of axis tags and values, one entry for each axis of the font, e.g., wght=400, wdth=100.")
		self.w.updateCoordinates = UpdateButton("auto", callback=self.resetCoordinates)
		self.w.updateCoordinates.setToolTip("Will reset the entry to half way between the first two masters, or same as the only master (if there is only one).")

		self.w.keepExistingBrace = CheckBox("auto", "Keep (don’t overwrite) existing brace layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingBrace.setToolTip("If checkbox is on and a glyph already contains (on any master) a brace layer at the indicated value, the script will skip the glyph. If the checkbox is off, it will deactivate the existing brace layer, and insert a new one.")

		# Run Button:
		self.w.runButton = Button("auto", "Insert", callback=self.InsertSpecialLayersV3Main)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-(>=inset)-|",
				"H:|-inset-[intermediateCoordinates]-gap-[updateCoordinates]-inset-|",
				"H:|-inset-[keepExistingBrace]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[intermediateCoordinates]-row-[keepExistingBrace]-inset-[runButton]-inset-|",
				{"view1": self.w.updateCoordinates, "attribute1": "centerY", "view2": self.w.intermediateCoordinates, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

	def resetCoordinates(self, sender=None):
		if not Glyphs.font:
			return
		text = self.braceDefaultForFont(Glyphs.font)
		self.setPref("intermediateCoordinates", text)
		self.LoadPreferences()


	def braceDefaultForFont(self, font):
		tags = [axis.axisTag for axis in font.axes]
		coords = list(font.masters[0].axes)
		if len(font.masters) > 1:
			otherMaster = font.masters[1]
			for i, coord in enumerate(coords):
				coords[i] = round((coord + otherMaster.axes[i]) / 2)
		braceText = ", ".join([f"{tag}={val}" for tag, val in zip(tags, coords)])
		return braceText


	def InsertSpecialLayersV3Main(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		thisFont = Glyphs.font  # frontmost font
		if thisFont is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		print("Insert Special Layers Report for %s" % thisFont.familyName)
		if thisFont.filepath:
			print(f"📄 {thisFont.filepath}")
		else:
			print(f"📄 {thisFont.familyName} (unsaved)")
		print()

		coordinates = {}
		for coordDef in [c.strip() for c in self.pref("intermediateCoordinates").split(",") if "=" in c]:
			axisTag, braceValue = coordDef.split("=")
			axisTag = axisTag.strip()
			braceValue = float(braceValue.strip())
			axis = thisFont.axisForTag_(axisTag)
			if not axis:
				Message(
					title=f"Axis Not Found: {axisTag}",
					message=f"No axis with tag ‘{axisTag}’ found in frontmost font ‘{thisFont.familyName}’.",
					OKButton=None,
				)
				return
			axisID = axis.axisId
			coordinates[axisID] = braceValue

		numUser = len(coordinates)
		numFont = len(thisFont.axes)
		if numUser != numFont:
			Message(
				title="Axes Mismatch Error",
				message=f"You defined {numUser} ax{'i' if numUser==1 else 'e'}s, but the frontmost font ‘{thisFont.familyName}’ has {numFont} ax{'i' if numFont==1 else 'e'}s.",
				OKButton=None,
			)
			return

		selectedGlyphs = set([l.parent for l in thisFont.selectedLayers])
		for selectedGlyph in selectedGlyphs:
			self.addBraceToGlyph(selectedGlyph, coordinates)


	def addBraceToGlyph(self, glyph, coordinates):
		if self.prefBool("keepExistingBrace"):
			for existingLayer in glyph.layers:
				if existingLayer.attributes["coordinates"] == coordinates:
					return
		braceLayer = copy(glyph.layers[0])
		braceLayer.attributes["coordinates"] = coordinates
		glyph.layers.append(braceLayer)
		braceLayer.reinterpolate()


class InsertSpecialLayers(mekkaObject):
	prefDict = {
		"layerName": "Intermediate {100}",
		"prefillWithMasterContent": 0,
		"keepExistingBrace": 1,
		"reinterpolateBrace": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Insert Special Layers",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = TextBox("auto", "Insert layer into selected glyphs:", sizeStyle='small', selectable=True)

		self.w.layerNameText = TextBox("auto", "Layer name:", sizeStyle='small', selectable=True)
		self.w.layerName = EditText("auto", "Intermediate {100}", callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Name of the new layer. Use curly braces for a brace layer, e.g., Intermediate {100}."
		self.w.layerNameText.setToolTip(tooltipText)
		self.w.layerName.setToolTip(tooltipText)

		self.w.prefillWithMasterContent = CheckBox("auto", "Create as duplicate of master layer", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.prefillWithMasterContent.setToolTip("Will add the new layer with the content of the associated master layer. If checkbox is off, will insert empty layer. In case of brace layers, the Reinterpolate option (further down) takes precedence, though.")

		self.w.keepExistingBrace = CheckBox("auto", "Keep existing brace layer", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingBrace.setToolTip("Only applies to brace layers. If checkbox is on and a glyph already contains (on any master) a brace layer at the indicated value, the script will skip the glyph. If the checkbox is off, it will deactivate the existing brace layer by replacing the curly braces with hashtags.")

		self.w.reinterpolateBrace = CheckBox("auto", "Reinterpolate brace layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reinterpolateBrace.setToolTip("Only applies to brace layers. If checkbox is on and a brace layer is inserted, it will reinterpolate the newly generated brace layer. It only does this for newly generated layer, and will not reinterpolate existing brace layers.")

		# Run Button:
		self.w.runButton = Button("auto", "Insert", callback=self.InsertSpecialLayersMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the field takes the leftover width:
		self.w.layerNameText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-(>=inset)-|",
				"H:|-inset-[layerNameText]-gap-[layerName]-inset-|",
				"H:|-inset-[prefillWithMasterContent]-(>=inset)-|",
				"H:|-inset-[keepExistingBrace]-(>=inset)-|",
				"H:|-inset-[reinterpolateBrace]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[layerName]-row-[prefillWithMasterContent]-checkRow-[keepExistingBrace]-checkRow-[reinterpolateBrace]-inset-[runButton]-inset-|",
				{"view1": self.w.layerNameText, "attribute1": "centerY", "view2": self.w.layerName, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def braceValueFromName(self, braceName):
		return braceName[braceName.find("{"):braceName.find("}") + 1]

	def InsertSpecialLayersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Insert Special Layers Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print("📄 %s" % thisFont.filepath)
				else:
					print("📄 %s (unsaved)" % thisFont.familyName)
				print()

				layerName = self.pref("layerName")
				prefillWithMasterContent = self.pref("prefillWithMasterContent")
				keepExistingBrace = self.pref("keepExistingBrace")
				reinterpolateBrace = self.pref("reinterpolateBrace")

				isBrace = "{" in layerName and "}" in layerName and layerName.find("{") < layerName.find("}") - 1

				currentMaster = thisFont.selectedFontMaster
				insertedLayerCount = 0

				for thisGlyph in [layer.parent for layer in thisFont.selectedLayers]:
					print("🔠 Processing %s" % thisGlyph.name)
					if isBrace and not keepExistingBrace:
						braceParticle = self.braceValueFromName(layerName)
						for potentialBraceLayer in thisGlyph.layers:
							if potentialBraceLayer.isSpecialLayer and braceParticle in potentialBraceLayer.name:
								# deactivate it: {100} -> #100#
								print("  Deactivating layer: %s" % potentialBraceLayer.name)
								potentialBraceLayer.name = potentialBraceLayer.name.replace("{", "#").replace("}", "#")

					if prefillWithMasterContent:
						newLayer = thisGlyph.layers[currentMaster.id].copy()
					else:
						newLayer = GSLayer()
						newLayer.associatedMasterId = currentMaster.id

					if newLayer:
						newLayer.name = layerName
						print("  Adding layer: %s" % newLayer.name)
						thisGlyph.layers.append(newLayer)
						insertedLayerCount += 1

						if isBrace and reinterpolateBrace:
							newLayer.reinterpolate()

				# Final report:
				Glyphs.showNotification(
					"%s: Done" % (thisFont.familyName),
					"Inserted %i layer%s. Details in Macro Window." % (
						insertedLayerCount,
						"" if insertedLayerCount == 1 else "s",
					),
				)
				print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Insert Special Layers Error: %s" % e)
			import traceback
			print(traceback.format_exc())


if Glyphs.versionNumber < 3:
	InsertSpecialLayers()
else:
	InsertSpecialLayersV3()
