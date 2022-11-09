#MenuTitle: Garbage Collection
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes annotations, glyph notes, guides, and node names.
"""

import vanilla

class GarbageCollection(object):
	prefID = "com.mekkablue.GarbageCollection"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 450
		windowWidthResize = 50 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Garbage Collection", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.GarbageCollection.mainwindow" # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, lineHeight * 1.8), "Removes the following items from the glyphs in the frontmost font:", sizeStyle='small', selectable=True
			)
		linePos += 1.8 * lineHeight

		self.w.removeNodeNames = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all node names 🔥❌👌🏻⛔️🧨 in font", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeNodeNames.getNSButton().setToolTip_("Deletes node markers, as employed by many mekkablue scripts to mark problematic spots.")
		linePos += lineHeight

		self.w.removeAnnotations = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all annotations 💬➕➖➚◯ in font", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeAnnotations.getNSButton().setToolTip_("Deletes annotations created with the Annotation Tool (A), e.g. circles, arrows, and texts.")
		linePos += lineHeight

		self.w.removeLocalGuides = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all local (blue) guides 🔵 in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeLocalGuides.getNSButton().setToolTip_("Deletes blue guides.")
		linePos += lineHeight

		self.w.removeGlobalGuides = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all global (red) guides 🔴 in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeGlobalGuides.getNSButton().setToolTip_("Deletes red guides.")
		linePos += lineHeight

		self.w.removeGlyphNotes = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all glyph notes in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeGlyphNotes.getNSButton().setToolTip_("Deletes glyph notes as entered in list view or through the Glyph Note Palette (plug-in).")
		linePos += lineHeight

		self.w.removeColors = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all glyph and layer colors 🟠🟡🟢🟣🟤 in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeColors.getNSButton().setToolTip_("Resets all glyph and layer colors to none.")
		linePos += lineHeight

		self.w.clearBackgroundLayers = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Clear all background layers in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.clearBackgroundLayers.getNSButton().setToolTip_("If checked, will clear all background layers (Cmd-B) of all layers.")
		linePos += lineHeight

		self.w.removeBackupLayers = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Remove all backup layers in font", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.removeBackupLayers.getNSButton(
		).setToolTip_("If checked, will remove all unused layers, i.e., all non-master, non-color, non-intermediate and non-alternate layers.")
		linePos += lineHeight

		self.w.line1 = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 6

		self.w.currentMasterOnly = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Limit clean-up to current master only", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.currentMasterOnly.getNSButton(
		).setToolTip_("If checked, applies the clean-up to layers of the current font master only. Exception: glyph notes are not master-specific.")
		linePos += lineHeight

		self.w.selectedGlyphsOnly = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Limit clean-up to selected glyphs only", value=False, callback=self.SavePreferences, sizeStyle='small'
			)
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("If checked, applies the clean-up only to selected glyphs. Otherwise, to all glyphs in the font.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allFonts.getNSButton().setToolTip_("If checked, will work on ALL currently open fonts; otherwise only the frontmost font file open.")
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
		self.w.userDataKeys = vanilla.EditText((inset + 92, linePos, -inset, 19), "UFO, fontlab, public", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Comma-separated list of search strings for userData keys to delete. Leave empty to remove all."
		self.w.userDataKeysText.getNSTextField().setToolTip_(tooltip)
		self.w.userDataKeys.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight + 3

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos += lineHeight

		self.w.statusText = vanilla.TextBox((inset, -17 - inset, -80 - inset, 14), "", sizeStyle='small', selectable=False)

		self.guiUpdate()

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Clean", sizeStyle='regular', callback=self.GarbageCollectionMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Garbage Collection' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def changeTitle(self, uiItem, toString):
		fromStrings = (
			"in current master",
			"in fontss", # just in case
			"in fonts",
			"in font",
			)
		currentTitle = uiItem.getTitle()
		for fromString in fromStrings:
			if currentTitle.endswith(fromString):
				newTitle = currentTitle.replace(fromString, toString)
				uiItem.setTitle(newTitle)
				return

	def guiUpdate(self, sender=None):
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

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults[self.domain("removeNodeNames")] = self.w.removeNodeNames.get()
			Glyphs.defaults[self.domain("removeLocalGuides")] = self.w.removeLocalGuides.get()
			Glyphs.defaults[self.domain("removeGlobalGuides")] = self.w.removeGlobalGuides.get()
			Glyphs.defaults[self.domain("removeAnnotations")] = self.w.removeAnnotations.get()
			Glyphs.defaults[self.domain("removeGlyphNotes")] = self.w.removeGlyphNotes.get()
			Glyphs.defaults[self.domain("removeColors")] = self.w.removeColors.get()
			Glyphs.defaults[self.domain("clearBackgroundLayers")] = self.w.clearBackgroundLayers.get()
			Glyphs.defaults[self.domain("removeBackupLayers")] = self.w.removeBackupLayers.get()

			Glyphs.defaults[self.domain("userDataFont")] = self.w.userDataFont.get()
			Glyphs.defaults[self.domain("userDataMasters")] = self.w.userDataMasters.get()
			Glyphs.defaults[self.domain("userDataInstances")] = self.w.userDataInstances.get()
			Glyphs.defaults[self.domain("userDataGlyphs")] = self.w.userDataGlyphs.get()
			Glyphs.defaults[self.domain("userDataLayers")] = self.w.userDataLayers.get()
			Glyphs.defaults[self.domain("userDataKeys")] = self.w.userDataKeys.get()

			Glyphs.defaults[self.domain("currentMasterOnly")] = self.w.currentMasterOnly.get()
			Glyphs.defaults[self.domain("selectedGlyphsOnly")] = self.w.selectedGlyphsOnly.get()
			Glyphs.defaults[self.domain("allFonts")] = self.w.allFonts.get()

			self.guiUpdate(sender=sender)
		except:
			return False

		return True

	def LoadPreferences(self, sender=None):
		try:
			Glyphs.registerDefault(self.domain("removeNodeNames"), 1)
			Glyphs.registerDefault(self.domain("removeLocalGuides"), 0)
			Glyphs.registerDefault(self.domain("removeGlobalGuides"), 0)
			Glyphs.registerDefault(self.domain("removeAnnotations"), 1)
			Glyphs.registerDefault(self.domain("removeGlyphNotes"), 0)
			Glyphs.registerDefault(self.domain("removeColors"), 0)
			Glyphs.registerDefault(self.domain("clearBackgroundLayers"), 0)
			Glyphs.registerDefault(self.domain("removeBackupLayers"), 0)

			Glyphs.registerDefault(self.domain("userDataFont"), 0)
			Glyphs.registerDefault(self.domain("userDataMasters"), 0)
			Glyphs.registerDefault(self.domain("userDataInstances"), 0)
			Glyphs.registerDefault(self.domain("userDataGlyphs"), 0)
			Glyphs.registerDefault(self.domain("userDataLayers"), 0)
			Glyphs.registerDefault(self.domain("userDataKeys"), "UFO, fontlab, public")

			Glyphs.registerDefault(self.domain("currentMasterOnly"), 0)
			Glyphs.registerDefault(self.domain("selectedGlyphsOnly"), 0)
			Glyphs.registerDefault(self.domain("allFonts"), 0)

			self.w.removeNodeNames.set(self.pref("removeNodeNames"))
			self.w.removeLocalGuides.set(self.pref("removeLocalGuides"))
			self.w.removeGlobalGuides.set(self.pref("removeGlobalGuides"))
			self.w.removeAnnotations.set(self.pref("removeAnnotations"))
			self.w.removeGlyphNotes.set(self.pref("removeGlyphNotes"))
			self.w.removeColors.set(self.pref("removeColors"))
			self.w.clearBackgroundLayers.set(self.pref("clearBackgroundLayers"))
			self.w.removeBackupLayers.set(self.pref("removeBackupLayers"))

			self.w.userDataFont.set(self.pref("userDataFont"))
			self.w.userDataMasters.set(self.pref("userDataMasters"))
			self.w.userDataInstances.set(self.pref("userDataInstances"))
			self.w.userDataGlyphs.set(self.pref("userDataGlyphs"))
			self.w.userDataLayers.set(self.pref("userDataLayers"))
			self.w.userDataKeys.set(self.pref("userDataKeys"))

			self.w.currentMasterOnly.set(self.pref("currentMasterOnly"))
			self.w.selectedGlyphsOnly.set(self.pref("selectedGlyphsOnly"))
			self.w.allFonts.set(self.pref("allFonts"))

			self.guiUpdate(sender=sender)
		except:
			return False

		return True

	def log(self, msg):
		try:
			print("\t%s" % msg)
			self.w.statusText.set(msg.strip())
		except Exception as e:
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
		if not self.SavePreferences(self):
			print("Note: 'Garbage Collection' could not write preferences.")

		# find out about what the fonts are:
		currentMasterOnly = self.pref("currentMasterOnly")
		allFonts = self.pref("allFonts")
		if allFonts and not currentMasterOnly:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font, )

		for fontIndex, thisFont in enumerate(theseFonts):
			try:
				thisFont.disableUpdateInterface() # suppresses UI updates in Font View

				print("🗑 Garbage Collection Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print("📄 %s" % thisFont.filepath)
				else:
					print("⚠️ file not saved yet")

				if self.pref("selectedGlyphsOnly"):
					glyphs = [l.parent for l in thisFont.selectedLayers]
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
				for i, thisGlyph in enumerate(glyphs):
					# update progress bar:
					self.w.progress.set((fontIndex + 1) * int(100 * i / len(glyphs)) / len(theseFonts))

					# glyph counters:
					removeNodeNamesGlyph = 0
					localGuidesGlyph = 0
					removeAnnotationsGlyph = 0
					layerDeletionCount = 0

					self.log("🔠 Cleaning %s ..." % thisGlyph.name)

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
								thisLayer.color = None
							if userDataLayers:
								if thisLayer.userData:
									keysToRemove = [k for k in thisLayer.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
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
							self.log("\t🚫 glyph note")
							thisGlyph.note = None
					if removeColors:
						thisGlyph.color = None
					if userDataGlyphs:
						if thisGlyph.userData:
							keysToRemove = [k for k in thisGlyph.userData.keys() if self.shouldBeRemoved(k, userDataKeys)]
							for keyToRemove in keysToRemove:
								thisGlyph.removeUserDataForKey_(keyToRemove)

					# report:
					if removeNodeNamesGlyph:
						self.log("\t🚫 %i node names" % removeNodeNamesGlyph)
						removeNodeNamesFont += removeNodeNamesGlyph
					if localGuidesGlyph:
						self.log("\t🚫 %i local guides" % localGuidesGlyph)
						localGuidesFont += localGuidesGlyph
					if removeAnnotationsGlyph:
						self.log("\t🚫 %i annotations" % removeAnnotationsGlyph)
						removeAnnotationsFont += removeAnnotationsGlyph
					if layerDeletionCount:
						self.log("\t🚫 %i backup layers" % layerDeletionCount)
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
						self.log("🧑🏽‍💻Ⓜ️ Cleaning master.userData: %s" % thisMaster.name)
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
						self.log("🧑🏽‍💻ℹ️ Cleaning instance.userData: %s" % thisInstance.name)
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
					self.log("✅ Removed %i annotations in font." % removeAnnotationsFont)
				if layerDeletionCountFont:
					self.log("✅ Removed %i layers in font." % layerDeletionCountFont)
				if localGuidesFont:
					self.log("✅ Removed %i local guides in font." % localGuidesFont)
				if removeNodeNamesFont:
					self.log("✅ Removed %i node names in font." % removeNodeNamesFont)

			except Exception as e:
				# brings macro window to front and reports error:
				Glyphs.showMacroWindow()
				print("😫 Garbage Collection Error: %s" % e)
				import traceback
				print(traceback.format_exc())
			finally:
				thisFont.enableUpdateInterface() # re-enables UI updates in Font View

			self.log("✅ Done. Log in Macro Window.\n")

GarbageCollection()
