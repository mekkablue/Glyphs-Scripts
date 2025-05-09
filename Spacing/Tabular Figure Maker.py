# MenuTitle: Tabular Figure Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Takes existing .tf figures and spaces them tabularly, or creates them from existing default figures.
"""

import vanilla
from GlyphsApp import Glyphs, GSGlyph, GSComponent, Message
from mekkablue import mekkaObject, UpdateButton


class TabularFigureSpacer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"target": "one.tf",
		"suffix": ".tf",
		"createFromDefaultFigs": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 138
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Tabular Figure Spacer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Fit default figures in tabular spaces", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.targetText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Reference glyph", sizeStyle="small", selectable=True)
		self.w.target = vanilla.ComboBox((inset + 93, linePos - 1, -inset - 22, 19), [], sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Tabular suffix", sizeStyle="small", selectable=True)
		self.w.suffix = vanilla.EditText((inset + 93, linePos, -inset, 19), ".tf", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.createFromDefaultFigs = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Create glyphs if they are missing", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.createFromDefaultFigs.getNSButton().setToolTip_("Creates glyphs for tab figures with default figures as components. Otherwise will just reset existing tab figures.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Tab", callback=self.TabularFigureSpacerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.update()
		self.w.open()
		self.w.makeKey()


	def update(self, sender=None):
		self.w.target.setItems([g.name for g in Glyphs.font.glyphs if ".tf" in g.name or ".tosf" in g.name])


	def TabularFigureSpacerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			font = Glyphs.font  # frontmost font
			if font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				filePath = font.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{font}\n⚠️ The font file has not been saved yet."
				print(f"Tabular Figure Spacer Report for {reportName}")
				print()

				if self.pref("createFromDefaultFigs"):
					figs = "0123456789"
					for fig in figs:
						niceName = Glyphs.niceGlyphName(fig)
						figName = f"{niceName}.{self.pref('suffix').lstrip('.')}"
						if not font.glyphs[figName]:
							newGlyph = GSGlyph(figName)
							font.glyphs.append(newGlyph)
							for layer in newGlyph.layers:
								layer.shapes.append(GSComponent(niceName))

				targetGlyph = font.glyphs[self.pref("target")]
				tabFigs = [g for g in font.glyphs if g.name.endswith(self.pref("suffix"))]
				if targetGlyph:
					for thisGlyph in tabFigs:
						for master in font.masters:
							mID = master.id
							targetLayer = targetGlyph.layers[mID]
							layer = thisGlyph.layers[mID]
							for thisComponent in layer.components:
								thisComponent.alignment = -1 # can be freely positioned

							if targetGlyph == thisGlyph:
								continue

							widthDiff = targetLayer.width - layer.width
							leftPercentage = layer.LSB / (layer.LSB + layer.RSB)
							layer.LSB += round(widthDiff * leftPercentage)
							layer.width = targetLayer.width
						thisGlyph.widthMetricsKey = f"={self.pref('target')}"

				names = [g.name for g in tabFigs]
				font.newTab("/" + "/".join(names))

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Tabular Figure Spacer Error: {e}")
			import traceback
			print(traceback.format_exc())


TabularFigureSpacer()
