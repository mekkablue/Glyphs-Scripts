# MenuTitle: Rename Glyphs
__doc__ = """
Takes a list of oldglyphname=newglyphname pairs and renames glyphs in the font accordingly, much like the Rename Glyphs parameter.
"""

import uuid
import vanilla
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs
from AppKit import NSFont, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut


class RenameGlyphs(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"renameList": "oldname=newname",
		"allFonts": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 200
		# the window stays resizable, because the user needs to enlarge the text editor
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Rename Glyphs",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15
		self.w.text_1 = vanilla.TextBox("auto", "Add lines like oldname=newname:", sizeStyle='small')
		self.w.renameList = vanilla.TextEditor("auto", "oldname=newname", callback=self.SavePreferences)
		self.w.renameList.getNSTextView().setFont_(NSFont.userFixedPitchFontOfSize_(-1.0))
		self.w.renameList.getNSTextView().turnOffLigatures_(1)
		self.w.renameList.getNSTextView().useStandardLigatures_(0)
		self.w.renameList.selectAll()

		self.w.allFonts = vanilla.CheckBox("auto", "⚠️ ALL Fonts", value=False, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Rename", callback=self.RenameGlyphsMain)
		# self.w.setDefaultButton(self.w.runButton)

		# everything hugs vertically, except for the text editor, which takes the leftover height:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.renameList.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-inset-|",
				"H:|-0-[renameList]-0-|",
				"H:|-inset-[allFonts]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[text_1]-gap-[renameList(>=80)]-gap-[runButton]-inset-|",
				{"view1": self.w.allFonts, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		makeWindowResizable(self.w, vertical=True)  # resizable, limits in content sizes

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def RenameGlyphsMain(self, sender):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			if self.pref("allFonts"):
				theseFonts = Glyphs.fonts
			else:
				theseFonts = [Glyphs.font, ] if Glyphs.font else []

			if not theseFonts:
				print("⚠️ Rename Glyphs: no font open.")
				return

			for thisFont in theseFonts:
				for thisLine in self.pref("renameList").splitlines():
					if thisLine.strip():
						if "=" not in thisLine:
							print(f"⚠️ Skipping line without equals sign: {thisLine.strip()}")
							continue
						glyphNameLeft = thisLine.split("=")[0].strip()
						glyphNameRight = thisLine.split("=")[1].strip()
						glyphLeft = thisFont.glyphs[glyphNameLeft]
						glyphRight = thisFont.glyphs[glyphNameRight]
						if glyphLeft:
							if glyphRight:
								uniqueSuffix = ".%s" % uuid.uuid4().hex
								glyphLeft.name = glyphNameRight + uniqueSuffix
								glyphRight.name = glyphNameLeft
								glyphLeft.name = glyphNameRight

								# swap export status:
								glyphLeftExport = glyphLeft.export
								glyphLeft.export = glyphRight.export
								glyphRight.export = glyphLeftExport
							else:
								glyphLeft.name = glyphNameRight
						else:
							print(f"Warning: {glyphNameLeft} not in font.")

			self.SavePreferences()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Rename Glyphs Error: {e}")
			import traceback
			print(traceback.format_exc())


RenameGlyphs()
