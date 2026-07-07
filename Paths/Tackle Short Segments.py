# MenuTitle: Tackle Short Segments
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds short segments (measuring between the on-curve nodes, ignoring handles) and can remove them, multiply the length of short line segments, or straighten short curve segments.
"""

import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, GSLINE, GSOFFCURVE

REMOVE = 0
MULTIPLY = 1
STRAIGHTEN = 2


class TackleShortSegments(mekkaObject):
	prefDict = {
		"threshold": 1,
		"action": 0,
		"factor": 1,
	}

	def __init__(self):
		windowWidth = 230
		windowHeight = 153
		windowWidthResize = 120
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Tackle Short Segments",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 12, 18

		# threshold line:
		self.w.thresholdText = vanilla.TextBox((inset, linePos + 1, 125, 17), "Short segments up to:", selectable=True, sizeStyle="small")
		self.w.threshold = vanilla.EditText((inset + 125, linePos - 2, -inset, 19), "1", callback=self.SavePreferences, sizeStyle="small")
		self.w.threshold.setToolTip("Segments whose horizontal and vertical extents (measured between the surrounding on-curve nodes) are both at or below this many units count as short.")
		linePos += lineHeight + 8

		# action radio buttons:
		radioHeight = lineHeight * 3
		self.w.action = vanilla.RadioGroup(
			(inset, linePos, -inset, radioHeight),
			[
				"Remove short segments",
				"Multiply line segments by:",
				"Straighten curve segments",
			],
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.action.getNSMatrix().setToolTip_("Choose what to do with short segments. Removal and straightening treat both lines and curves; multiplication only affects line segments.")

		# factor field, aligned with the second radio option:
		self.w.factor = vanilla.EditText((inset + 160, linePos + lineHeight - 2, -inset, 19), "2", callback=self.SavePreferences, sizeStyle="small")
		self.w.factor.setToolTip("Factor by which the length of a short line segment gets multiplied (e.g. 2 doubles it).")
		linePos += radioHeight

		# run button (regular size):
		self.w.runButton = vanilla.Button((-90 - inset, -22 - inset, -inset, 22), "Tackle", callback=self.TackleShortSegmentsMain)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.factor.enable(self.prefInt("action") == MULTIPLY)

	def process(self, thisLayer, threshold, action, factor):
		count = 0
		for thisPath in thisLayer.paths:
			# collect on-curve nodes first, so index shifts from editing do not disturb the loop:
			onCurveNodes = [thisNode for thisNode in thisPath.nodes if thisNode.type != GSOFFCURVE]
			for thisNode in reversed(onCurveNodes):
				prevNode = thisNode.prevNode
				if prevNode is None:
					continue  # open path start node

				if prevNode.type == GSOFFCURVE:
					isCurve = True
					startNode = prevNode.prevNode.prevNode  # the previous on-curve node
				else:
					isCurve = False
					startNode = prevNode

				if startNode is None:
					continue

				xDistance = thisNode.x - startNode.x
				yDistance = thisNode.y - startNode.y
				if abs(xDistance) > threshold or abs(yDistance) > threshold:
					continue  # not a short segment

				if action == REMOVE:
					thisPath.removeNodeCheckKeepShape_(thisNode)
					count += 1
				elif action == MULTIPLY:
					if not isCurve:
						thisNode.x = startNode.x + xDistance * factor
						thisNode.y = startNode.y + yDistance * factor
						count += 1
				elif action == STRAIGHTEN:
					if isCurve:
						secondHandle = prevNode
						firstHandle = prevNode.prevNode
						del thisPath.nodes[secondHandle.index]
						del thisPath.nodes[firstHandle.index]
						thisNode.type = GSLINE
						count += 1
		return count

	def TackleShortSegmentsMain(self, sender):
		self.SavePreferences()
		thisFont = Glyphs.font
		if not thisFont:
			Glyphs.showNotification("Tackle Short Segments", "No font open.")
			return

		threshold = self.prefFloat("threshold")
		action = self.prefInt("action")
		factor = self.prefFloat("factor")
		selectedLayers = thisFont.selectedLayers
		if not selectedLayers:
			Glyphs.showNotification("Tackle Short Segments", "Select at least one glyph.")
			return

		Glyphs.clearLog()
		print("Tackle Short Segments\n")
		verbs = {
			REMOVE: ("Removed", "removed"),
			MULTIPLY: ("Multiplied", "multiplied"),
			STRAIGHTEN: ("Straightened", "straightened"),
		}
		pastTense, verb = verbs[action]

		thisFont.disableUpdateInterface()
		totalCount = 0
		try:
			for thisLayer in selectedLayers:
				thisGlyph = thisLayer.parent
				count = self.process(thisLayer, threshold, action, factor)
				totalCount += count
				if count:
					print("\t✅ %s: %s %i segment%s" % (thisGlyph.name, verb, count, "" if count == 1 else "s"))
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

		Glyphs.showNotification("Tackle Short Segments", "%s %i segment%s. Details in Macro Window." % (pastTense, totalCount, "" if totalCount == 1 else "s"))


TackleShortSegments()
