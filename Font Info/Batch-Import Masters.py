# MenuTitle: Batch-Import Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Import many masters at once with the Import Master parameter.
"""

import vanilla
from AppKit import NSNotificationCenter
from GlyphsApp import Glyphs, GSCustomParameter, Message
from mekkablue import mekkaObject


def menuForFonts(fonts):
	menu = []
	for i, font in enumerate(fonts):
		if font.filepath:
			path = font.filepath.lastPathComponent()
			menu.append(f"{i + 1}. {font.familyName} ({path})")
	if menu:
		return menu
	else:
		return ("⚠️ No saved font files. Save fonts and press Update.", )


def masterNameParticlesForFont(font, separators=".,-:/"):
	allParticles = []
	for m in font.masters:
		particles = m.name.split()
		for sep in separators:
			newParticles = []
			for particle in particles:
				newParticles.extend(particle.split(sep))
			particles = newParticles
		allParticles.extend(particles)
	return set(allParticles)


def cleanParametersFromFont(font, cpName="Import Master"):
	while font.customParameters[cpName]:
		font.removeObjectFromCustomParametersForKey_(cpName)


def importMastersFromFontToFont(importedFont, targetFont, searchFor="", useRelativePath=False):
	importedPath = importedFont.filepath
	importedFileName = importedPath.lastPathComponent()
	importedDir = importedPath.stringByDeletingLastPathComponent()
	importedRelativePath = importedPath.relativePathFromBaseDirPath_(targetFont.filepath.stringByDeletingLastPathComponent())
	for importedMaster in importedFont.masters:
		if searchFor and searchFor not in importedMaster.name:
			continue
		cpName = "Import Master"
		cpValue = {
			"Master": importedMaster.name,
			"Path": importedRelativePath if useRelativePath else importedPath,
		}
		cp = GSCustomParameter(cpName, cpValue)
		targetFont.customParameters.append(cp)
		print(f"✅ Added master: {importedMaster.name}")


class BatchImportMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"sourceFont": 0,
		"targetFont": 0,
		"searchFor": "",
		"useRelativePath": True,
		"resetParameters": True,
	}

	currentFonts = Glyphs.fonts

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 230
		windowWidthResize = 300  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Batch-Import Masters",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Batch-add ‘Import Master’ parameters to target font:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		indent = 75
		self.w.targetFontText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Target font:", sizeStyle="small", selectable=True)
		self.w.targetFont = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font that receives the Import Master parameters."
		self.w.targetFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.targetFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.sourceFontText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Source font:", sizeStyle="small", selectable=True)
		self.w.sourceFont = vanilla.PopUpButton((inset + indent, linePos, -inset, 17), (), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "The font the custom parameters refer to."
		self.w.sourceFont.getNSPopUpButton().setToolTip_(tooltip)
		self.w.sourceFontText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		indent = 195
		self.w.searchForText = vanilla.TextBox((inset, linePos + 2, indent, 14), "Source master name must contain:", sizeStyle="small", selectable=True)
		self.w.searchFor = vanilla.ComboBox((inset + indent, linePos - 1, -inset, 19), (masterNameParticlesForFont(self.currentFonts[0]) if self.currentFonts else ()), sizeStyle="small", callback=self.SavePreferences)
		tooltip = "If set, will only import masters that contain this name particle. Leave empty to import all masters of the source font."
		self.w.searchFor.getNSComboBox().setToolTip_(tooltip)
		self.w.searchForText.getNSTextField().setToolTip_(tooltip)
		linePos += lineHeight

		self.w.useRelativePath = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Use relative font path in parameter values", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.useRelativePath.getNSButton().setToolTip_("If set, will add a relative path rather than an absolute path. Better for git repos.")
		linePos += lineHeight

		self.w.resetParameters = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete all existing Import Master parameters in target font", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.resetParameters.getNSButton().setToolTip_("If set, will first clean out all existing ‘Import Master’ parameters, so the font will only have the ‘Import Master’ parameters you add.")
		linePos += lineHeight

		self.w.suppressMessage = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Suppress confirmation dialog", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.suppressMessage.getNSButton().setToolTip_("After you add the masters, there is a success dialog confirming the import. If it gets on your nerves, check this checkbox.")
		linePos += lineHeight

		# Update Button:
		self.w.updateButton = vanilla.Button((inset, -20 - inset, 100, -inset), "Update", callback=self.UpdateUI)
		self.w.updateButton.getNSButton().setToolTip_("Will update all the menus and buttons of this window. Click here if you opened or closed a font since you invoked the script, or after you changed the source font.")

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - inset, -20 - inset, -inset, -inset), "Import", callback=self.BatchImportMastersMain)
		self.w.setDefaultButton(self.w.runButton)

		self.UpdateUI()

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.currentFonts = [f for f in Glyphs.fonts if f.filepath]
		menu = menuForFonts(self.currentFonts)
		self.w.sourceFont.setItems(menu)
		self.w.targetFont.setItems(menu)

		if self.currentFonts:
			self.w.sourceFont.enable(True)
			self.w.targetFont.enable(True)

			sourceFontIndex = self.pref("sourceFont")
			self.w.sourceFont.set(sourceFontIndex if sourceFontIndex is not None and sourceFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("sourceFont")] = self.w.sourceFont.get()

			targetFontIndex = self.pref("targetFont")
			self.w.targetFont.set(targetFontIndex if targetFontIndex is not None and targetFontIndex < len(menu) else 0)
			Glyphs.defaults[self.domain("targetFont")] = self.w.targetFont.get()

			# update search combobox :
			if sender != self.w.searchFor:
				searchBoxContent = self.w.searchFor.get()
				choiceIndex = self.w.sourceFont.get()
				if choiceIndex < len(self.currentFonts):
					sourceFont = self.currentFonts[choiceIndex]
					particles = masterNameParticlesForFont(sourceFont)
					self.w.searchFor.setItems(particles)
					self.w.searchFor.set(searchBoxContent)  # circumvent bug
		else:
			Glyphs.defaults[self.domain("sourceFont")] = 0
			Glyphs.defaults[self.domain("targetFont")] = 0
			self.w.sourceFont.enable(False)
			self.w.targetFont.enable(False)

		# double check
		self.w.runButton.enable(self.pref("sourceFont") != self.pref("targetFont"))

	def BatchImportMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Batch-Import Masters Report")

				font = self.currentFonts[self.pref("targetFont")]
				importedFont = self.currentFonts[self.pref("sourceFont")]

				print("Target:", font.filepath.lastPathComponent())
				print("Source:", importedFont.filepath.lastPathComponent())
				print()

				font.disableUpdateInterface()
				try:
					if self.prefBool("resetParameters"):
						cleanParametersFromFont(font, cpName="Import Master")
					importMastersFromFontToFont(importedFont, font, searchFor=self.pref("searchFor"), useRelativePath=self.pref("useRelativePath"))

				except Exception as e:
					raise e
				finally:
					font.enableUpdateInterface()
					for thisUI in (font.currentTab, font.fontView):
						NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisUI)
					print("\n✅ Done.")
					if not self.pref("suppressMessage"):
						Message(
							title="Imported Masters",
							message="Successfully imported all masters. Consider saving, closing and reopening the file in case you experience UI glitches.",
							OKButton=None,
						)

				# self.w.close()  # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Batch-Import Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


BatchImportMasters()
