# MenuTitle: Find Near Vertical Misses
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds nodes that are close but not exactly on vertical metrics (baseline,
xHeight, capHeight, ascender, descender, and alignment zones).
Case-aware: for uppercase glyphs, xHeight is excluded from the checked
metrics; for lowercase glyphs, capHeight is excluded.
"""

import vanilla
from GlyphsApp import Glyphs, GSUppercase, GSLowercase, GSOFFCURVE
from mekkablue import mekkaObject


class FindNearVerticalMisses(mekkaObject):
	prefDict = {
		"threshold": 4,
		"checkBaseline": 1,
		"checkXHeight": 1,
		"checkCapHeight": 1,
		"checkAscender": 1,
		"checkDescender": 1,
		"checkAlignmentZones": 1,
		"includeNonExporting": 0,
		"markNodes": 0,
	}

	def __init__(self):
		windowWidth = 280
		windowHeight = 265
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find Near Vertical Misses",
			autosaveName=self.domain("mainwindow"),
		)

		indent = 15
		y = 10

		self.w.thresholdText = vanilla.TextBox((indent, y + 2, 150, 14), "Report nodes within:", sizeStyle="small")
		self.w.threshold = vanilla.EditText((165, y, 40, 20), "4", sizeStyle="small", callback=self.SavePreferences)
		self.w.thresholdUnit = vanilla.TextBox((210, y + 2, -15, 14), "units", sizeStyle="small")
		y += 30

		self.w.checkBaseline = vanilla.CheckBox((indent, y, -15, 20), "Baseline (0)", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.checkXHeight = vanilla.CheckBox((indent, y, -15, 20), "x-height (skipped for uppercase)", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.checkCapHeight = vanilla.CheckBox((indent, y, -15, 20), "Cap height (skipped for lowercase)", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.checkAscender = vanilla.CheckBox((indent, y, -15, 20), "Ascender", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.checkDescender = vanilla.CheckBox((indent, y, -15, 20), "Descender", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.checkAlignmentZones = vanilla.CheckBox((indent, y, -15, 20), "Alignment zone edges", value=True, sizeStyle="small", callback=self.SavePreferences)
		y += 28

		self.w.includeNonExporting = vanilla.CheckBox((indent, y, -15, 20), "Include non-exporting glyphs", value=False, sizeStyle="small", callback=self.SavePreferences)
		y += 22
		self.w.markNodes = vanilla.CheckBox((indent, y, -15, 20), "Mark affected nodes with ⚠", value=False, sizeStyle="small", callback=self.SavePreferences)

		self.w.runButton = vanilla.Button((-90, -30, -15, -10), "Find", sizeStyle="small", callback=self.FindNearVerticalMissesMain)
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def glyphCase(self, glyph):
		try:
			return glyph.case
		except AttributeError:
			subCat = glyph.subCategory
			if subCat == "Uppercase":
				return GSUppercase
			if subCat == "Lowercase":
				return GSLowercase
			return None

	def metricsForMasterAndGlyph(self, master, glyph):
		case = self.glyphCase(glyph)
		metrics = set()

		if self.pref("checkBaseline"):
			metrics.add(0)
		if self.pref("checkXHeight") and case != GSUppercase:
			metrics.add(master.xHeight)
		if self.pref("checkCapHeight") and case != GSLowercase:
			metrics.add(master.capHeight)
		if self.pref("checkAscender"):
			metrics.add(master.ascender)
		if self.pref("checkDescender"):
			metrics.add(master.descender)
		if self.pref("checkAlignmentZones"):
			for zone in master.alignmentZones:
				metrics.add(zone.position)
				metrics.add(zone.position + zone.size)

		return metrics

	def FindNearVerticalMissesMain(self, sender=None):
		font = Glyphs.font
		if not font:
			return

		self.SavePreferences()
		Glyphs.clearLog()

		threshold = int(self.pref("threshold"))
		includeNonExporting = bool(self.pref("includeNonExporting"))
		markNodes = bool(self.pref("markNodes"))

		affectedLayers = []

		font.disableUpdateInterface()
		try:
			for glyph in font.glyphs:
				if not includeNonExporting and not glyph.export:
					continue

				for layer in glyph.layers:
					if not layer.isMasterLayer:
						continue

					metrics = self.metricsForMasterAndGlyph(layer.master, glyph)
					if not metrics:
						continue

					layerHasMiss = False
					for path in layer.paths:
						for node in path.nodes:
							if node.type == GSOFFCURVE:
								continue
							y = node.position.y
							if not any(abs(y - m) <= threshold and y != m for m in metrics):
								continue
							layerHasMiss = True
							nearestMetric = min(metrics, key=lambda m: abs(y - m))
							print(f"  ⚠ {glyph.name} | {layer.name}: y={y:.0f} (near {nearestMetric:.0f}, off by {y - nearestMetric:.0f})")
							if markNodes:
								node.name = "⚠"

					if not layerHasMiss:
						continue
					if layer not in affectedLayers:
						affectedLayers.append(layer)

		finally:
			font.enableUpdateInterface()

		if not affectedLayers:
			print("✅ No near vertical misses found.")
			return

		seen = set()
		glyphNames = []
		for layer in affectedLayers:
			name = layer.parent.name
			if name in seen:
				continue
			seen.add(name)
			glyphNames.append(name)

		font.newTab("/" + "/".join(glyphNames))
		print(f"\nFound near vertical misses in {len(affectedLayers)} layer(s) across {len(glyphNames)} glyph(s).")


FindNearVerticalMisses()
