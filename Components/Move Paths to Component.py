# MenuTitle: Move Paths to Component
__doc__ = """
Moves paths to a separate glyph and insert them as auto-aligned, anchored components in the source glyph. Perfect for making path+component mixtures into pure composites.
"""

import vanilla
from AppKit import NSNotificationCenter, NSPoint, NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from copy import copy as copy
from GlyphsApp import Glyphs, GSGlyph, GSComponent, GSPath, GSAnchor, GSUppercase, Message
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable


class MovePathstoComponent(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"name": "_bar.dollar",
		"anchor": "bottom",
		"includeSpecialLayers": 0,
		"keepBaseComponentPosition": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 380
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Move Paths to Component",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Turn paths of selected glyph into component on all masters:", sizeStyle='small', selectable=True)

		self.w.nameText = vanilla.TextBox("auto", "Component name:", sizeStyle='small', selectable=True)
		self.w.name = vanilla.EditText("auto", "_bar.dollar", callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Name of the new glyph that receives the paths. The button suggests a name based on the selected glyph."
		self.w.nameText.setToolTip(tooltipText)
		self.w.name.setToolTip(tooltipText)
		self.w.nameUpdateButton = UpdateButton("auto", callback=self.updateName)
		self.w.nameUpdateButton.setToolTip("Suggests a name for the new component glyph, based on the selected glyph.")

		self.w.anchorText = vanilla.TextBox("auto", "Attach to anchor:", sizeStyle='small', selectable=True)
		self.w.anchor = vanilla.ComboBox("auto", self.allAnchorNames(), sizeStyle='small', callback=self.SavePreferences)
		tooltipText = "Anchor of the base glyph to which the new component is attached."
		self.w.anchorText.setToolTip(tooltipText)
		self.w.anchor.setToolTip(tooltipText)
		self.w.anchorUpdateButton = UpdateButton("auto", callback=self.updateAnchors)
		self.w.anchorUpdateButton.setToolTip("Updates the anchor names from the selected glyph, and picks the anchor that suits the component name.")

		self.w.includeSpecialLayers = vanilla.CheckBox("auto", "Include special layers (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeSpecialLayers.setToolTip("Also processes brace and bracket layers, and other special layers, not just the masters.")

		self.w.keepBaseComponentPosition = vanilla.CheckBox("auto", "Keep base component position (with incremental keys)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepBaseComponentPosition.setToolTip("Will add an incremental metrics key (e.g. ==+10) if width deviation is at least 5u.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Make Composite", callback=self.MovePathsToComponentMain)
		self.w.runButton.setToolTip("Moves the paths into the new glyph and inserts it as a component.")
		self.w.setDefaultButton(self.w.runButton)

		self.w.warningText = vanilla.TextBox("auto", "", sizeStyle="small", selectable=True)
		self.w.warningText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for labelName in ("nameText", "anchorText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[nameText]-gap-[name]-gap-[nameUpdateButton]-inset-|",
				"H:|-inset-[anchorText]-gap-[anchor]-gap-[anchorUpdateButton]-inset-|",
				"H:|-inset-[includeSpecialLayers]-(>=inset)-|",
				"H:|-inset-[keepBaseComponentPosition]-(>=inset)-|",
				"H:|-inset-[warningText]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[name]-row-[anchor]-sectionGap-[includeSpecialLayers]-checkRow-[keepBaseComponentPosition]-inset-[runButton]-inset-|",
				{"view1": self.w.nameText, "attribute1": "centerY", "view2": self.w.name, "attribute2": "centerY"},
				{"view1": self.w.nameUpdateButton, "attribute1": "centerY", "view2": self.w.name, "attribute2": "centerY"},
				{"view1": self.w.anchorText, "attribute1": "centerY", "view2": self.w.anchor, "attribute2": "centerY"},
				{"view1": self.w.anchorUpdateButton, "attribute1": "centerY", "view2": self.w.anchor, "attribute2": "centerY"},
				{"view1": self.w.warningText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.anchorText, "attribute1": "width", "view2": self.w.nameText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 10, "sectionGap": 12, "checkRow": 5},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		# check for existing glyph:
		glyphName = self.w.name.get()
		if Glyphs.font is None:
			self.w.runButton.enable(False)
			self.w.warningText.set("")
			return True
		glyphExistsInFont = Glyphs.font.glyphs[glyphName]
		self.w.runButton.enable(not glyphExistsInFont)
		if glyphExistsInFont:
			self.w.warningText.set(f"⚠️ {glyphName} already exists")
		else:
			self.w.warningText.set("")
		return True

	def updateAnchors(self, sender=None):
		anchorNames = self.allAnchorNames()
		self.w.anchor.setItems(anchorNames)

		glyphInfo = Glyphs.glyphInfoForName(self.w.name.get())
		if glyphInfo:
			possibleAnchors = glyphInfo.anchors
			if possibleAnchors:
				for anchorName in anchorNames:
					for possibleAnchorName in possibleAnchors:
						if anchorName in possibleAnchorName or possibleAnchorName in anchorName:
							self.w.anchor.set(anchorName)
							return

		for anchorName in anchorNames:
			if anchorName[0] == "#":
				self.w.anchor.set(anchorName)
				return

	def updateName(self, sender=None):
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				thisLayer = thisFont.selectedLayers[0]
				existingComponents = thisLayer.componentNames()
				thisGlyph = thisLayer.parent
				if thisGlyph:
					foundName = False
					if thisGlyph.glyphInfo and thisGlyph.glyphInfo.components:
						for compInfo in thisGlyph.glyphInfo.components[::-1]:
							compName = f"{compInfo.name}{'.case' if thisGlyph.case == GSUppercase and Glyphs.glyphInfoForName(compInfo.name).category == 'Mark' else ''}".replace(
								".case.case", ".case"
							)
							if compName not in existingComponents:
								self.w.name.set(compName)
								foundName = True
								break
					elif thisGlyph.name == "Q":
						self.w.name.set("_tail.Q")
						foundName = True
					if not foundName:
						self.w.name.set(f"_part.{thisGlyph.name}")
					self.SavePreferences()

	def allAnchorNames(self, sender=None):
		anchorNames = []
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				thisLayer = thisFont.selectedLayers[0]
				for thisAnchor in thisLayer.anchorsTraversingComponents():
					if thisAnchor.name not in anchorNames:
						anchorNames.append(thisAnchor.name)
		return anchorNames

	def MovePathsToComponentMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			glyphName = None
			componentNames = []
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			else:
				print(f"‘Move Paths to Component’ Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				# determine current glyph:
				if not thisFont.selectedLayers:
					Message(title="Error: No Glyph", message="The script requires a selected glyph. Best to open a glyph in Edit view.", OKButton="Oops")
					print("🚫 No glyph selected. Aborting.\nDone.")
					return

				thisGlyph = thisFont.selectedLayers[0].parent
				glyphName = thisGlyph.name
				if not thisGlyph.layers[0].paths:
					Message(
						title="Error: No Paths in Glyph",
						message="The glyph ‘%s’ seems to have no paths. So the script has nothing to turn into a component." % glyphName,
						OKButton="Oops"
					)
					print("🚫 No paths in first layer of %s. Aborting.\nDone." % glyphName)
					return

				print("⚒️ Processing %s..." % thisGlyph.name)

				# query prefs:
				newCompName = self.pref("name")
				# category = self.pref("category")
				# subCategory = self.pref("subCategory")
				attachToAnchor = str(self.pref("anchor"))
				includeSpecialLayers = self.pref("includeSpecialLayers")

				# determine the kind of comp glyph, and the name of the new anchor
				category = "Letter"
				subCategory = None
				if attachToAnchor.endswith("entry"):
					insertAnchor = attachToAnchor.replace("entry", "exit")
				elif attachToAnchor.endswith("exit"):
					insertAnchor = attachToAnchor.replace("exit", "entry")
				elif attachToAnchor.startswith("_"):
					insertAnchor = attachToAnchor[1:]
				else:
					insertAnchor = "_" + attachToAnchor
					category = "Mark"
					subCategory = "Nonspacing"

				# create new comp glyph:
				print("🔠 Creating %s..." % newCompName)
				newGlyph = GSGlyph()
				newGlyph.name = newCompName
				newGlyph.export = False
				newGlyph.category = category
				if subCategory:
					newGlyph.subCategory = subCategory
				if thisFont.glyphs[newCompName]:
					# overwrite if it already exists
					del thisFont.glyphs[newCompName]
					print("⚠️ Overwrote existing %s" % newCompName)
				thisFont.glyphs.append(newGlyph)

				# step through current glyph and extract paths to new comp glyph:
				for layer in thisGlyph.layers:
					# extract paths:
					if layer.isMasterLayer or (layer.isSpecialLayer and includeSpecialLayers):
						originalWidth = layer.width
						newLayer = copy(layer)
						if layer.components:
							originalFirstComponentPosition = layer.components[0].position
						else:
							originalFirstComponentPosition = NSPoint(0, 0)

						# get rid of components, we just want paths:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3
							for i in range(len(newLayer.shapes) - 1, -1, -1):
								thisShape = newLayer.shapes[i]
								if isinstance(thisShape, GSComponent):
									del newLayer.shapes[i]
						else:
							# GLYPHS 2
							for i in range(len(newLayer.components) - 1, -1, -1):
								del newLayer.components[i]

						# insert connecting anchor:
						newAnchor = GSAnchor()
						newAnchor.name = insertAnchor
						newAnchor.position = NSPoint(0, 0)
						for referralAnchor in layer.anchorsTraversingComponents():
							if referralAnchor.name == attachToAnchor:
								newAnchor.position = referralAnchor.position
								break
						newLayer.anchors.append(newAnchor)

						# insert the new layer into the new comp glyph:
						if layer.isMasterLayer:
							newGlyph.layers[layer.associatedMasterId] = newLayer
						else:
							newGlyph.layers.append(newLayer)

						# in original glyph, insert component before or after:
						componentNames = None
						if "entry" in attachToAnchor or attachToAnchor.startswith("_"):
							componentNames = [newCompName]
							for c in layer.components:
								componentNames.append(c.componentName)
						else:
							componentNames = []
							for c in layer.components:
								componentNames.append(c.componentName)
							componentNames.append(newCompName)
						if componentNames:
							layer.setComponentNames_(componentNames)

						# remove paths from original glyph, we just want to keep components:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3
							for i in range(len(layer.shapes) - 1, -1, -1):
								thisShape = layer.shapes[i]
								if isinstance(thisShape, GSPath):
									del layer.shapes[i]
						else:
							# GLYPHS 2
							for i in range(len(layer.paths) - 1, -1, -1):
								del layer.paths[i]

						# autoalign all components and update metrics
						for i in range(len(layer.components)):
							c = layer.components[i]
							if self.pref("keepBaseComponentPosition") and i == 0:
								c.alignment = -1
								c.position = originalFirstComponentPosition
							else:
								c.alignment = 1
						if not self.pref("keepBaseComponentPosition"):
							layer.alignComponents()  # updates the width

						# insert correcting RSB adjustment (minimum 5):
						widthDifference = originalWidth - layer.width
						if abs(widthDifference) > 4 and self.pref("keepBaseComponentPosition"):
							metricsKey = "==%s%i" % (
								"-" if widthDifference < 0 else "+",
								abs(widthDifference),
							)
							if attachToAnchor.endswith("exit"):
								layer.leftMetricsKey = metricsKey
								leftOrRight = "left"
							elif attachToAnchor.endswith("entry"):
								layer.rightMetricsKey = metricsKey
								leftOrRight = "right"
							else:  # all other cases
								layer.leftMetricsKey = metricsKey
								leftOrRight = "left"
								layer.components[0].alignment = 1
								layer.alignComponents()

							layer.updateMetrics()
							layer.syncMetrics()

							print(
								"↔️ Added %s metrics key ‘%s’ on layer ‘%s’ (original width: %i)" % (
									leftOrRight,
									layer.rightMetricsKey if leftOrRight == "right" else layer.leftMetricsKey,
									layer.name,
									originalWidth,
								)
							)

			# trigger UI update:
			if Glyphs.versionNumber >= 3 and thisFont.currentTab:
				NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)
			if thisFont.currentTab:
				thisFont.currentTab.reflow()

			# Final report:
			if glyphName:
				print("✅ Turned %s into a pure composite of %s." % (
					glyphName,
					" and ".join(componentNames),
				))
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Move Paths to Component Error: %s" % e)
			import traceback
			print(traceback.format_exc())


MovePathstoComponent()
