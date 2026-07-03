# MenuTitle: Tackle Short Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds very short (single-unit) straight segments and either removes them or enlarges them.
"""

import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSOFFCURVE


class TackleShortSegments(mekkaObject):
	prefDict = {
		"action": 0,  # 0 = remove, 1 = enlarge
		"threshold": 1.0,
	}

	def __init__(self):
		windowWidth = 260
		windowHeight = 120
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Tackle Short Segments",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth, windowHeight),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		self.w.text = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Short straight segments up to:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.thresholdText = vanilla.TextBox((inset, linePos + 2, 100, 14), "Max distance:", sizeStyle="small", selectable=True)
		self.w.threshold = vanilla.EditText((inset + 90, linePos, -inset, 19), "1.0", callback=self.SavePreferences, sizeStyle="small")
		self.w.threshold.setToolTip("Segments whose horizontal and vertical extents are both at or below this many units count as short.")
		linePos += lineHeight

		self.w.action = vanilla.RadioGroup((inset, linePos, -inset, 40), ["Remove short segments", "Enlarge short segments (double their length)"], callback=self.SavePreferences, sizeStyle="small")
		self.w.action.getNSMatrix().setToolTip_("Choose whether to delete the short segments or to double their length.")
		linePos += lineHeight * 2

		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Tackle", callback=self.TackleShortSegmentsMain, sizeStyle="small")
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def process(self, thisLayer, threshold, enlarge):
		count = 0
		for thisPath in thisLayer.paths:
			for i in range(len(thisPath.nodes))[::-1]:
				thisNode = thisPath.nodes[i]
				prevNode = thisNode.prevNode
				if prevNode.type != GSOFFCURVE and thisNode.type != GSOFFCURVE:
					xDistance = thisNode.x - prevNode.x
					yDistance = thisNode.y - prevNode.y
					if abs(xDistance) <= threshold and abs(yDistance) <= threshold:
						if enlarge:
							thisNode.x = prevNode.x + xDistance * 2
							thisNode.y = prevNode.y + yDistance * 2
						else:
							thisPath.removeNodeCheckKeepShape_(thisNode)
						count += 1
		return count

	def TackleShortSegmentsMain(self, sender):
		self.SavePreferences()
		thisFont = Glyphs.font
		if not thisFont:
			Glyphs.showNotification("Tackle Short Segments", "No font open.")
			return

		threshold = self.prefFloat("threshold")
		enlarge = self.prefInt("action") == 1
		selectedLayers = thisFont.selectedLayers

		Glyphs.clearLog()
		print("Tackle Short Segments\n")
		verb = "Enlarged" if enlarge else "Removed"

		thisFont.disableUpdateInterface()
		totalCount = 0
		try:
			for thisLayer in selectedLayers:
				thisGlyph = thisLayer.parent
				count = self.process(thisLayer, threshold, enlarge)
				totalCount += count
				if count:
					print("\t✅ %s: %s %i segment%s" % (thisGlyph.name, verb.lower(), count, "" if count == 1 else "s"))
				else:
					print("\t☑️ %s: no short segments" % thisGlyph.name)
		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e
		finally:
			thisFont.enableUpdateInterface()

		Glyphs.showNotification("Tackle Short Segments", "%s %i segment%s. Details in Macro Window." % (verb, totalCount, "" if totalCount == 1 else "s"))


TackleShortSegments()
