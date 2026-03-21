# MenuTitle: Remove Images
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes placed images from glyphs. Options: scope (all glyphs in font or selected glyphs only), remove images with existing files, remove orphaned images (source file no longer on disk), and optional glyph-name filter with wildcard support.
"""

import os
import vanilla
from mekkablue import mekkaObject, match
from GlyphsApp import Glyphs


class RemoveImages(mekkaObject):
	prefDict = {
		"scope": 0,
		"removeLinked": 1,
		"removeOrphaned": 1,
		"filterByName": 0,
		"nameFilter": "",
	}

	def __init__(self):
		windowWidth = 500
		windowHeight = 155
		windowWidthResize = 200
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Remove Images",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow"),
		)

		linePos, inset, lineHeight = 12, 15, 22

		# Scope
		self.w.scopeLabel = vanilla.TextBox((inset, linePos + 2, 140, 14), "Remove images from:", sizeStyle="small")
		self.w.scope = vanilla.PopUpButton(
			(inset + 140, linePos, 210, 18),
			["all glyphs in font", "selected glyphs only"],
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		scopeTooltip = "Choose whether to process all glyphs in the font, or only the glyphs currently selected in Font View."
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)
		linePos += lineHeight

		# Remove linked images
		self.w.removeLinked = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Remove images whose source file still exists on disk",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.removeLinked.setToolTip("Remove placed images where the source image file is still present on disk. Uncheck to skip these and only remove orphaned references.")
		linePos += lineHeight

		# Remove orphaned images
		self.w.removeOrphaned = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Remove orphaned images (source file no longer on disk)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.removeOrphaned.setToolTip("Remove placed images where the source file can no longer be found on disk. These are broken references that cannot be displayed correctly.")
		linePos += lineHeight

		# Filter by glyph name
		self.w.filterByName = vanilla.CheckBox(
			(inset, linePos, 220, 20),
			"Only in glyphs whose name contains:",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.filterByName.setToolTip("If enabled, restricts removal to glyphs whose names match one of the comma-separated particles. Wildcards * and ? are supported.")
		self.w.nameFilter = vanilla.EditText(
			(inset + 222, linePos, -inset, 19),
			"",
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.nameFilter.setToolTip("Comma-separated glyph name particles. Each particle is matched as a substring unless it contains wildcards. Wildcards * (any string) and ? (any single character) are supported. Example: 'A, *comb, ?.sc'")
		linePos += lineHeight

		self.w.divider = vanilla.HorizontalLine((inset, linePos + 4, -inset, 1))

		# Status line and Run button
		self.w.status = vanilla.TextBox((inset, -28 - inset, -80 - inset - 10, 14), "", sizeStyle="small")
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Remove", callback=self.run, sizeStyle="small")
		self.w.setDefaultButton(self.w.runButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.nameFilter.enable(self.prefBool("filterByName"))

	def run(self, sender):
		font = Glyphs.font
		if not font:
			self.w.status.set("⚠️ No font open.")
			return

		removeLinked = self.prefBool("removeLinked")
		removeOrphaned = self.prefBool("removeOrphaned")
		filterByName = self.prefBool("filterByName")
		nameFilter = self.pref("nameFilter") or ""
		scope = self.prefInt("scope")

		if not removeLinked and not removeOrphaned:
			self.w.status.set("⚠️ Nothing selected to remove.")
			return

		# Determine glyph scope
		if scope == 1:
			glyphs = []
			seen = set()
			for layer in font.selectedLayers:
				glyph = layer.parent
				if glyph.name not in seen:
					seen.add(glyph.name)
					glyphs.append(glyph)
		else:
			glyphs = list(font.glyphs)

		# Apply name filter
		if filterByName and nameFilter.strip():
			particles = [p.strip() for p in nameFilter.split(",") if p.strip()]
			if particles:
				glyphs = [g for g in glyphs if any(match("*" + p + "*", g.name) for p in particles)]

		# Report header
		Glyphs.clearLog()
		print("Remove Images\n")
		scopeLabel = "selected glyphs" if scope == 1 else "all glyphs in font"
		print(f"Scope: {scopeLabel}")
		if filterByName and nameFilter.strip():
			print(f"Name filter: {nameFilter.strip()}")
		removing = []
		if removeLinked:
			removing.append("linked")
		if removeOrphaned:
			removing.append("orphaned")
		print(f"Removing: {' + '.join(removing)} images\n")

		totalRemoved = 0
		totalOrphaned = 0

		font.disableUpdateInterface()
		try:
			for glyph in glyphs:
				removedInGlyph = 0
				orphanedInGlyph = 0
				for layer in glyph.layers:
					try:
						# Foreground background image
						img = layer.backgroundImage
						if img is not None:
							imgPath = None
							try:
								imgPath = img.path
							except Exception:
								pass
							isOrphaned = bool(imgPath) and not os.path.exists(imgPath)
							if (isOrphaned and removeOrphaned) or (not isOrphaned and removeLinked):
								layer.setBackgroundImage_(None)
								removedInGlyph += 1
								if isOrphaned:
									orphanedInGlyph += 1

						# Background layer's background image
						try:
							bgLayer = layer.background
							bgImg = bgLayer.backgroundImage if bgLayer else None
							if bgImg is not None:
								bgImgPath = None
								try:
									bgImgPath = bgImg.path
								except Exception:
									pass
								isOrphaned = bool(bgImgPath) and not os.path.exists(bgImgPath)
								if (isOrphaned and removeOrphaned) or (not isOrphaned and removeLinked):
									bgLayer.setBackgroundImage_(None)
									removedInGlyph += 1
									if isOrphaned:
										orphanedInGlyph += 1
						except Exception:
							pass

					except Exception as e:
						print(f"\t⚠️ {glyph.name}, layer '{layer.name}': {e}")

				if removedInGlyph:
					orphanNote = f" ({orphanedInGlyph} orphaned)" if orphanedInGlyph else ""
					plural = "s" if removedInGlyph != 1 else ""
					print(f"\t✅ {glyph.name}: removed {removedInGlyph} image{plural}{orphanNote}")
					totalRemoved += removedInGlyph
					totalOrphaned += orphanedInGlyph

		except Exception as e:
			import traceback
			print(traceback.format_exc())

		finally:
			font.enableUpdateInterface()

		if totalRemoved:
			orphanNote = f" ({totalOrphaned} orphaned)" if totalOrphaned else ""
			plural = "s" if totalRemoved != 1 else ""
			summary = f"Removed {totalRemoved} image{plural}{orphanNote}."
		else:
			summary = "No images found to remove."

		print(f"\n{summary}")
		self.w.status.set(summary)
		Glyphs.showNotification("Remove Images", summary)


RemoveImages()
