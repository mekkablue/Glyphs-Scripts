# MenuTitle: Snap Anchors to Nearest Metric
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Moves specified anchors to the nearest metric (e.g. x-height, ascender, etc.), within a specified threshold.
"""

import vanilla
from Foundation import NSPoint
from AppKit import NSAffineTransform
from GlyphsApp import Glyphs, Message, addPoints
from mekkaCore import mekkaObject, italicize


def closestMetric(position, metrics):
	return sorted(metrics, key=lambda metric: abs(metric - position))[0]


def legibleNum(number):
	try:
		return f"{float(number):0.1f}".rstrip("0").rstrip(".")
	except:
		return number


class SnapAnchorsToNearestMetric(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"anchorNames": "_top, _bottom, top, bottom, ogonek, _ogonek",
		"threshold": 30,
		"respectItalic": True,
		"focusOnMarkAnchorsInMarks": True,
		"allFonts": False,
		"verbose": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 220
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Snap Anchors to Nearest Metric",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Move these anchors to the nearest vertical metric line:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.anchorNames = vanilla.EditText((inset, linePos, -inset, 19), "_top, _bottom, top, bottom, ogonek, _ogonek", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.anchorNamesDescription = vanilla.TextBox((inset, linePos + 2, -inset, 14), "For mark anchors (like _top), will shift complete glyph.", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.thresholdText = vanilla.TextBox((inset, linePos + 3, 110, 14), "Max vertical move:", sizeStyle="small", selectable=True)
		self.w.threshold = vanilla.EditText((inset + 110, linePos, 50, 19), "30", callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.respectItalic = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Respect italic angle (otherwise always vertical)", value=True, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		self.w.focusOnMarkAnchorsInMarks = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "In marks, ignore non-underscore anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.focusOnMarkAnchorsInMarks.getNSButton().setToolTip_("Will look only for _xxx anchors in marks (i.e., with an underscore), and ignore those not starting with an underscore.")
		linePos += lineHeight

		self.w.allFonts = vanilla.CheckBox((inset, linePos - 1, 150, 20), "Apply to ⚠️ ALL fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.verbose = vanilla.CheckBox((inset + 150, linePos - 1, -inset, 20), "Verbose reporting", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Snap", sizeStyle="regular", callback=self.SnapAnchorsToNearestMetricMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Snap Anchors to Nearest Metric’ could not load preferences. Will resort to defaults.")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def moveAnchorsToNearestMetricsOnLayer(
		self, layer, anchorNames=["_top", "_bottom", "top", "bottom", "ogonek", "_ogonek"], respectItalic=True, threshold=30, verbose=False, underscoreOnlyInMarks=True
	):
		didMove = False
		reports = []
		isMark = layer.parent.category == "Mark"
		beyondThreshold = False

		if not layer.anchors:
			if verbose:
				reports.append(f"   🤷🏻‍♀️ no anchors on layer {layer.name}")
			return didMove, reports, beyondThreshold

		if not any([layer.anchors[an] for an in anchorNames]):
			if verbose:
				reports.append(f"   🤷🏻‍♀️ no matching anchors on layer {layer.name}, only: {', '.join([a.name for a in layer.anchors])}")
			return didMove, reports, beyondThreshold

		respectItalic = respectItalic and layer.italicAngle != 0
		positions = tuple(m.position for m in layer.metrics)
		for anchorName in anchorNames:
			anchor = layer.anchors[anchorName]
			if anchor:
				currentHeight = anchor.position.y
				targetHeight = closestMetric(currentHeight, positions)
				verticalMovement = targetHeight - currentHeight
				if verticalMovement == 0:
					continue
				if abs(verticalMovement) > threshold:
					reports.append(f"   ⚠️ layer {layer.name}, anchor {anchorName}: move {legibleNum(verticalMovement)} beyond threshold {threshold}")
					beyondThreshold = True
					continue
				move = NSPoint(0, verticalMovement)
				if respectItalic:
					move = italicize(move, italicAngle=layer.italicAngle)
				if anchorName.startswith("_"):
					moveTransform = NSAffineTransform.transform()
					moveTransform.translateXBy_yBy_(move.x, move.y)
					# moveMatrix = moveTransform.transformStruct()
					layer.applyTransform(moveTransform)
					if verbose:
						reports.append(f"   ↕️ shifted layer {layer.name} {legibleNum(move.x)} {legibleNum(move.y)}")
				elif not isMark or not underscoreOnlyInMarks:
					anchor.position = addPoints(anchor.position, move)
					if verbose:
						reports.append(f"   ⚓️ moved {layer.name} {anchorName} {legibleNum(move.x)} {legibleNum(move.y)}")
				didMove = True

		return didMove, reports, beyondThreshold

	def SnapAnchorsToNearestMetricMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Snap Anchors to Nearest Metric’ could not write preferences.")

			if Glyphs.font is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			allFonts = self.prefBool("allFonts")
			if allFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )

			# read prefs:
			threshold = self.prefInt("threshold")
			respectItalic = self.prefBool("respectItalic")
			verbose = self.prefBool("verbose")
			anchorNamesList = sorted(set([a.strip() for a in self.pref("anchorNames").strip().split(",")]))
			focusOnMarkAnchorsInMarks = self.prefBool("focusOnMarkAnchorsInMarks")

			for thisFont in theseFonts:
				filePath = thisFont.filepath
				if filePath:
					reportName = f"{filePath.lastPathComponent()}\n📄 {filePath}"
				else:
					reportName = f"{thisFont.familyName}\n⚠️ The font file has not been saved yet."
				print(f"Snap Anchors to Nearest Metric Report for {reportName}")
				print()

				thisFont = Glyphs.font
				if thisFont.filepath:
					fontName = thisFont.filepath.lastPathComponent().stringByDeletingLastDotSuffix()
				else:
					fontName = thisFont.familyName
				print(f"Moving Anchors in {fontName}:\n")
				tabText = ""
				glyphsBeyondThreshold = []
				for g in thisFont.glyphs:
					movedAnchorsInGlyph = False
					glyphReports = []
					beyondThreshold = False
					for layer in g.layers:
						if layer.isMasterLayer or layer.isSpecialLayer:
							movedAnchorsOnLayer, layerReports, layerBeyondThreshold = self.moveAnchorsToNearestMetricsOnLayer(
								layer,
								anchorNames=anchorNamesList,
								respectItalic=respectItalic,
								threshold=threshold,
								underscoreOnlyInMarks=focusOnMarkAnchorsInMarks,
								verbose=verbose,
							)
							movedAnchorsInGlyph = movedAnchorsInGlyph or movedAnchorsOnLayer
							glyphReports.extend(layerReports)
							beyondThreshold = beyondThreshold or layerBeyondThreshold

					if glyphReports:
						reports = '\n'.join(glyphReports)
						print(f"🔤 {g.name}:\n{reports}")

					if movedAnchorsInGlyph:
						tabText += f"/{g.name}"

					if beyondThreshold:
						glyphsBeyondThreshold.append(g.name)

				if tabText:
					if glyphsBeyondThreshold:
						tabText += f"\n\nBeyond threshold:\n/{'/'.join(glyphsBeyondThreshold)}"
					thisFont.newTab(f"Snapped anchors:\n{tabText}")

			print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Snap Anchors to Nearest Metric Error: {e}")
			import traceback
			print(traceback.format_exc())


SnapAnchorsToNearestMetric()
