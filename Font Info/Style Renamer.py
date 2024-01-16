# MenuTitle: Style Renamer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-add a name particle to your style names, or batch-remove it from them. Useful for switching all your styles from italic to roman naming and vice versa.
"""

import vanilla
from AppKit import NSFileManager
from GlyphsApp import Glyphs, INSTANCETYPESINGLE, Message


particleDefault = "Italic"
elidablePartDefault = "Regular"
menuOptions = (
	"Subtract particle from",
	"Add particle at the end of",
	"Add particle before",
)


class StyleRenamer(object):
	prefID = "com.mekkablue.StyleRenamer"
	prefDict = {
		# "prefName": defaultValue,
		"particle": particleDefault,
		"subtractOrAdd": 1,
		"elidablePart": elidablePartDefault,
		"includeInactiveInstances": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 285
		windowHeight = 190
		windowWidthResize = 200  # user can resize width by this value
		windowHeightResize = 800  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Style Renamer",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 24
		column = 55

		self.w.subtractOrAdd = vanilla.PopUpButton((inset, linePos, 160, 17), menuOptions, sizeStyle='small', callback=self.SavePreferences)
		self.w.subtractOrAddText = vanilla.TextBox((inset + 165, linePos + 2, -inset, 14), "all instance names:", sizeStyle='small', selectable=True)
		tooltipText = "Choose here if you want to add the chosen particle name to all styles, or remove it from them."
		self.w.subtractOrAdd.getNSPopUpButton().setToolTip_(tooltipText)
		self.w.subtractOrAddText.getNSTextField().setToolTip_(tooltipText)
		linePos += lineHeight

		self.w.particleText = vanilla.TextBox((inset, linePos + 3, column, 14), "Particle:", sizeStyle='small', selectable=True)
		self.w.particle = vanilla.EditText((inset + column, linePos, -inset - 25, 19), particleDefault, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "This is the name part you want to add to the name, or erase from it. Typically something like ‘%s’." % particleDefault
		self.w.particleText.getNSTextField().setToolTip_(tooltipText)
		self.w.particle.getNSTextField().setToolTip_(tooltipText)
		self.w.particleUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update)
		self.w.particleUpdate.getNSButton().setToolTip_("Will reset the name particle to ‘%s’." % particleDefault)
		linePos += lineHeight

		self.w.elidablePartText = vanilla.TextBox((inset, linePos + 3, column, 14), "Elidable:", sizeStyle='small', selectable=True)
		self.w.elidablePart = vanilla.EditText((inset + column, linePos, -inset - 25, 19), elidablePartDefault, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Typically something like ‘%s’. This is the stub name part that will be the name of the style if it would be otherwise empty, e.g., remove the word ‘%s’ from the style ‘%s’, and the style name would be empty, so the elidable name kicks in, and the style is ‘%s’.\nOr, the other way around, the part of the name that gets deleted from the name, as soon as you add any particle to it. E.g., you add ‘%s’ to ‘%s’, and instead of calling it ‘%s %s’, it will be simply ‘%s’." % (
			elidablePartDefault, particleDefault, particleDefault, elidablePartDefault, particleDefault, elidablePartDefault, elidablePartDefault, particleDefault, particleDefault
		)
		self.w.elidablePartText.getNSTextField().setToolTip_(tooltipText)
		self.w.elidablePart.getNSTextField().setToolTip_(tooltipText)
		self.w.elidablePartUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update)
		self.w.elidablePartUpdate.getNSButton().setToolTip_("Will reset the elidable part of style name to ‘%s’." % elidablePartDefault)
		linePos += lineHeight

		self.w.includeInactiveInstances = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include inactive instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeInactiveInstances.getNSButton().setToolTip_("If turned, will add/remove the particle to/from all instances, rather than just the active ones.")
		linePos += lineHeight

		self.w.preview = vanilla.Box((inset, linePos, -inset, -30 - inset))
		self.w.preview.previewText = vanilla.TextBox((5, 1, -5, -1), "", sizeStyle='small', selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Rename", sizeStyle='regular', callback=self.StyleRenamerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Style Renamer' could not load preferences. Will resort to defaults")

		self.fileManager = NSFileManager.alloc().init()
		self.updatePreviewText()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender is self.w.elidablePartUpdate:
			self.w.elidablePart.set(elidablePartDefault)
		if sender is self.w.particleUpdate:
			self.w.particle.set(particleDefault)
		self.SavePreferences()

	def updatePreviewText(self, sender=None):
		previewText = ""
		thisFont = Glyphs.font  # frontmost font
		if thisFont:
			fileName = self.fileManager.displayNameAtPath_(thisFont.filepath)
			previewText += "%s\n(File: %s)\n" % (thisFont.familyName, fileName)

			# read out user settings:
			particle = self.pref("particle")
			shouldAddParticle = self.pref("subtractOrAdd")
			elidablePart = self.pref("elidablePart")
			includeInactiveInstances = self.pref("includeInactiveInstances")

			# clean up user entry:
			elidablePart = elidablePart.strip()
			particle = particle.strip()

			if particle:
				for thisInstance in thisFont.instances:
					if Glyphs.buildNumber > 3198:
						instanceIsExporting = thisInstance.exports
					else:
						instanceIsExporting = thisInstance.active
					if (instanceIsExporting or includeInactiveInstances) and thisInstance.type == INSTANCETYPESINGLE:
						newName = self.renameInstance(thisInstance, shouldAddParticle, particle, elidablePart)
						if newName:
							previewText += "▸ %s → %s\n" % (thisInstance.name, newName)
						else:
							previewText += "▸ (unchanged: %s)\n" % thisInstance.name

		self.w.preview.previewText.set(previewText.strip())

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.updatePreviewText()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set(self.pref(prefName))
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def renameInstance(self, thisInstance, shouldAddParticle, particle, elidablePart):
		originalName = thisInstance.name.strip()
		newName = ""
		if shouldAddParticle:
			if shouldAddParticle == 1:
				nameParts = (originalName, particle.strip())  # POSTFIX
			else:  # shouldAddParticle == 2
				nameParts = (particle.strip(), originalName)  # PREFIX

			newName = "%s %s" % nameParts
			if elidablePart:
				newNameParts = newName.split()
				while elidablePart in newNameParts:
					newNameParts.remove(elidablePart)
				newName = " ".join(newNameParts)
		else:
			# SUBTRACT PARTICLE
			if particle in originalName:
				if particle == originalName:
					if elidablePart:
						# typically "Italic" -> "Regular"
						newName = elidablePart
				elif len(particle.split()) == 1:
					nameParts = originalName.split()
					newName = " ".join([part for part in nameParts if part != particle])
				elif len(particle.split()) > 1:
					# PROBLEM: removing particle "Bold Italic" (with whitespace) should leave "SemiBold Italic" intact
					delim = "🧙"
					modifiedOriginalName = delim.join(originalName.split())
					modifiedParticle = delim.join(particle.split())

					# remove particle in the MIDDLE of the name:
					searchTerm = "%s%s%s" % (delim, modifiedParticle, delim)
					modifiedOriginalName = modifiedOriginalName.replace(modifiedParticle, delim)

					# remove particle at the END of the name:
					searchTerm = "%s%s" % (delim, modifiedParticle)
					if modifiedOriginalName.endswith(searchTerm):
						modifiedOriginalName = modifiedOriginalName[:-len(searchTerm)]

					# remove particle at the BEGINNING of the name:
					searchTerm = "%s%s" % (modifiedParticle, delim)
					if modifiedOriginalName.startswith(searchTerm):
						modifiedOriginalName = modifiedOriginalName[len(searchTerm):]

					newName = " ".join(modifiedOriginalName.split(delim))
		return newName

	def StyleRenamerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Style Renamer' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Style Renamer Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				# read out user settings:
				particle = self.pref("particle")
				shouldAddParticle = self.pref("subtractOrAdd")
				elidablePart = self.pref("elidablePart")
				includeInactiveInstances = self.pref("includeInactiveInstances")

				# clean up user entry:
				elidablePart = elidablePart.strip()
				particle = particle.strip()

				if not particle:
					Message(
						title="No Particle Provided",
						message=f"Please enter a particle like ‘{particleDefault}’ to add to or subtract from style names in the frontmost fonts.",
						OKButton=None
					)
				else:
					renameCount = 0
					for thisInstance in thisFont.instances:
						if Glyphs.buildNumber > 3198:
							instanceIsExporting = thisInstance.exports
						else:
							instanceIsExporting = thisInstance.active
						if instanceIsExporting or includeInactiveInstances:
							originalName = thisInstance.name
							newName = self.renameInstance(thisInstance, shouldAddParticle, particle, elidablePart)

							# clean up any double spaces that may be left in the name:
							while "  " in newName:
								newName = newName.replace("  ", " ")

							if newName:
								if thisInstance.name != newName:
									print("✅ %s → %s" % (thisInstance.name, newName))
									thisInstance.name = newName
									renameCount += 1
								else:
									print("⚠️ %s unchanged." % originalName)
							else:
								print("❌ Cannot rename ‘%s’: style name would be empty." % originalName)

					# Final report:
					Glyphs.showNotification(
						u"%s: Done" % (thisFont.familyName),
						u"Style Renamer renamed %i style%s. Details in Macro Window" % (
							renameCount,
							"" if renameCount == 1 else "s",
						),
					)
					print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Style Renamer Error: %s" % e)
			import traceback
			print(traceback.format_exc())


StyleRenamer()
