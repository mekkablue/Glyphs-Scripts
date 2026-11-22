# MenuTitle: Find and Replace in Metrics Keys
__doc__ = """
Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys.
"""

import traceback

import vanilla
from mekkablue import mekkaObject, makeWindowResizable
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)


class MetricKeyReplacer(mekkaObject):
	prefDict = {
		"leftSearchFor": "=a",
		"leftReplaceBy": "=a.ss01",
		"rightSearchFor": "=|a",
		"rightReplaceBy": "=|a.ss01",
	}

	def __init__(self):
		windowWidth = 335
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace in Metrics Keys",
			autosaveName=self.domain("mainwindow"),  # stores last window position and width
		)

		inset = 15
		self.w.text_Find = vanilla.TextBox("auto", "Find", sizeStyle='small')
		self.w.text_Replace = vanilla.TextBox("auto", "Replace", sizeStyle='small')

		self.w.text_left = vanilla.TextBox("auto", "Left Key", sizeStyle='small')
		self.w.leftSearchFor = vanilla.EditText("auto", "=a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.leftReplaceBy = vanilla.EditText("auto", "=a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')

		self.w.text_right = vanilla.TextBox("auto", "Right Key", sizeStyle='small')
		self.w.rightSearchFor = vanilla.EditText("auto", "=|a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.rightReplaceBy = vanilla.EditText("auto", "=|a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')

		self.w.runButton = vanilla.Button("auto", "Replace", callback=self.MetricKeyReplaceMain)
		self.w.setDefaultButton(self.w.runButton)

		# with everything hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the row labels are right-aligned and share one width, so the fields line up:
		for label in (self.w.text_Find, self.w.text_Replace):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_Find]-gap-[leftSearchFor(>=100)]-gap-[rightSearchFor]-inset-|",
				"H:|-inset-[text_Replace]-gap-[leftReplaceBy]-gap-[rightReplaceBy]-inset-|",
				"H:[text_right]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=95)]-inset-|",
				"V:|-gap-[text_left]-headGap-[leftSearchFor]-row-[leftReplaceBy]-inset-[runButton]-inset-|",
				# both labels and all four fields share their widths:
				{"view1": self.w.text_Find, "attribute1": "width", "view2": self.w.text_Replace, "attribute2": "width"},
				{"view1": self.w.rightSearchFor, "attribute1": "width", "view2": self.w.leftSearchFor, "attribute2": "width"},
				{"view1": self.w.leftReplaceBy, "attribute1": "width", "view2": self.w.leftSearchFor, "attribute2": "width"},
				{"view1": self.w.rightReplaceBy, "attribute1": "width", "view2": self.w.leftSearchFor, "attribute2": "width"},
				# the headlines sit on top of their columns:
				{"view1": self.w.text_left, "attribute1": "left", "view2": self.w.leftSearchFor, "attribute2": "left"},
				{"view1": self.w.text_right, "attribute1": "left", "view2": self.w.rightSearchFor, "attribute2": "left"},
				{"view1": self.w.text_right, "attribute1": "centerY", "view2": self.w.text_left, "attribute2": "centerY"},
				# one baseline per row:
				{"view1": self.w.text_Find, "attribute1": "centerY", "view2": self.w.leftSearchFor, "attribute2": "centerY"},
				{"view1": self.w.rightSearchFor, "attribute1": "centerY", "view2": self.w.leftSearchFor, "attribute2": "centerY"},
				{"view1": self.w.text_Replace, "attribute1": "centerY", "view2": self.w.leftReplaceBy, "attribute2": "centerY"},
				{"view1": self.w.rightReplaceBy, "attribute1": "centerY", "view2": self.w.leftReplaceBy, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headGap": 4},
		)

		try:
			self.LoadPreferences()
		except:
			print("Warning: Could not load preferences.\n%s" % traceback.format_exc())

		makeWindowResizable(self.w)  # resizable horizontally only

		self.w.open()
		self.w.makeKey()

	def MetricKeyReplaceMain(self, sender):
		Font = Glyphs.font
		if Font is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		Font.disableUpdateInterface()
		try:
			self.SavePreferences()

			selectedLayers = Font.selectedLayers
			currentLayers = [layer for layer in selectedLayers if layer.parent.name is not None]

			LsearchFor = self.w.leftSearchFor.get()
			LreplaceBy = self.w.leftReplaceBy.get()
			RsearchFor = self.w.rightSearchFor.get()
			RreplaceBy = self.w.rightReplaceBy.get()

			for layer in currentLayers:
				try:
					g = layer.parent
					# g.beginUndo()  # undo grouping causes crashes

					# Left Metrics Key:
					try:
						for glyphOrLayer in (g, layer):
							leftKey = glyphOrLayer.leftMetricsKey
							if leftKey:
								if LsearchFor == "":
									glyphOrLayer.leftMetricsKey = leftKey + LreplaceBy
								else:
									glyphOrLayer.leftMetricsKey = leftKey.replace(LsearchFor, LreplaceBy)

								print("%s: new left metrics key: '%s'" % (g.name, glyphOrLayer.leftMetricsKey))

					except Exception as e:
						print("\nError while trying to set left key for: %s" % g.name)
						print(e)
						print(traceback.format_exc())

					# Right Metrics Key:
					try:
						for glyphOrLayer in (g, layer):
							rightKey = glyphOrLayer.rightMetricsKey
							if rightKey:
								if RsearchFor == "":
									glyphOrLayer.rightMetricsKey = rightKey + RreplaceBy
								else:
									glyphOrLayer.rightMetricsKey = rightKey.replace(RsearchFor, RreplaceBy)

								print("%s: new right metrics key: '%s'" % (g.name, glyphOrLayer.rightMetricsKey))

					except Exception as e:
						print("\nError while trying to set right key for: %s" % g.name)
						print(e)
						print(traceback.format_exc())

					# g.endUndo()  # undo grouping causes crashes

				except Exception as e:
					print("\nError while processing glyph %s" % g.name)
					print(e)
					print(traceback.format_exc())

					# g.endUndo()  # undo grouping causes crashes

			self.w.close()

		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			print(traceback.format_exc())
			print()
			raise e

		finally:
			Font.enableUpdateInterface()


Glyphs.clearLog()
MetricKeyReplacer()
