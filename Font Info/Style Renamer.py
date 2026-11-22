# MenuTitle: Style Renamer
__doc__ = """
Batch-add a name particle to your style names, or batch-remove it from them. Useful for switching all your styles from italic to roman naming and vice versa.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, INSTANCETYPESINGLE, Message
from mekkablue import mekkaObject, UpdateButton, fontFileName, makeWindowResizable


particleDefault = "Italic"
elidablePartDefault = "Regular"
menuOptions = (
	"Subtract particle from",
	"Add particle at the end of",
	"Add particle before",
)


class StyleRenamer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"particle": particleDefault,
		"subtractOrAdd": 1,
		"elidablePart": elidablePartDefault,
		"includeInactiveInstances": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 300
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Style Renamer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15

		self.w.subtractOrAdd = vanilla.PopUpButton("auto", menuOptions, sizeStyle='small', callback=self.savePrefsAndUpdatePreview)
		self.w.subtractOrAddText = vanilla.TextBox("auto", "all instance names", sizeStyle='small', selectable=True)
		tooltipText = "Choose here if you want to add the chosen particle name to all styles, or remove it from them."
		self.w.subtractOrAdd.setToolTip(tooltipText)
		self.w.subtractOrAddText.setToolTip(tooltipText)

		self.w.particleText = vanilla.TextBox("auto", "Particle", sizeStyle='small', selectable=True)
		self.w.particle = vanilla.EditText("auto", particleDefault, callback=self.savePrefsAndUpdatePreview, sizeStyle='small')
		tooltipText = "This is the name part you want to add to the name, or erase from it. Typically something like ‘%s’." % particleDefault
		self.w.particleText.setToolTip(tooltipText)
		self.w.particle.setToolTip(tooltipText)
		self.w.particleUpdate = UpdateButton("auto", callback=self.update)
		self.w.particleUpdate.setToolTip("Will reset the name particle to ‘%s’." % particleDefault)

		self.w.elidablePartText = vanilla.TextBox("auto", "Elidable", sizeStyle='small', selectable=True)
		self.w.elidablePart = vanilla.EditText("auto", elidablePartDefault, callback=self.savePrefsAndUpdatePreview, sizeStyle='small')
		tooltipText = "Typically something like ‘%s’. This is the stub name part that will be the name of the style if it would be otherwise empty, e.g., remove the word ‘%s’ from the style ‘%s’, and the style name would be empty, so the elidable name kicks in, and the style is ‘%s’.\nOr, the other way around, the part of the name that gets deleted from the name, as soon as you add any particle to it. E.g., you add ‘%s’ to ‘%s’, and instead of calling it ‘%s %s’, it will be simply ‘%s’." % (
			elidablePartDefault, particleDefault, particleDefault, elidablePartDefault, particleDefault, elidablePartDefault, elidablePartDefault, particleDefault, particleDefault
		)
		self.w.elidablePartText.setToolTip(tooltipText)
		self.w.elidablePart.setToolTip(tooltipText)
		self.w.elidablePartUpdate = UpdateButton("auto", callback=self.update)
		self.w.elidablePartUpdate.setToolTip("Will reset the elidable part of style name to ‘%s’." % elidablePartDefault)

		self.w.includeInactiveInstances = vanilla.CheckBox("auto", "Include inactive instances", value=False, callback=self.savePrefsAndUpdatePreview, sizeStyle='small')
		self.w.includeInactiveInstances.setToolTip("If turned, will add/remove the particle to/from all instances, rather than just the active ones.")

		self.w.preview = vanilla.TextEditor("auto", text="", readOnly=True, checksSpelling=False)
		self.w.preview.setToolTip("Preview of the style names before and after renaming.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Rename", callback=self.StyleRenamerMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content, except for the preview, which takes the surplus height
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.preview.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned, hug their text and share one width:
		for labelName in ("particleText", "elidablePartText"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[subtractOrAdd(>=150)]-gap-[subtractOrAddText]-(>=inset)-|",
				"H:|-inset-[particleText]-gap-[particle]-gap-[particleUpdate]-inset-|",
				"H:|-inset-[elidablePartText]-gap-[elidablePart]-gap-[elidablePartUpdate]-inset-|",
				"H:|-inset-[includeInactiveInstances]-(>=inset)-|",
				"H:|-inset-[preview]-inset-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[subtractOrAdd]-row-[particle]-row-[elidablePart]-row-[includeInactiveInstances]-row-[preview(>=70)]-inset-[runButton]-inset-|",
				{"view1": self.w.subtractOrAddText, "attribute1": "centerY", "view2": self.w.subtractOrAdd, "attribute2": "centerY"},
				{"view1": self.w.particleText, "attribute1": "centerY", "view2": self.w.particle, "attribute2": "centerY"},
				{"view1": self.w.particleUpdate, "attribute1": "centerY", "view2": self.w.particle, "attribute2": "centerY"},
				{"view1": self.w.elidablePartText, "attribute1": "centerY", "view2": self.w.elidablePart, "attribute2": "centerY"},
				{"view1": self.w.elidablePartUpdate, "attribute1": "centerY", "view2": self.w.elidablePart, "attribute2": "centerY"},
				{"view1": self.w.elidablePartText, "attribute1": "width", "view2": self.w.particleText, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8},
		)

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Load Settings:
		self.LoadPreferences()

		self.updatePreviewText()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender is self.w.elidablePartUpdate:
			self.w.elidablePart.set(elidablePartDefault)
		if sender is self.w.particleUpdate:
			self.w.particle.set(particleDefault)
		self.savePrefsAndUpdatePreview()
	
	def savePrefsAndUpdatePreview(self, sender=None):
		self.SavePreferences()
		self.updatePreviewText()

	def updatePreviewText(self, sender=None):
		previewText = ""
		thisFont = Glyphs.font  # frontmost font
		if thisFont:
			fileName = fontFileName(thisFont)
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

		self.w.preview.set(previewText.strip())

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
					modifiedOriginalName = modifiedOriginalName.replace(searchTerm, delim)

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
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Style Renamer Report for %s" % thisFont.familyName)
				print(fontFileName(thisFont, fullPath=True))
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
						if (instanceIsExporting or includeInactiveInstances) and thisInstance.type == INSTANCETYPESINGLE:
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
