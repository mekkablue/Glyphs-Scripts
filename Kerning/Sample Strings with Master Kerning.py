# MenuTitle: Sample Strings with Master Kerning
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates kern strings for the current kerning and adds them to the Sample Strings.
"""

import vanilla
import sampleText
from GlyphsApp import Glyphs, GSUppercase, GSSmallcaps, Message
from mekkablue import mekkaObject


class SampleStringsWithMasterKerning(mekkaObject):
	prefDict = {
		"groupToGroupOnly": 0,
		"positivePairs": 1,
		"negativePairs": 1,
		"zeroPairs": 1,
		"applyKernValueThreshold": 0,
		"minimumKerning": 100,
		"openTab": 1,
		"lockKerning": 1,
		"overrideContext": 0,
		"contextGlyphs": "HOOH,noon",
		"mirrorPair": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 225
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Sample Strings with Master Kerning",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Builds kern strings with current kerning in Sample Texts.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		tab = 70
		self.w.positivePairs = vanilla.CheckBox((inset + 2, linePos - 1, tab, 20), "Positive", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.negativePairs = vanilla.CheckBox((inset + tab, linePos - 1, tab, 20), "Negative", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.zeroPairs = vanilla.CheckBox((inset + tab * 2, linePos - 1, -inset, 20), "Zero pairs", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.groupToGroupOnly = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Group-to-group kerning only", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.applyKernValueThreshold = vanilla.CheckBox((inset + 2, linePos - 1, 150, 20), "Only kernings of at least:", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.minimumKerning = vanilla.EditText((inset + 150, linePos, -inset, 19), "100", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.overrideContext = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Override context glyphs:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.overrideContext.getNSButton().setToolTip_("If checked, the surrounding glyphs will be replaced with those given in the text box. Use a comma to differentiate the left-side context from the right-side context: ‘HOOH,noon’ will put HOOH on the left side, ‘noon’ on the right side.")
		self.w.contextGlyphs = vanilla.EditText((inset + 150, linePos, -inset, 19), "HOOH,noon", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.mirrorPair = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Mirror kerning pair (AV→AVA)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.mirrorPair.getNSButton().setToolTip_("If checked, will create a mirrored version of the kerning string. E.g., instead of just AV, it will show AVA between the context glyphs.")
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset + 2, linePos - 1, 170, 20), "Open tab at first kern string", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("If checked, a new tab will be opened with the first found kern string, and the cursor positioned accordingly, ready for group kerning and switching to the next sample string.")
		self.w.lockKerning = vanilla.CheckBox((inset + 170, linePos - 1, -inset, 20), "in kerning mode", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lockKerning.getNSButton().setToolTip_("Will set the kerning lock in the tab, prevents you from spacing accidentally.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Add", callback=self.SampleStringsWithCurrentKerning)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(self.w.positivePairs.get() or self.w.negativePairs.get() or self.w.zeroPairs.get())

	def parseTheContextGlyphs(self):
		separator = ","
		txt = self.pref("contextGlyphs")
		if separator in txt:
			linePrefix, linePostfix = txt.split(separator)[:2]
		else:
			linePrefix, linePostfix = txt, txt
		return linePrefix, linePostfix

	def namesForGroupName(self, groupName, font, isLeft=True):
		names = []
		for g in font.glyphs:
			if isLeft:  # left side = right group
				if g.rightKerningGroup in (groupName, groupName[7:]):
					names.append(g.name)
			else:
				if g.leftKerningGroup in (groupName, groupName[7:]):
					names.append(g.name)
		return names

	def glyphNameForKerningName(self, name, font, isLeft=True):
		glyphName = None
		if name[0] == "@":
			names = self.namesForGroupName(name, font, isLeft=isLeft)
			if name.startswith("@MMK_"):
				glyphName = name.split("_")[2]
				if glyphName == "KO":  # KernOn convention
					glyphName = name.split("_")[3]
				if not font.glyphs[glyphName] or glyphName not in names:
					glyphName = None
			if not glyphName:
				for name in names:
					if font.glyphs[name]:
						glyphName = name
						break
		else:
			glyph = font.glyphForId_(name)
			if glyph:
				glyphName = glyph.name

		if glyphName:
			return glyphName
		else:
			print("⚠️ No glyph found for: {name}")
			return None

	def contextForGlyphs(self, leftName, rightName, font):
		linePrefix = "nonn"
		linePostfix = "noon"

		L = font.glyphs[leftName]
		R = font.glyphs[rightName]

		numberTriggers = ("Math", "Currency", "Decimal Digit")
		if L and L.subCategory in numberTriggers:
			linePrefix = "1200"
		if R and R.subCategory in numberTriggers:
			linePostfix = "0034567"
		if L and L.case == GSUppercase:
			linePrefix = "HOOH"
		elif L and L.case == GSSmallcaps:
			linePrefix = "/h.sc/o.sc/h.sc/h.sc"
		if R and R.case == GSSmallcaps:
			linePostfix = "/h.sc/o.sc/o.sc/h.sc"

		return linePrefix, linePostfix

	def SampleStringsWithCurrentKerning(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			thisMaster = thisFont.selectedFontMaster
			print(f"Sample Strings with Master Kerning Report for {thisFont.familyName}")
			if thisFont.filepath:
				print(thisFont.filepath)
			print(f"Ⓜ️ Master: ‘{thisMaster.name}’")
			print()

			leftContext, rightContext = "nonn", "noon"
			if self.pref("contextGlyphs"):
				leftContext, rightContext = self.parseTheContextGlyphs()

			cursorPos = len(leftContext) + 1
			minimumKerning = self.prefInt("minimumKerning")

			kernStrings = []
			for leftSide in thisFont.kerning[thisMaster.id].keys():
				leftGlyph = self.glyphNameForKerningName(leftSide, thisFont, isLeft=True)
				if not leftGlyph:
					continue
				for rightSide in thisFont.kerning[thisMaster.id][leftSide].keys():
					value = thisFont.kerning[thisMaster.id][leftSide][rightSide]
					if self.pref("applyKernValueThreshold") and minimumKerning > abs(value):
						continue
					if (self.pref("positivePairs") and value > 0) or (self.pref("negativePairs") and value < 0) or (self.pref("zeroPairs") and value == 0):
						rightGlyph = self.glyphNameForKerningName(rightSide, thisFont, isLeft=False)
						if not rightGlyph:
							continue
						if not self.pref("overrideContext"):
							leftContext, rightContext = self.contextForGlyphs(leftGlyph, rightGlyph, thisFont)
						line = f"{leftContext}/{leftGlyph}/{rightGlyph}"
						if self.pref("mirrorPair"):
							line += f"/{leftGlyph}"
						line += f" {rightContext}"
						kernStrings.append(line)

			if not kernStrings:
				Message(title="No Kern Strings Created", message="No kerning in the font that meets your selection.", OKButton=None)
				print("No kern strings built. Done.")
			else:
				marker = "Master Kerning"
				sampleText.executeAndReport(kernStrings, marker=marker)

				if self.pref("openTab"):
					newTab = thisFont.newTab()
					if Glyphs.versionNumber >= 3:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab, marker=marker)
					else:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab)
					if len(newTab.text) >= cursorPos:
						newTab.textCursor = cursorPos

					# set it to lock kerning:
					if self.pref("lockKerning"):
						newTab.graphicView().setDoSpacing_(0)
						newTab.graphicView().setDoKerning_(1)
						newTab.updateKerningButton()

				self.w.close()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Sample Strings with Master Kerning Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Glyphs.clearLog()
SampleStringsWithMasterKerning()
