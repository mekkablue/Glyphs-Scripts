# MenuTitle: Build asterisk
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Builds the asterisk from rotated components of _part.asterisk (a trapezoid ray with a #connect anchor). Each ray is rotated around the #connect anchor. A live preview updates the asterisk in all masters as you change the values.
"""

import objc
import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSPoint, NSAffineTransform
from GlyphsApp import Glyphs, GSComponent, GSPath, GSNode, LINE, GSMetricsTypeCapHeight, GSMetricsTypeAscender, Message
from mekkablue import mekkaObject, newAnchorWithName, newGlyphWithName

asteriskName = "asterisk"
partName = "_part.asterisk"
connectAnchorName = "#connect"

# geometry of the ray, in units:
rayHeight = 130
rayTopWidth = 80
rayBottomWidth = 20
rayInset = 100  # sidebearings of the part
connectDepth = 110  # distance of the #connect anchor below the cap height

buttAgainstOptions = (
	"cap height",
	"cap height overshoot",
	"ascender",
	"ascender overshoot",
	"height of…",
)
heightOfGlyphIndex = 4


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def rotationTransform(rotationCenter, rotationDegrees):
	"""Rotation by rotationDegrees (ccw is positive) around rotationCenter."""
	transform = NSAffineTransform.transform()
	transform.translateXBy_yBy_(rotationCenter.x, rotationCenter.y)
	transform.rotateByDegrees_(rotationDegrees)
	transform.translateXBy_yBy_(-rotationCenter.x, -rotationCenter.y)
	return transform


def metricPosition(font, master, metricType, withOvershoot=False):
	"""Returns the position of the metric of that type in the master, or None."""
	for metric in font.metrics:
		if metric.type == metricType:
			metricValue = master.metrics[metric.id]
			return metricValue.position + (metricValue.overshoot if withOvershoot else 0)
	return None


class BuildAsterisk(mekkaObject):
	prefDict = {
		"rays": 5,
		"inclination": 0,
		"buttAgainst": 0,
		"glyphName": "zero",
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Build asterisk",
			autosaveName=self.domain("mainwindow"),  # persists window position
		)

		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Builds the asterisk from rotated components of _part.asterisk. Each ray rotates around the #connect anchor of the part. After editing _part.asterisk, click Redraw.",
			sizeStyle="small",
			selectable=True,
		)

		self.w.raysLabel = vanilla.TextBox("auto", "Number of rays:", sizeStyle="small")
		self.w.rays = SteppingEditText("auto", "5", callback=self.SavePreferences, sizeStyle="small")
		self.w.rays.setToolTip("How many rays the asterisk has. Use the arrow keys to step up and down. The rays are distributed evenly around the circle.")

		self.w.inclinationLabel = vanilla.TextBox("auto", "Inclination:", sizeStyle="small")
		self.w.inclination = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle="small")
		self.w.inclination.setToolTip("Rotation of the first ray in degrees, clockwise. 0 means the first ray points north (up). Use the arrow keys to step.")
		self.w.inclinationText = vanilla.TextBox("auto", "° clockwise, 0 = north", sizeStyle="small")

		self.w.buttAgainstLabel = vanilla.TextBox("auto", "Butt against:", sizeStyle="small")
		self.w.buttAgainst = vanilla.PopUpButton("auto", buttAgainstOptions, callback=self.SavePreferences, sizeStyle="small")
		self.w.buttAgainst.setToolTip("The height the tip of the top-most (unrotated) ray reaches, measured in each master.")
		self.w.glyphName = vanilla.EditText("auto", "zero", callback=self.SavePreferences, sizeStyle="small")
		self.w.glyphName.setToolTip("Name of the glyph whose top edge (bounding box) is the height to butt against. Only active for ‘height of…’.")

		self.w.redrawButton = vanilla.Button("auto", "Redraw", callback=self.redraw)
		self.w.redrawButton.setToolTip("Recomposes the asterisk. Use this after you have edited _part.asterisk or moved its #connect anchor.")
		self.w.buildButton = vanilla.Button("auto", "Build", callback=self.build)
		self.w.buildButton.setToolTip("Updates the asterisk with the current values and closes this window.")
		self.w.setDefaultButton(self.w.buildButton)

		# the description wraps: it takes the width it is given instead of demanding one long line
		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(
			NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal
		)
		# the labels share one width and resist compression:
		for label in (self.w.raysLabel, self.w.inclinationLabel, self.w.buttAgainstLabel):
			nsLabel = label.getNSTextField()
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and buttons stretch vertically by default; hugging makes the window as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		rules = [
			"H:|-inset-[descriptionText]-inset-|",
			"H:|-inset-[raysLabel]-gap-[rays(60)]-(>=inset)-|",
			"H:|-inset-[inclinationLabel]-gap-[inclination(60)]-gap-[inclinationText]-(>=inset)-|",
			"H:|-inset-[buttAgainstLabel]-gap-[buttAgainst]-gap-[glyphName(90)]-inset-|",
			"H:|-(>=inset)-[redrawButton(>=70)]-gap-[buildButton(>=70)]-inset-|",
			"V:|-inset-[descriptionText(42)]-row-[rays]-row-[inclination]-row-[buttAgainst]-inset-[buildButton]-inset-|",
			{"view1": self.w.inclinationLabel, "attribute1": "width", "view2": self.w.raysLabel, "attribute2": "width"},
			{"view1": self.w.buttAgainstLabel, "attribute1": "width", "view2": self.w.raysLabel, "attribute2": "width"},
			{"view1": self.w.inclination, "attribute1": "width", "view2": self.w.rays, "attribute2": "width"},
		]
		# everything in a row sits on the vertical center of its field:
		rowFields = {
			self.w.rays: (self.w.raysLabel, ),
			self.w.inclination: (self.w.inclinationLabel, self.w.inclinationText),
			self.w.buttAgainst: (self.w.buttAgainstLabel, self.w.glyphName),
			self.w.buildButton: (self.w.redrawButton, ),
		}
		for field, others in rowFields.items():
			for other in others:
				rules.append({"view1": other, "attribute1": "centerY", "view2": field, "attribute2": "centerY"})
		self.w.addAutoPosSizeRules(rules, metrics={"inset": 15, "gap": 8, "row": 8})

		self.LoadPreferences()

		font = Glyphs.font
		self.prepareGlyphs(font)
		self.backUpAsterisk(font)
		self.compose(font, report=True)
		tab = font.newTab("/H/%s/%s" % (asteriskName, partName))
		tab.textCursor = len(tab.layers) - 1  # _part.asterisk, ready for editing

		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.glyphName.enable(self.w.buttAgainst.get() == heightOfGlyphIndex)

	def SavePreferences(self, sender=None):
		super().SavePreferences(sender)
		# live preview:
		self.compose(Glyphs.font)

	def redraw(self, sender=None):
		self.compose(Glyphs.font, report=True)

	def build(self, sender=None):
		self.compose(Glyphs.font, report=True)
		Glyphs.showNotification("Build asterisk", "Asterisk built. Details in Macro Window.")
		self.w.close()

	def settings(self):
		"""Returns (rays, inclination) from the UI, or None while the fields hold no valid numbers."""
		try:
			rays = int(self.pref("rays"))
			inclination = float(self.pref("inclination"))
		except (TypeError, ValueError):
			return None
		if rays < 1:
			return None
		return rays, inclination

	def buttHeight(self, font, master):
		"""The height the unrotated ray reaches in this master, or None."""
		index = self.prefInt("buttAgainst")
		if index == 0:
			return metricPosition(font, master, GSMetricsTypeCapHeight)
		elif index == 1:
			return metricPosition(font, master, GSMetricsTypeCapHeight, withOvershoot=True)
		elif index == 2:
			return metricPosition(font, master, GSMetricsTypeAscender)
		elif index == 3:
			return metricPosition(font, master, GSMetricsTypeAscender, withOvershoot=True)
		else:
			glyph = font.glyphs[self.pref("glyphName").strip()]
			if glyph is None:
				return None
			layer = glyph.layers[master.id]
			if not layer.shapes:
				return None
			return layer.bounds.origin.y + layer.bounds.size.height

	def prepareGlyphs(self, font):
		"""Makes sure asterisk and _part.asterisk exist, and that _part.asterisk is drawn in every master."""
		asteriskGlyph = font.glyphs[asteriskName]
		if asteriskGlyph is None:
			asteriskGlyph = newGlyphWithName(asteriskName)
			font.glyphs.append(asteriskGlyph)
			print("\t✅ Created %s" % asteriskName)
		partGlyph = font.glyphs[partName]
		if partGlyph is None:
			partGlyph = newGlyphWithName(partName)
			partGlyph.export = False
			font.glyphs.append(partGlyph)
			print("\t✅ Created %s" % partName)
		for master in font.masters:
			layer = partGlyph.layers[master.id]
			if layer.shapes:
				continue  # keep what the user drew
			capHeight = metricPosition(font, master, GSMetricsTypeCapHeight)
			topY = capHeight
			bottomY = topY - rayHeight
			centerX = rayInset + rayTopWidth / 2.0
			path = GSPath()
			for point in (
				NSPoint(centerX - rayBottomWidth / 2.0, bottomY),
				NSPoint(centerX + rayBottomWidth / 2.0, bottomY),
				NSPoint(centerX + rayTopWidth / 2.0, topY),
				NSPoint(centerX - rayTopWidth / 2.0, topY),
			):
				path.nodes.append(GSNode(point, type=LINE))
			path.closed = True
			layer.shapes.append(path)
			layer.width = rayTopWidth + 2 * rayInset
			layer.anchors.append(newAnchorWithName(connectAnchorName, NSPoint(centerX, topY - connectDepth)))
			print("\t✅ Drew %s in master %s" % (partName, master.name))

	def backUpAsterisk(self, font):
		"""Copies the current asterisk shapes into the background of each master layer, unless the layer only holds rays."""
		asteriskGlyph = font.glyphs[asteriskName]
		for master in font.masters:
			layer = asteriskGlyph.layers[master.id]
			shapes = tuple(layer.shapes)
			if not shapes:
				continue
			if all(hasattr(shape, "componentName") and shape.componentName == partName for shape in shapes):
				continue  # made by this script, so do not overwrite an earlier backup
			layer.background.clear()
			for shape in shapes:
				layer.background.shapes.append(shape.copy())
			layer.background.decomposeComponents()
			print("\t💾 Backed up previous %s of master %s in background" % (asteriskName, master.name))

	def compose(self, font, report=False):
		"""Recomposes the asterisk in all masters at once. If any master cannot be done, none is touched, so the masters stay in sync."""
		values = self.settings()
		if values is None:
			return
		rays, inclination = values
		asteriskGlyph = font.glyphs[asteriskName]
		partGlyph = font.glyphs[partName]
		if report:
			print("\nBuild asterisk: %i rays, first ray %s° clockwise from north\n" % (rays, inclination))

		# first pass: collect the center of rotation and the vertical offset of each master
		placements = []
		problems = []
		for master in font.masters:
			anchor = partGlyph.layers[master.id].anchors[connectAnchorName]
			capHeight = metricPosition(font, master, GSMetricsTypeCapHeight)
			buttHeight = self.buttHeight(font, master)
			if anchor is None:
				problems.append("%s: no %s anchor in %s" % (master.name, connectAnchorName, partName))
			elif capHeight is None or buttHeight is None:
				problems.append("%s: no height to butt against" % master.name)
			else:
				offsetY = buttHeight - capHeight
				placements.append((master, offsetY, NSPoint(anchor.position.x, anchor.position.y + offsetY)))
		if problems:
			if report:
				for problem in problems:
					print("\t⚠️ %s" % problem)
				print("\n\t⚠️ Nothing changed, so that all masters stay in sync.")
			return

		# second pass: draw all masters
		asteriskGlyph.leftMetricsKey = "=50"
		asteriskGlyph.rightMetricsKey = "=|"
		for master, offsetY, center in placements:
			layer = asteriskGlyph.layers[master.id]
			layer.shapes = None
			for rayIndex in range(rays):
				clockwiseDegrees = inclination + rayIndex * 360.0 / rays
				component = GSComponent(partName)
				component.automaticAlignment = False
				component.position = NSPoint(0, offsetY)
				component.applyTransform(rotationTransform(center, -clockwiseDegrees).transformStruct())
				layer.shapes.append(component)
			layer.updateMetrics()
			layer.syncMetrics()
			if report:
				print("\t✅ %s: %i rays around (%i, %i)" % (master.name, rays, center.x, center.y))
		if font.currentTab:
			font.currentTab.redraw()


font = Glyphs.font
if font:
	BuildAsterisk()
else:
	Message(title="No Font Open", message="Build asterisk needs a font. Please open one and run the script again.", OKButton=None)
