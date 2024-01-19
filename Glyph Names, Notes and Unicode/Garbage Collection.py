# MenuTitle: Garbage Collection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes annotations, glyph notes, guides, and node names.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


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
		windowWidth = 330
		windowHeight = 430
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Garbage Collection",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, lineHeight * 1.8), "Clean frontmost font:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.removeNodeNames = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all node names 🔥❌👌🏻⛔️🧨 in font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeNodeNames.getNSButton().setToolTip_("Deletes node markers, as employed by many mekkablue scripts to mark problematic spots.")
		linePos += lineHeight

		self.w.removeAnnotations = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all annotations 💬➕➖➚◯ in font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeAnnotations.getNSButton().setToolTip_("Deletes annotations created with the Annotation Tool (A), e.g. circles, arrows, and texts.")
		linePos += lineHeight

		self.w.removeLocalGuides = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all local (blue) guides 🔵 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeLocalGuides.getNSButton().setToolTip_("Deletes blue guides.")
		linePos += lineHeight

		self.w.removeGlobalGuides = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all global (red) guides 🔴 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeGlobalGuides.getNSButton().setToolTip_("Deletes red guides.")
		linePos += lineHeight

		self.w.removeGlyphNotes = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all glyph notes in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeGlyphNotes.getNSButton().setToolTip_("Deletes glyph notes as entered in list view or through the Glyph Note Palette (plug-in).")
		linePos += lineHeight

		self.w.removeColors = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all glyph and layer colors 🟠🟡🟢🟣 in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeColors.getNSButton().setToolTip_("Resets all glyph and layer colors to none.")
		linePos += lineHeight

		self.w.clearBackgroundLayers = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Clear all background layers in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.clearBackgroundLayers.getNSButton().setToolTip_("If checked, will clear all background layers (Cmd-B) of all layers.")
		linePos += lineHeight

		self.w.removeBackupLayers = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Remove all backup layers in font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.removeBackupLayers.getNSButton().setToolTip_("If checked, will remove all unused layers, i.e., all non-master, non-color, non-intermediate and non-alternate layers.")
		linePos += lineHeight

		self.w.line1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 6

		self.w.currentMasterOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Limit clean-up to current master only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.currentMasterOnly.getNSButton().setToolTip_("If checked, applies the clean-up to layers of the current font master only. Exception: glyph notes are not master-specific.")
		linePos += lineHeight

		self.w.selectedGlyphsOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Limit clean-up to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("If checked, applies the clean-up only to selected glyphs. Otherwise, to all glyphs in the font.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, 180, 20), "⚠️ Apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.getNSButton().setToolTip_("If checked, will work on ALL currently open fonts; otherwise only the frontmost font file open.")

		self.w.verbose = vanilla.CheckBox((inset + 180, linePos - 1, -inset, 20), "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose.getNSButton().setToolTip_("Verbose reporting in Macro Window (slow).")
		linePos += lineHeight

		self.w.line2 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 6

		self.w.userDataText = vanilla.TextBox((inset, linePos + 2, 115, 14), "Remove userData in", sizeStyle='small', selectable=True)
		self.w.userDataFont = vanilla.CheckBox((inset + 115, linePos - 1, 43, 20), "font", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataMasters = vanilla.CheckBox((inset + 115 + 43, linePos - 1, 63, 20), "masters", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataInstances = vanilla.CheckBox((inset + 115 + 43 + 63, linePos - 1, 75, 20), "instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Remove userData from the frontmost font, its masters, and/or instances.\n\n⚠️ Attention: the font/masters/instances options do NOT respect the ‘Limit’ settings above."
		self.w.userDataText.getNSTextField().setToolTip_(tooltip)
		self.w.userDataFont.getNSButton().setToolTip_(tooltip)
		self.w.userDataMasters.getNSButton().setToolTip_(tooltip)
		self.w.userDataInstances.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.userDataGlyphs = vanilla.CheckBox((inset + 115, linePos - 1, 58, 20), "glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.userDataLayers = vanilla.CheckBox((inset + 115 + 58, linePos - 1, -inset, 20), "layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Remove userData from glyphs and/or layers. Will respect the ‘Limit’ settings above."
		self.w.userDataGlyphs.getNSButton().setToolTip_(tooltip)
		self.w.userDataLayers.getNSButton().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.userDataKeysText = vanilla.TextBox((inset, linePos + 3, 92, 14), "…only keys with:", sizeStyle='small', selectable=True)
		self.w.userDataKeys = vanilla.EditText((inset + 92, linePos, -inset - 25, 19), "UFO, fontlab, public", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Comma-separated list of search strings for userData keys to delete. Leave empty to remove all."
		self.w.userDataKeysText.getNSTextField().setToolTip_(tooltip)
		self.w.userDataKeys.getNSTextField().setToolTip_(tooltip)
		self.w.userDataUpdate = vanilla.SquareButton((-inset - 20, linePos + 1, -inset, 18), "↺", sizeStyle="small", callback=self.updateUserDataUI)
		self.w.userDataUpdate.getNSButton().setToolTip_("Add the userData keys of frontmost font.")
		linePos += lineHeight + 3

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		self.w.statusText = vanilla.TextBox((inset, -17 - inset, -80 - inset, 14), "", sizeStyle='small', selectable=False)

		self.updateUI()

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Clean", sizeStyle='regular', callback=self.GarbageCollectionMain)
		self.w.setDefaultButton(self.w.runButton)

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
				userDataKeys = [k.strip() for k in self.pref("userDataKeys").split(",")]

				# set up counters:
				removeNodeNamesFont = 0
				localGuidesFont = 0
				removeAnnotationsFont = 0
				layerDeletionCountFont = 0

				# go through glyphs:
				print(f"🔠 Processing {len(glyphs)} glyphs...")
				for i, thisGlyph in enumerate(glyphs):
					# update progress bar:
					self.w.progress.set((fontIndex + 1) * int(100 * i / len(glyphs)) / len(theseFonts))

					# glyph counters:
					removeNodeNamesGlyph = 0
					localGuidesGlyph = 0
					removeAnnotationsGlyph = 0
					layerDeletionCount = 0

					self.log(f"🔤 Cleaning {thisGlyph.name} ...")

					# layer clean-up:
					for thisLayer in thisGlyph.layers:
						if thisLayer.master == thisFont.selectedFontMaster or not currentMasterOnly:
							if removeNodeNames:
								for thisPath in thisLayer.paths:
									for thisNode in thisPath.nodes:
										if thisNode.name:
											removeNodeNamesGlyph += 1
											thisNode.name = None
							if removeLocalGuides:
								localGuidesGlyph += len(thisLayer.guideLines)
								thisLayer.guideLines = None
							if removeAnnotations:
								removeAnnotationsGlyph += len(thisLayer.annotations)
								thisLayer.annotations = None
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
							thisMaster.guideLines = None

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
