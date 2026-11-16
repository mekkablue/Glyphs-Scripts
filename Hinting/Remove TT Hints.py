# MenuTitle: Remove TT Hints
__doc__ = """
Deletes a user-specified set of TT instructions throughout the current font, the selected master and/or the selected glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, TTSTEM, TTANCHOR, TTALIGN, TTINTERPOLATE, TTDIAGONAL, TTDELTA, Message
from mekkablue import mekkaObject


class RemoveTTHints(mekkaObject):
	prefDict = {
		"where": 0,

		"hStems": 0,
		"hAnchors": 0,
		"hAlign": 0,
		"hInterpolate": 0,
		"hDiagonal": 0,
		"hDelta": 0,

		"vStems": 0,
		"vAnchors": 0,
		"vAlign": 0,
		"vInterpolate": 0,
		"vDiagonal": 0,
		"vDelta": 0,
	}
	wheres = (
		"current layer of selected glyphs",
		"all layers of selected glyphs",
		"this master",
		"the complete font",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove TT Hints",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", u"Remove the following hints in", sizeStyle='small', selectable=True)
		self.w.where = vanilla.PopUpButton("auto", self.wheres, sizeStyle='small', callback=self.SavePreferences)

		self.w.hStems = vanilla.CheckBox("auto", u"⬍ H Stem", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vStems = vanilla.CheckBox("auto", u"⬌ V Stem", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hAnchors = vanilla.CheckBox("auto", u"⬍ H Snap (Anchor)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vAnchors = vanilla.CheckBox("auto", u"⬌ V Snap (Anchor)", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hAlign = vanilla.CheckBox("auto", u"⬍ H Shift (Align)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vAlign = vanilla.CheckBox("auto", u"⬌ V Shift (Align)", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hInterpolate = vanilla.CheckBox("auto", u"⬍ H Interpolate", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vInterpolate = vanilla.CheckBox("auto", u"⬌ V Interpolate", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hDiagonal = vanilla.CheckBox("auto", u"⬍ H Diagonal", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vDiagonal = vanilla.CheckBox("auto", u"⬌ V Diagonal", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hDelta = vanilla.CheckBox("auto", u"⬍ H Delta", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.vDelta = vanilla.CheckBox("auto", u"⬌ V Delta", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.hON = vanilla.SquareButton("auto", u"H on", sizeStyle='small', callback=self.update)
		self.w.hOFF = vanilla.SquareButton("auto", u"H off", sizeStyle='small', callback=self.update)

		self.w.vON = vanilla.SquareButton("auto", u"V on", sizeStyle='small', callback=self.update)
		self.w.vOFF = vanilla.SquareButton("auto", u"V off", sizeStyle='small', callback=self.update)

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveTTHintsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.descriptionText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# two columns of checkboxes, one shared width:
		rowNames = ("Stems", "Anchors", "Align", "Interpolate", "Diagonal", "Delta")
		hNames = [f"h{name}" for name in rowNames]
		vNames = [f"v{name}" for name in rowNames]
		columnRules = [
			{"view1": getattr(self.w, name), "attribute1": "width", "view2": self.w.hStems, "attribute2": "width"}
			for name in hNames[1:] + vNames
		]
		rowRules = [
			{"view1": getattr(self.w, vName), "attribute1": "centerY", "view2": getattr(self.w, hName), "attribute2": "centerY"}
			for hName, vName in zip(hNames, vNames)
		]
		rules = ["H:|-inset-[descriptionText]-gap-[where]-inset-|"]
		rules += [f"H:|-inset-[{hName}]-gap-[{vName}]-(>=inset)-|" for hName, vName in zip(hNames, vNames)]
		rules += [
			"H:|-inset-[hON(>=40)]-4-[hOFF(>=40)]-(>=gap)-[vON(>=40)]-4-[vOFF(>=40)]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-(>=inset)-[runButton(>=70)]-inset-|",
			"V:|-gap-[where]-headlineGap-" + "-stackRow-".join(f"[{hName}]" for hName in hNames) + "-headlineGap-[hON]-headlineGap-[progress(16)]-inset-[runButton]-inset-|",
			{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.where, "attribute2": "centerY"},
			{"view1": self.w.hOFF, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			{"view1": self.w.vON, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			{"view1": self.w.vOFF, "attribute1": "centerY", "view2": self.w.hON, "attribute2": "centerY"},
			# the V buttons start in the column of the V checkboxes:
			{"view1": self.w.vON, "attribute1": "left", "view2": self.w.vStems, "attribute2": "left"},
		]
		self.w.addAutoPosSizeRules(
			rules + columnRules + rowRules,
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "stackRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		self.update()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None, savePrefs=True):
		if sender:  # any button
			onOff = 0
			if sender in (self.w.hON, self.w.vON):
				onOff = 1

			if sender in (self.w.hON, self.w.hOFF):
				self.w.hStems.set(onOff)
				self.w.hAnchors.set(onOff)
				self.w.hAlign.set(onOff)
				self.w.hInterpolate.set(onOff)
				self.w.hDiagonal.set(onOff)
				self.w.hDelta.set(onOff)

			if sender in (self.w.vON, self.w.vOFF):
				self.w.vStems.set(onOff)
				self.w.vAnchors.set(onOff)
				self.w.vAlign.set(onOff)
				self.w.vInterpolate.set(onOff)
				self.w.vDiagonal.set(onOff)
				self.w.vDelta.set(onOff)

		self.updateUI()

		if savePrefs:
			self.SavePreferences()

	def updateUI(self, sender=None):
		onOff = (
			self.w.hStems.get() or self.w.hAnchors.get() or self.w.hAlign.get() or self.w.hInterpolate.get() or self.w.hDiagonal.get() or self.w.hDelta.get() or self.w.vStems.get()
			or self.w.vAnchors.get() or self.w.vAlign.get() or self.w.vInterpolate.get() or self.w.vDiagonal.get() or self.w.vDelta.get()
		)
		self.w.runButton.enable(onOff)

	def removeHintsFromLayer(self, layer):
		delCount = 0
		for i in reversed(range(len(layer.hints))):
			h = layer.hints[i]
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				isTrueType = h.isTrueType
			else:
				# GLYPHS 2
				isTrueType = h.isTrueType()

			if isTrueType:
				if h.type == TTSTEM and h.horizontal and self.pref("hStems"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTANCHOR and h.horizontal and self.pref("hAnchors"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTALIGN and h.horizontal and self.pref("hAlign"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTINTERPOLATE and h.horizontal and self.pref("hInterpolate"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDIAGONAL and h.horizontal and self.pref("hDiagonal"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDELTA and h.horizontal and self.pref("hDelta"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTSTEM and not h.horizontal and self.pref("vStems"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTANCHOR and not h.horizontal and self.pref("vAnchors"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTALIGN and not h.horizontal and self.pref("vAlign"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTINTERPOLATE and not h.horizontal and self.pref("vInterpolate"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDIAGONAL and not h.horizontal and self.pref("vDiagonal"):
					del layer.hints[i]
					delCount += 1
				elif h.type == TTDELTA and not h.horizontal and self.pref("vDelta"):
					del layer.hints[i]
					delCount += 1

		if delCount:
			print("- Removed %i instruction%s from %s, layer ‘%s’" % (
				delCount,
				"" if delCount == 1 else "s",
				layer.parent.name,
				layer.name,
			))
		return delCount

	def RemoveTTHintsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Remove TT Hints Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				where = self.pref("where")

				deletedHintsCount = 0
				if where == 0:
					# Current Layer of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, layer in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						deletedHintsCount += self.removeHintsFromLayer(layer)
				elif where == 1:
					# All Layers of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, layer in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						g = layer.parent
						for ll in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(ll)
				elif where == 2:
					# this Master
					masterID = thisFont.selectedFontMaster.id
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, g in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						for layer in g.layers:
							if layer.associatedMasterId == masterID:
								deletedHintsCount += self.removeHintsFromLayer(layer)
				else:
					# the Complete Font
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, g in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						for layer in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(layer)

				# Complete progress bar:
				self.w.progress.set(100)

				# Final report:
				totalCountMsg = "Removed %i instruction%s" % (
					deletedHintsCount,
					"" if deletedHintsCount == 1 else "s",
				)

				Glyphs.showNotification(
					totalCountMsg,
					"Font: %s" % (thisFont.familyName),
				)

				print("%sTOTAL: %s" % (
					"\n" if deletedHintsCount else "",
					totalCountMsg,
				))

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove TT Hints Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemoveTTHints()
