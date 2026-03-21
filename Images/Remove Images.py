# MenuTitle: Remove Images
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Removes placed images from glyphs. Options: scope (all glyphs in font or selected glyphs only), optional restriction to orphaned images only (source file no longer on disk), and optional glyph-name filter with wildcard support.
"""

import os
import vanilla
from mekkablue import mekkaObject, match
from GlyphsApp import Glyphs


class RemoveImages(mekkaObject):
	prefDict = {
		"scope": 0,
		"removeOrphaned": 1,
		"filterByName": 0,
		"nameFilter": "",
	}

	def __init__(self):
		windowWidth = 370
		windowHeight = 140
		windowWidthResize = 300
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
		self.w.scopeLabel = vanilla.TextBox((inset, linePos + 2, 120, 14), "Remove images in:", sizeStyle="small")
		self.w.scope = vanilla.PopUpButton(
			(inset + 112, linePos - 1, 185, 18),
			["selected glyphs only", "⚠️ all glyphs in font", "⚠️ all glyphs in all open fonts"],
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		scopeTooltip = "Choose the scope: selected glyphs only, all glyphs in the frontmost font, or all glyphs across every open font."
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope.setToolTip(scopeTooltip)
		linePos += lineHeight

		# Remove orphaned images only
		self.w.removeOrphaned = vanilla.CheckBox(
			(inset, linePos, -inset, 20),
			"Only remove orphaned images (source file no longer on disk)",
			value=True,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.removeOrphaned.setToolTip("If checked, only images whose source file can no longer be found on disk are removed. If unchecked, all placed images in the current scope are removed.")
		linePos += lineHeight

		# Filter by glyph name
		self.w.filterByName = vanilla.CheckBox(
			(inset, linePos, 168, 20),
			"Only in glyphs containing:",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.filterByName.setToolTip("If enabled, restricts removal to glyphs whose names match one of the comma-separated particles. Wildcards * and ? are supported.")
		self.w.nameFilter = vanilla.EditText(
			(inset + 155, linePos, -inset, 19),
			"",
			placeholder="(see tooltip)",
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.nameFilter.setToolTip("Comma-separated glyph name particles. Each particle is matched as a substring unless it contains wildcards. Wildcards * (any string) and ? (any single character) are supported. Example: 'A, *comb, ?.sc'")
		linePos += lineHeight

		# Status line and Run button
		self.w.status = vanilla.TextBox((inset, -20 - inset + 3, -80 - inset - 10, 14), "", sizeStyle="small")
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Remove", callback=self.run)
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

		removeOrphaned = self.prefBool("removeOrphaned")
		filterByName = self.prefBool("filterByName")
		nameFilter = self.pref("nameFilter") or ""
		scope = self.prefInt("scope")

		# Build per-font glyph lists (scope: 0=selected, 1=all in font, 2=all open fonts)
		if scope == 0:
			seen = set()
			glyphsByFont = {font: []}
			for layer in font.selectedLayers:
				glyph = layer.parent
				if glyph.name not in seen:
					seen.add(glyph.name)
					glyphsByFont[font].append(glyph)
		elif scope == 1:
			glyphsByFont = {font: list(font.glyphs)}
		else:
			glyphsByFont = {f: list(f.glyphs) for f in Glyphs.fonts}

		# Apply name filter
		if filterByName and nameFilter.strip():
			particles = [p.strip() for p in nameFilter.split(",") if p.strip()]
			if particles:
				glyphsByFont = {
					f: [g for g in gs if any(match("*" + p + "*", g.name) for p in particles)]
					for f, gs in glyphsByFont.items()
				}

		# Report header
		Glyphs.clearLog()
		print("Remove Images\n")
		scopeLabels = ["selected glyphs", "all glyphs in font", "all glyphs in all open fonts"]
		print(f"Scope: {scopeLabels[scope]}")
		if filterByName and nameFilter.strip():
			print(f"Name filter: {nameFilter.strip()}")
		print(f"Removing: {'orphaned images only' if removeOrphaned else 'all images'}\n")

		totalRemoved = 0
		totalOrphaned = 0

		for thisFont, glyphs in glyphsByFont.items():
			thisFont.disableUpdateInterface()
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
								if not removeOrphaned or isOrphaned:
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
									if not removeOrphaned or isOrphaned:
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
				thisFont.enableUpdateInterface()

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
