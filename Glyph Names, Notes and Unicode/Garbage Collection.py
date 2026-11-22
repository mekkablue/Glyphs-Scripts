# MenuTitle: Garbage Collection
__doc__ = """
Removes annotations, glyph notes, guides, and node names.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, clearGuides, guidesOf, makeWindowResizable
from GlyphsApp import Glyphs
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)


def extractUserDataKeys(obj):
	userDataKeys = []
	if obj.userData:
		userDataKeys.extend(obj.userData.keys())
	return userDataKeys


def allUserDataKeysForFont(font):
	keys = []
	for master in font.masters:
		keys.extend(extractUserDataKeys(master))
	for glyph in font.glyphs:
		keys.extend(extractUserDataKeys(glyph))
		for layer in glyph.layers:
			keys.extend(extractUserDataKeys(layer))
	return sorted(set(keys))


class GarbageCollection(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"removeNodeNames": 1,
		"removeLocalGuides": 0,
		"removeGlobalGuides": 0,
		"removeAnnotations": 1,
		"removeGlyphNotes": 0,
		"removeColors": 0,
		"clearBackgroundLayers": 0,
		"removeBackupLayers": 0,
		"userDataFont": 0,
		"userDataMasters": 0,
		"userDataInstances": 0,
		"userDataGlyphs": 0,
		"userDataLayers": 0,
		"userDataKeys": "UFO, fontlab, public",
		"currentMasterOnly": 0,
		"selectedGlyphsOnly": 0,
		"allFonts": 0,
		"verbose": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Garbage Collection",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Clean frontmost font", sizeStyle='small', selectable=True)

		self.w.removeNodeNames = vanilla.CheckBox("auto", "Remove all node names 🔥❌👌🏻⛔️🧨 in font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeNodeNames.setToolTip("Deletes node markers, as employed by many mekkablue scripts to mark problematic spots.")

		self.w.removeAnnotations = vanilla.CheckBox("auto", "Remove all annotations 💬➕➖➚◯ in font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeAnnotations.setToolTip("Deletes annotations created with the Annotation Tool (A), e.g. circles, arrows, and texts.")

		self.w.removeLocalGuides = vanilla.CheckBox("auto", "Remove all local (blue) guides 🔵 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeLocalGuides.setToolTip("Deletes blue guides.")

		self.w.removeGlobalGuides = vanilla.CheckBox("auto", "Remove all global (red) guides 🔴 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeGlobalGuides.setToolTip("Deletes red guides.")

		self.w.removeGlyphNotes = vanilla.CheckBox("auto", "Remove all glyph notes in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeGlyphNotes.setToolTip("Deletes glyph notes as entered in list view or through the Glyph Note Palette (plug-in).")

		self.w.removeColors = vanilla.CheckBox("auto", "Remove all glyph and layer colors 🟠🟡🟢🟣 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeColors.setToolTip("Resets all glyph and layer colors to none.")

		self.w.clearBackgroundLayers = vanilla.CheckBox("auto", "Clear all background layers in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.clearBackgroundLayers.setToolTip("If checked, will clear all background layers (Cmd-B) of all layers.")

		self.w.removeBackupLayers = vanilla.CheckBox("auto", "Remove all backup layers in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeBackupLayers.setToolTip("If checked, will remove all unused layers, i.e., all non-master, non-color, non-intermediate and non-alternate layers.")

		self.w.line1 = vanilla.HorizontalLine("auto")

		self.w.currentMasterOnly = vanilla.CheckBox("auto", "Limit clean-up to current master only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.currentMasterOnly.setToolTip("If checked, applies the clean-up to layers of the current font master only. Exception: glyph notes are not master-specific.")

		self.w.selectedGlyphsOnly = vanilla.CheckBox("auto", "Limit clean-up to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedGlyphsOnly.setToolTip("If checked, applies the clean-up only to selected glyphs. Otherwise, to all glyphs in the font.")

		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ Apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.setToolTip("If checked, will work on ALL currently open fonts; otherwise only the frontmost font file open.")

		self.w.verbose = vanilla.CheckBox("auto", "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.setToolTip("Verbose reporting in Macro Window (slow).")

		self.w.line2 = vanilla.HorizontalLine("auto")

		self.w.userDataText = vanilla.TextBox("auto", "Remove userData in", sizeStyle='small', selectable=True)
		self.w.userDataFont = vanilla.CheckBox("auto", "font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataMasters = vanilla.CheckBox("auto", "masters", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataInstances = vanilla.CheckBox("auto", "instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Remove userData from the frontmost font, its masters, and/or instances.\n\n⚠️ Attention: the font/masters/instances options do NOT respect the ‘Limit’ settings above."
		self.w.userDataText.setToolTip(tooltip)
		self.w.userDataFont.setToolTip(tooltip)
		self.w.userDataMasters.setToolTip(tooltip)
		self.w.userDataInstances.setToolTip(tooltip)

		self.w.userDataGlyphs = vanilla.CheckBox("auto", "glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataLayers = vanilla.CheckBox("auto", "layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Remove userData from glyphs and/or layers. Will respect the ‘Limit’ settings above."
		self.w.userDataGlyphs.setToolTip(tooltip)
		self.w.userDataLayers.setToolTip(tooltip)

		self.w.userDataKeysText = vanilla.TextBox("auto", "…only keys with", sizeStyle='small', selectable=True)
		self.w.userDataKeys = vanilla.EditText("auto", "UFO, fontlab, public", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Comma-separated list of search strings for userData keys to delete. Leave empty to remove all."
		self.w.userDataKeysText.setToolTip(tooltip)
		self.w.userDataKeys.setToolTip(tooltip)
		self.w.userDataUpdate = UpdateButton("auto", callback=self.updateUserDataUI)
		self.w.userDataUpdate.setToolTip("Add the userData keys of frontmost font.")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=False)
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Clean", callback=self.GarbageCollectionMain)
		self.w.runButton.setToolTip("Removes the checked items from the frontmost font.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for label in (self.w.userDataText, self.w.userDataKeysText):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		checkBoxNames = (
			"removeNodeNames",
			"removeAnnotations",
			"removeLocalGuides",
			"removeGlobalGuides",
			"removeGlyphNotes",
			"removeColors",
			"clearBackgroundLayers",
			"removeBackupLayers",
			"currentMasterOnly",
			"selectedGlyphsOnly",
		)
		rules = ["H:|-inset-[descriptionText]-inset-|"]
		rules += [f"H:|-inset-[{name}]-(>=inset)-|" for name in checkBoxNames]
		rules += [
			"H:|-inset-[line1]-inset-|",
			"H:|-inset-[allFonts]-gap-[verbose]-(>=inset)-|",
			"H:|-inset-[line2]-inset-|",
			"H:|-inset-[userDataText]-gap-[userDataFont]-gap-[userDataMasters]-gap-[userDataInstances]-(>=inset)-|",
			"H:[userDataGlyphs]-gap-[userDataLayers]-(>=inset)-|",
			"H:|-inset-[userDataKeysText]-gap-[userDataKeys]-gap-[userDataUpdate]-inset-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[statusText]-(>=gap)-[runButton(>=70)]-inset-|",
			(
				"V:|-gap-[descriptionText]-row-[removeNodeNames]-checkRow-[removeAnnotations]-checkRow-[removeLocalGuides]-checkRow-[removeGlobalGuides]"
				"-checkRow-[removeGlyphNotes]-checkRow-[removeColors]-checkRow-[clearBackgroundLayers]-checkRow-[removeBackupLayers]"
				"-gap-[line1(1)]-gap-[currentMasterOnly]-checkRow-[selectedGlyphsOnly]-checkRow-[allFonts]"
				"-gap-[line2(1)]-gap-[userDataFont]-checkRow-[userDataGlyphs]-row-[userDataKeys]-barGap-[progress(16)]-barGap-[runButton]-inset-|"
			),
			{"view1": self.w.verbose, "attribute1": "centerY", "view2": self.w.allFonts, "attribute2": "centerY"},
			{"view1": self.w.userDataText, "attribute1": "centerY", "view2": self.w.userDataFont, "attribute2": "centerY"},
			{"view1": self.w.userDataMasters, "attribute1": "centerY", "view2": self.w.userDataFont, "attribute2": "centerY"},
			{"view1": self.w.userDataInstances, "attribute1": "centerY", "view2": self.w.userDataFont, "attribute2": "centerY"},
			{"view1": self.w.userDataGlyphs, "attribute1": "left", "view2": self.w.userDataFont, "attribute2": "left"},
			{"view1": self.w.userDataLayers, "attribute1": "centerY", "view2": self.w.userDataGlyphs, "attribute2": "centerY"},
			{"view1": self.w.userDataKeysText, "attribute1": "centerY", "view2": self.w.userDataKeys, "attribute2": "centerY"},
			{"view1": self.w.userDataUpdate, "attribute1": "centerY", "view2": self.w.userDataKeys, "attribute2": "centerY"},
			{"view1": self.w.userDataKeysText, "attribute1": "width", "view2": self.w.userDataText, "attribute2": "width"},
			{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
		]
		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "barGap": 12})

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def changeTitle(self, uiItem, toString):
		fromStrings = (
			"in current master",
			"in fontss",  # just in case
			"in fonts",
			"in font",
		)
		currentTitle = uiItem.getTitle()
		for fromString in fromStrings:
			if currentTitle.endswith(fromString):
				newTitle = currentTitle.replace(fromString, toString)
				uiItem.setTitle(newTitle)
				return

	def updateUserDataUI(self, sender=None):
		if not Glyphs.font:
			return
		userDataKeysForFrontmostFont = allUserDataKeysForFont(Glyphs.font)
		if userDataKeysForFrontmostFont:
			existingKeys = self.w.userDataKeys.get().strip()
			if existingKeys:
				for key in [k.strip() for k in existingKeys.split(",") if k.strip()]:
					if key not in userDataKeysForFrontmostFont:
						userDataKeysForFrontmostFont.append(key)
			userDataString = ", ".join(userDataKeysForFrontmostFont)
			self.w.userDataKeys.set(userDataString)
			self.SavePreferences()

	def updateUI(self, sender=None):
		uiItemNames = (
			"removeNodeNames",
			"removeAnnotations",
			"removeLocalGuides",
			"removeGlobalGuides",
			"removeGlyphNotes",
			"removeColors",
			"clearBackgroundLayers",
			"removeBackupLayers",
		)

		# change the checkbox titles:
		if self.pref("currentMasterOnly"):
			self.w.allFonts.enable(False)
			toString = "in current master"
		else:
			self.w.allFonts.enable(True)
			toString = "in font%s" % ("s" if self.pref("allFonts") else "")

		for uiItemName in uiItemNames:
			uiItem = self.w.__getattribute__(uiItemName)
			self.changeTitle(uiItem, toString)

		anyUserDataOn = self.pref("userDataGlyphs") or self.pref("userDataLayers") or self.pref("userDataInstances") or self.pref("userDataMasters") or self.pref("userDataFont")
		self.w.userDataKeys.enable(anyUserDataOn)

	def log(self, msg):
		try:
			if self.pref("verbose"):
				print(f"\t{msg}")
			self.w.statusText.set(msg.strip())
		except Exception as e:  # noqa: F841
			import traceback
			print(traceback.format_exc())

	def shouldBeRemoved(self, keyName, searchFor):
		if not searchFor:
			return True
		for searchText in searchFor:
			if searchText in keyName:
				return True
		return False

	def GarbageCollectionMain(self, sender):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		# find out about what the fonts are:
		currentMasterOnly = self.pref("currentMasterOnly")
		allFonts = self.pref("allFonts")
		if allFonts and not currentMasterOnly:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font, )

		if not theseFonts or not theseFonts[0]:
			self.log("❌ No font open.")
			return

		for fontIndex, thisFont in enumerate(theseFonts):
			try:
				thisFont.disableUpdateInterface()  # suppresses UI updates in Font View

				print(f"🗑 Garbage Collection Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(f"📄 {thisFont.filepath}")
				else:
					print("⚠️ file not saved yet")

				if self.pref("selectedGlyphsOnly"):
					glyphs = [layer.parent for layer in thisFont.selectedLayers]
				else:
					glyphs = thisFont.glyphs

				# query user settings:
				removeNodeNames = self.pref("removeNodeNames")
				removeLocalGuides = self.pref("removeLocalGuides")
				removeAnnotations = self.pref("removeAnnotations")
				removeGlyphNotes = self.pref("removeGlyphNotes")
				removeColors = self.pref("removeColors")
				clearBackgroundLayers = self.pref("clearBackgroundLayers")
				removeBackupLayers = self.pref("removeBackupLayers")

				userDataGlyphs = self.pref("userDataGlyphs")
				userDataLayers = self.pref("userDataLayers")
				userDataKeys = [k.strip() for k in self.pref("userDataKeys").split(",") if k.strip()]

				# set up counters:
				removeNodeNamesFont = 0
				localGuidesFont = 0
				removeAnnotationsFont = 0
				layerDeletionCountFont = 0
				cleanedBackgroundCount = 0

				# go through glyphs:
				print(f"🔠 Processing {len(glyphs)} glyphs...")
				for i, thisGlyph in enumerate(glyphs):
					# update progress bar:
					self.w.progress.set((fontIndex + i / len(glyphs)) * 100 / len(theseFonts))

					# glyph counters:
					removeNodeNamesGlyph = 0
					localGuidesGlyph = 0
					removeAnnotationsGlyph = 0
					layerDeletionCount = 0

					self.log(f"🔠 {thisGlyph.name}")

					# layer clean-up:
					for thisLayer in thisGlyph.layers:
						if thisLayer.master == thisFont.selectedFontMaster or not currentMasterOnly:
							if removeNodeNames:
								for thisPath in list(thisLayer.paths) + list(thisLayer.background.paths):
									for thisNode in thisPath.nodes:
										if thisNode.name:
											removeNodeNamesGlyph += 1
											thisNode.setName_(None)

							if removeLocalGuides:
								localGuidesGlyph += len(guidesOf(thisLayer))
								clearGuides(thisLayer)

								localGuidesGlyph += len(guidesOf(thisLayer.background))
								clearGuides(thisLayer.background)

							if removeAnnotations:
								removeAnnotationsGlyph += len(thisLayer.annotations)
								thisLayer.annotations = None

								removeAnnotationsGlyph += len(thisLayer.background.annotations)
								thisLayer.background.annotations = None

							if removeColors:
								# self.log(f"\t🚫 color for layer ‘{thisLayer.name}’")
								thisLayer.color = None

							if userDataLayers:
								# if thisLayer.userData:  # BROKEN IN 3.2
								if thisLayer.userData.keys():
									keysToRemove = [k for k in thisLayer.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
									# self.log(f"\t🚫 layer.userData: {', '.join(keysToRemove)}")
									for keyToRemove in keysToRemove:
										thisLayer.removeUserDataForKey_(keyToRemove)

							if clearBackgroundLayers:
								if thisLayer.background.shapes:
									cleanedBackgroundCount += 1
								thisLayer.background.clear()

					# glyph clean-up:
					if removeBackupLayers:
						for j in range(len(thisGlyph.layers) - 1, -1, -1):
							layerToBeDeleted = thisGlyph.layers[j]
							if layerToBeDeleted.master == thisFont.selectedFontMaster or not currentMasterOnly:
								if not layerToBeDeleted.isMasterLayer and not layerToBeDeleted.isSpecialLayer:
									del thisGlyph.layers[j]
									layerDeletionCount += 1
					if removeGlyphNotes:
						if thisGlyph.note:
							# self.log("\t🚫 glyph note")
							thisGlyph.note = None

					if removeColors:
						# self.log("\t🚫 glyph color")
						thisGlyph.color = None

					if userDataGlyphs:
						if thisGlyph.userData:
							keysToRemove = [k for k in thisGlyph.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
							# self.log(f"\t🚫 glyph.userData: {', '.join(keysToRemove)}")
							for keyToRemove in keysToRemove:
								thisGlyph.removeUserDataForKey_(keyToRemove)

					# report:
					if removeNodeNamesGlyph:
						# self.log(f"\t🚫 {removeNodeNamesGlyph} node names")
						removeNodeNamesFont += removeNodeNamesGlyph
					if localGuidesGlyph:
						# self.log(f"\t🚫 {localGuidesGlyph} local guides")
						localGuidesFont += localGuidesGlyph
					if removeAnnotationsGlyph:
						# self.log(f"\t🚫 {removeAnnotationsGlyph} annotations")
						removeAnnotationsFont += removeAnnotationsGlyph
					if layerDeletionCount:
						# self.log(f"\t🚫 {layerDeletionCount} backup layers")
						layerDeletionCountFont += layerDeletionCount

				# Remove global guides:
				if self.pref("removeGlobalGuides"):
					self.log("📏 Removing global guides ...")
					for thisMaster in thisFont.masters:
						if thisMaster == thisFont.selectedFontMaster or not currentMasterOnly:
							clearGuides(thisMaster)

				# Remove User Data (font level):
				if self.pref("userDataFont"):
					self.log("🧑🏽‍💻📄 Cleaning font.userData")
					if thisFont.userData:
						keysToRemove = [k for k in thisFont.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
						if len(keysToRemove) > 0:
							self.log(
								"\t🚫 %i font.userData entr%s%s%s" % (
									len(keysToRemove),
									"y" if len(keysToRemove) == 1 else "ies",
									": " if len(keysToRemove) > 0 else "",
									", ".join(keysToRemove) if keysToRemove else "",
								)
							)
							for keyToRemove in keysToRemove:
								thisFont.removeUserDataForKey_(keyToRemove)

				# Remove User Data (master levels):
				if self.pref("userDataMasters"):
					for thisMaster in thisFont.masters:
						self.log(f"🧑🏽‍💻Ⓜ️ Cleaning master.userData: {thisMaster.name}")
						if thisMaster.userData:
							keysToRemove = [k for k in thisMaster.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
							if len(keysToRemove) > 0:
								self.log(
									"\t🚫 %i master.userData entr%s: %s" % (
										len(keysToRemove),
										"y" if len(keysToRemove) == 1 else "ies",
										", ".join(keysToRemove) if keysToRemove else "",
									)
								)
								for keyToRemove in keysToRemove:
									thisMaster.removeUserDataForKey_(keyToRemove)

				# Remove User Data (instance levels):
				if self.pref("userDataInstances"):
					for thisInstance in thisFont.instances:
						self.log(f"🧑🏽‍💻ℹ️ Cleaning instance.userData: {thisInstance.name}")
						if thisInstance.userData:
							keysToRemove = [k for k in thisInstance.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
							if len(keysToRemove) > 0:
								self.log(
									"\t🚫 %i instance.userData entr%s: %s" % (
										len(keysToRemove),
										"y" if len(keysToRemove) == 1 else "ies",
										", ".join(keysToRemove) if keysToRemove else "",
									)
								)
								for keyToRemove in keysToRemove:
									thisInstance.removeUserDataForKey_(keyToRemove)

				# full progress bar:
				self.w.progress.set((fontIndex + 1) * 100 / len(theseFonts))

				# report in macro window
				print()
				if removeAnnotationsFont:
					self.log(f"🚫 Removed {removeAnnotationsFont} annotations in font.")
				if layerDeletionCountFont:
					self.log(f"🚫 Removed {layerDeletionCountFont} layers in font.")
				if localGuidesFont:
					self.log(f"🚫 Removed {localGuidesFont} local guides in font.")
				if removeNodeNamesFont:
					self.log(f"🚫 Removed {removeNodeNamesFont} node names in font.")
				if cleanedBackgroundCount:
					self.log(f"🚫 Emptied {cleanedBackgroundCount} layer backgrounds in font.")

			except Exception as e:
				# brings macro window to front and reports error:
				Glyphs.showMacroWindow()
				print(f"😫 Garbage Collection Error: {e}")
				import traceback
				print(traceback.format_exc())
			finally:
				thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

			self.log(f"✅ Done.{' Log in Macro Window.' if self.pref('verbose') else ''}\n")
			if not self.pref("verbose"):
				print("✅ Done.")


GarbageCollection()
