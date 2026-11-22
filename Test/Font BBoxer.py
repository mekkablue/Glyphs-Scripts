# MenuTitle: Font BBoxer
__doc__ = """
Overlays the highest, lowest, leftmost and rightmost glyphs in a resizable window, with the measurements in the canvas and a text report underneath. Ties are shown on top of each other. Optionally shows all glyphs of the scope as faint outlines.
"""

from time import time_ns

import vanilla
from mekkablue import mekkaObject, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, Message, GSMetricsTypeItalicAngle
from AppKit import (
	NSAffineTransform, NSAlternateKeyMask, NSAttributedString, NSEvent, NSEventMaskFlagsChanged, NSBezierPath, NSBitmapImageFileTypePNG, NSColor, NSFont,
	NSFontAttributeName, NSForegroundColorAttributeName, NSGraphicsContext, NSImage, NSPasteboard,
	NSPasteboardTypePNG, NSPasteboardTypePDF, NSRectFill, NSView,
	NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut,
)
from Foundation import NSMakePoint, NSMakeRect, NSUnionRect

baseAlpha = 0.4
alphaStep = 0.05
minimumAlpha = 0.1
marginX = 50
marginY = 24
labelGap = 4
tolerance = 0.001

# highest has more green and less red than lowest, rightmost more green and less blue than leftmost
lowestColor = NSColor.colorWithSRGBRed_green_blue_alpha_(0.45, 0.15, 1.0, 1.0)
highestColor = NSColor.colorWithSRGBRed_green_blue_alpha_(0.0, 0.65, 1.0, 1.0)
leftmostColor = NSColor.colorWithSRGBRed_green_blue_alpha_(1.0, 0.1, 0.45, 1.0)
rightmostColor = NSColor.colorWithSRGBRed_green_blue_alpha_(1.0, 0.5, 0.0, 1.0)

neutralLineAlpha = 0.6  # plain bounding box and design metrics

typoColor = NSColor.colorWithSRGBRed_green_blue_alpha_(0.0, 0.55, 0.25, 1.0)
hheaColor = NSColor.colorWithSRGBRed_green_blue_alpha_(0.4, 0.75, 0.15, 1.0)
winColor = NSColor.colorWithSRGBRed_green_blue_alpha_(0.05, 0.35, 0.2, 1.0)

# custom parameter, short name, sign of the height relative to the parameter value (usWinDescent is unsigned), color
verticalMetrics = (
	("typoAscender", "typoAsc", 1, typoColor),
	("typoDescender", "typoDesc", 1, typoColor),
	("hheaAscender", "hheaAsc", 1, hheaColor),
	("hheaDescender", "hheaDesc", 1, hheaColor),
	("winAscent", "winAsc", 1, winColor),
	("winDescent", "winDesc", -1, winColor),
)


def allGlyphsAlphaForCount(glyphCount):
	if glyphCount >= 3000:
		return 0.04
	if glyphCount > 2000:
		return 0.05
	if glyphCount > 1000:
		return 0.06
	if glyphCount > 500:
		return 0.07
	return 0.08


def composeText(labelText, numberText, showLabels, showNumbers):
	return " ".join(part for part, shown in ((labelText, showLabels), (numberText, showNumbers)) if shown and part)


def unionOfRects(firstRect, secondRect):
	if firstRect is None:
		return secondRect
	if secondRect is None:
		return firstRect
	return NSUnionRect(firstRect, secondRect)


class GlyphOverlayDrawing:
	allPaths = ()  # outlines of all glyphs in the scope, stroked thinly underneath the overlays
	allAlpha = 0.08
	overlays = ()  # (bezierPath, color) tuples, drawn in order
	labels = ()  # (labelText, numberText, color, edge) tuples, edge is "top", "bottom", "left" or "right"
	metricLines = ()  # (height, labelText, numberText, color) tuples
	designLines = ()  # heights of the design metrics, never labeled
	showLabels = True
	showNumbers = True
	unionRect = None  # bounding box of everything shown
	fitRect = None  # what has to fit into the view: the bounding box plus the metrics
	showBBox = True
	plainBBox = False  # all four sides in text color, when no measurement is shown
	transparent = False  # no background, for copying

	def drawRect_(self, rect):
		if not self.transparent:
			NSColor.textBackgroundColor().set()
			NSRectFill(self.bounds())
		if self.fitRect is None:
			return

		viewBounds = self.bounds()
		availableWidth = max(viewBounds.size.width - 2 * marginX, 1)
		availableHeight = max(viewBounds.size.height - 2 * marginY, 1)
		contentWidth = max(self.fitRect.size.width, 1)
		contentHeight = max(self.fitRect.size.height, 1)
		scale = min(availableWidth / contentWidth, availableHeight / contentHeight)
		shiftX = marginX + (availableWidth - contentWidth * scale) / 2 - self.fitRect.origin.x * scale
		shiftY = marginY + (availableHeight - contentHeight * scale) / 2 - self.fitRect.origin.y * scale

		NSGraphicsContext.saveGraphicsState()
		transform = NSAffineTransform.transform()
		transform.translateXBy_yBy_(shiftX, shiftY)
		transform.scaleBy_(scale)
		transform.concat()
		NSColor.textColor().colorWithAlphaComponent_(self.allAlpha).set()
		for path in self.allPaths:
			path.setLineWidth_(1.0 / scale)
			path.stroke()
		for path, color in self.overlays:
			color.set()
			path.fill()
		NSGraphicsContext.restoreGraphicsState()

		# design metrics (horizontal lines and the vertical line at x=0) stay within the bounding box, dotted like
		# its sides, and never get a label or number
		if self.designLines:
			horizontalRect = self.unionRect if self.unionRect is not None else self.fitRect
			designLeft = shiftX + horizontalRect.origin.x * scale
			designRight = designLeft + horizontalRect.size.width * scale
			designBottom = shiftY + horizontalRect.origin.y * scale
			designTop = designBottom + horizontalRect.size.height * scale
			designSegments = [((designLeft, shiftY + height * scale), (designRight, shiftY + height * scale)) for height in self.designLines]
			if designLeft <= shiftX <= designRight:
				designSegments.append(((shiftX, designBottom), (shiftX, designTop)))
			NSColor.textColor().colorWithAlphaComponent_(neutralLineAlpha).set()
			for start, end in designSegments:
				designPath = NSBezierPath.bezierPath()
				designPath.moveToPoint_(NSMakePoint(*start))
				designPath.lineToPoint_(NSMakePoint(*end))
				designPath.setLineWidth_(1.5)
				designPath.setLineDash_count_phase_((4.0, 4.0), 2, 0.0)
				designPath.stroke()

		metricAttributes = {NSFontAttributeName: NSFont.systemFontOfSize_(9)}
		for height, labelText, numberText, color in self.metricLines:
			y = shiftY + height * scale
			linePath = NSBezierPath.bezierPath()
			linePath.moveToPoint_(NSMakePoint(0, y))
			linePath.lineToPoint_(NSMakePoint(viewBounds.size.width, y))
			linePath.setLineWidth_(1.0)
			color.set()
			linePath.stroke()
			text = composeText(labelText, numberText, self.showLabels, self.showNumbers)
			if not text:
				continue
			metricAttributes[NSForegroundColorAttributeName] = color
			label = NSAttributedString.alloc().initWithString_attributes_(text, metricAttributes)
			size = label.size()
			labelY = y + 1 if height >= 0 else y - 1 - size.height
			label.drawAtPoint_(NSMakePoint(viewBounds.size.width - labelGap - size.width, labelY))

		if self.unionRect is None:
			return
		boxLeft = shiftX + self.unionRect.origin.x * scale
		boxBottom = shiftY + self.unionRect.origin.y * scale
		boxRight = boxLeft + self.unionRect.size.width * scale
		boxTop = boxBottom + self.unionRect.size.height * scale
		sides = {
			"top": ((boxLeft, boxTop), (boxRight, boxTop)),
			"bottom": ((boxLeft, boxBottom), (boxRight, boxBottom)),
			"left": ((boxLeft, boxBottom), (boxLeft, boxTop)),
			"right": ((boxRight, boxBottom), (boxRight, boxTop)),
		}
		if self.showBBox:
			if self.plainBBox:
				plainColor = NSColor.textColor().colorWithAlphaComponent_(neutralLineAlpha)
				sideColors = [(plainColor, edge) for edge in ("top", "bottom", "left", "right")]
			else:
				sideColors = [(color, edge) for labelText, numberText, color, edge in self.labels]
			for color, edge in sideColors:
				start, end = sides[edge]
				sidePath = NSBezierPath.bezierPath()
				sidePath.moveToPoint_(NSMakePoint(*start))
				sidePath.lineToPoint_(NSMakePoint(*end))
				sidePath.setLineWidth_(1.5)
				sidePath.setLineDash_count_phase_((4.0, 4.0), 2, 0.0)
				color.set()
				sidePath.stroke()

		for labelText, numberText, color, edge in self.labels:
			text = composeText(labelText, numberText, self.showLabels, self.showNumbers)
			if not text:
				continue
			attributes = {
				NSFontAttributeName: NSFont.systemFontOfSize_(10),
				NSForegroundColorAttributeName: color,
			}
			label = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
			size = label.size()
			if edge == "top":
				point = ((boxLeft + boxRight - size.width) / 2, boxTop + labelGap)
			elif edge == "bottom":
				point = ((boxLeft + boxRight - size.width) / 2, boxBottom - labelGap - size.height)
			elif edge == "left":
				point = (boxLeft - labelGap - size.width, (boxBottom + boxTop - size.height) / 2)
			else:
				point = (boxRight + labelGap, (boxBottom + boxTop - size.height) / 2)
			label.drawAtPoint_(point)


# Objective-C class names are global and Glyphs keeps them between script runs, so every run needs a new name
GlyphOverlayView = type(
	f"MekkaGlyphOverlayView{time_ns()}",
	(NSView, ),
	{name: value for name, value in vars(GlyphOverlayDrawing).items() if not name.startswith("__")},
)


class GlyphOverlayPreview(vanilla.Group):
	nsViewClass = GlyphOverlayView


def layerKey(entry):
	fontIndex, font, layer, bounds = entry
	return (fontIndex, layer.parent.name, layer.layerId)


class ReportHighestAndLowestGlyphs(mekkaObject):
	prefDict = {
		"showHighLow": True,
		"showLeftRight": True,
		"showBBox": True,
		"showAll": False,
		"showMetrics": False,
		"showDesignMetrics": False,
		"showLabels": False,
		"showNumbers": True,
		"scope": 0,
	}

	def __init__(self):
		windowWidth = 360
		windowHeight = 540
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Font BBoxer",
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		inset = 15
		self.cachedScope = None
		self.cachedEntries = []
		self.cachedUnionRect = None
		self.cachedPaths = None
		self.cachedMetricLines = ()
		self.cachedDesignHeights = ()
		self.shownEntries = []

		self.w.preview = GlyphOverlayPreview("auto")
		self.w.report = vanilla.TextEditor("auto", "", readOnly=True)
		self.w.report.setToolTip("Highest, lowest, leftmost (smallest origin.x) and rightmost (highest origin.x + width) glyph.")
		self.w.report.getNSTextView().setFont_(NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))

		self.w.showHighLow = vanilla.CheckBox("auto", "Show highest/lowest", callback=self.SavePreferences, sizeStyle="small")
		self.w.showHighLow.setToolTip("Overlay the highest and the lowest glyphs.")
		self.w.showLeftRight = vanilla.CheckBox("auto", "Show left/rightmost", callback=self.SavePreferences, sizeStyle="small")
		self.w.showLeftRight.setToolTip("Overlay the leftmost glyph (smallest origin.x) and the rightmost glyph (highest origin.x + width).")
		self.w.showBBox = vanilla.CheckBox("auto", "Show bounding box", callback=self.SavePreferences, sizeStyle="small")
		self.w.showBBox.setToolTip("Dotted bounding box sides for the shown measurements, in the color of the respective glyph.")
		self.w.showAll = vanilla.CheckBox("auto", "Show all glyphs", callback=self.SavePreferences, sizeStyle="small")
		self.w.showAll.setToolTip("Also draw the outlines of all exporting glyphs in the scope, as faint outlines.")
		self.w.showMetrics = vanilla.CheckBox("auto", "Show vertical metrics", callback=self.SavePreferences, sizeStyle="small")
		self.w.showMetrics.setToolTip("Horizontal lines for the typo, hhea and win ascender and descender values set in the masters or the font, in shades of green. Heights that several metrics share are shown once.")

		scopeTooltip = "Which glyphs to measure."
		self.w.scopeLabel = vanilla.TextBox("auto", "Scope:", sizeStyle="small", selectable=True)
		self.w.scopeLabel.setToolTip(scopeTooltip)
		self.w.scope = vanilla.PopUpButton(
			"auto",
			("Current Master of Frontmost Font", "All Masters of Frontmost Font", "All Masters of All Open Fonts"),
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.scope.setToolTip(scopeTooltip)
		self.w.previousButton = vanilla.Button("auto", "", callback=self.stepThrough)
		self.w.previousButton.getNSButton().setImage_(NSImage.imageNamed_("NSGoLeftTemplate"))
		self.w.previousButton.getNSButton().setBordered_(False)
		self.w.nextButton = vanilla.Button("auto", "", callback=self.stepThrough)
		self.w.nextButton.getNSButton().setImage_(NSImage.imageNamed_("NSGoRightTemplate"))
		self.w.nextButton.getNSButton().setBordered_(False)

		self.w.updateButton = UpdateButton("auto", callback=self.refresh)
		self.w.updateButton.setToolTip("Measure and redraw again, e.g. after switching the master, changing glyphs or opening a font.")

		self.w.showDesignMetrics = vanilla.CheckBox("auto", "Show design metrics", callback=self.SavePreferences, sizeStyle="small")
		self.w.showDesignMetrics.setToolTip("Dotted lines within the bounding box for the font’s metrics (baseline, x-height, cap height, ascender, descender and so on) as set in the masters, except italic angles, plus a vertical line at x=0. Never labeled.")

		self.w.showLabels = vanilla.CheckBox("auto", "Show labels", callback=self.SavePreferences, sizeStyle="small")
		self.w.showLabels.setToolTip("Name the vertical metric lines in the canvas (typo, hhea, win). The numbers at the bounding box never get a name, and design metrics are never labeled.")
		self.w.showNumbers = vanilla.CheckBox("auto", "Show numbers", callback=self.SavePreferences, sizeStyle="small")
		self.w.showNumbers.setToolTip("Show the values of the measurements and the vertical metrics in the canvas. Design metrics never show numbers.")

		self.w.copyPNGButton = vanilla.Button("auto", "Copy PNG", callback=self.copyImage)
		self.w.copyPNGButton.setToolTip("Copies the canvas at its current size as a PNG with transparent background. Hold down the Option key to copy a PDF instead, with the background of the current appearance (dark in Dark Mode).")
		self.w.openTabButton = vanilla.Button("auto", "Open Tab", callback=self.openTab)
		self.w.openTabButton.setToolTip("Opens a tab with all currently shown glyphs in the fonts of the scope.")
		self.w.setDefaultButton(self.w.openTabButton)

		nsScopeLabel = self.w.scopeLabel.getNSTextField()
		nsScopeLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# the preview takes all extra height, everything else hugs
		self.w.preview.getNSView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)
		for view in self.w.getNSWindow().contentView().subviews():
			if view is not self.w.preview.getNSView():
				view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[preview]-inset-|",
				"H:|-inset-[report]-inset-|",
				"H:|-inset-[showHighLow]-gap-[showLeftRight]-(>=inset)-|",
				"H:|-inset-[showBBox]-gap-[showAll]-(>=inset)-|",
				"H:|-inset-[scopeLabel]-gap-[scope]-gap-[previousButton(24)]-buttonGap-[nextButton(24)]-buttonGap-[updateButton(24)]-inset-|",
				{"view1": self.w.previousButton, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.nextButton, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				"H:|-inset-[showMetrics]-gap-[showDesignMetrics]-(>=inset)-|",
				"H:|-inset-[showLabels]-gap-[showNumbers]-(>=inset)-|",
				{"view1": self.w.showNumbers, "attribute1": "centerY", "view2": self.w.showLabels, "attribute2": "centerY"},
				{"view1": self.w.showLabels, "attribute1": "width", "view2": self.w.showHighLow, "attribute2": "width"},
				{"view1": self.w.showDesignMetrics, "attribute1": "centerY", "view2": self.w.showMetrics, "attribute2": "centerY"},
				{"view1": self.w.showMetrics, "attribute1": "width", "view2": self.w.showHighLow, "attribute2": "width"},
				"H:|-inset-[copyPNGButton(>=70)]-(>=gap)-[openTabButton(>=70)]-inset-|",
				"V:|-inset-[preview(>=150)]-gap-[report(64)]-row-[showHighLow]-checkRow-[showBBox]-checkRow-[showMetrics]-checkRow-[showLabels]-row-[scope]-inset-[openTabButton]-inset-|",
				"V:[copyPNGButton]-inset-|",
				{"view1": self.w.showLeftRight, "attribute1": "centerY", "view2": self.w.showHighLow, "attribute2": "centerY"},
				{"view1": self.w.showAll, "attribute1": "centerY", "view2": self.w.showBBox, "attribute2": "centerY"},
				{"view1": self.w.showBBox, "attribute1": "width", "view2": self.w.showHighLow, "attribute2": "width"},
				{"view1": self.w.scopeLabel, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 8, "checkRow": 5, "buttonGap": 4},
		)

		self.optionKeyMonitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(NSEventMaskFlagsChanged, self.optionKeyChanged)
		self.w.bind("close", self.removeMonitor)

		makeWindowResizable(self.w, vertical=True, minSize=(300, 440))  # resizable, limits in content sizes

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def collectEntries(self):
		scope = self.prefInt("scope")
		frontFont = Glyphs.font
		if scope == 2:
			fonts = tuple(Glyphs.fonts)
		else:
			fonts = (frontFont, )

		entries = []
		for fontIndex, font in enumerate(fonts):
			if scope == 0:
				masterIDs = (font.selectedFontMaster.id, )
			else:
				masterIDs = tuple(master.id for master in font.masters)
			for glyph in font.glyphs:
				if not glyph.export:
					continue
				for masterID in masterIDs:
					layer = glyph.layers[masterID]
					if layer is None or not layer.shapes:
						continue
					entries.append((fontIndex, font, layer, layer.bounds))
		return entries

	def collectMetricLines(self):
		scope = self.prefInt("scope")
		fonts = tuple(Glyphs.fonts) if scope == 2 else (Glyphs.font, )
		linesByHeight = {}  # rounded height -> [height, short names, color]
		for font in fonts:
			masters = (font.selectedFontMaster, ) if scope == 0 else font.masters
			for master in masters:
				for parameterName, shortName, sign, color in verticalMetrics:
					value = master.customParameters[parameterName]
					if value is None:
						value = font.customParameters[parameterName]
					if value is None:
						continue
					height = sign * float(value)
					line = linesByHeight.setdefault(round(height, 2), [height, [], color])
					if shortName not in line[1]:
						line[1].append(shortName)
		return tuple(
			(height, ", ".join(shortNames), f"{round(height, 1):g}", color)
			for height, shortNames, color in sorted(linesByHeight.values(), key=lambda line: -line[0])
		)

	def collectDesignMetricHeights(self):
		scope = self.prefInt("scope")
		fonts = tuple(Glyphs.fonts) if scope == 2 else (Glyphs.font, )
		heights = set()
		for font in fonts:
			masters = (font.selectedFontMaster, ) if scope == 0 else font.masters
			for master in masters:
				for metric in font.metrics:
					if metric.type == GSMetricsTypeItalicAngle:
						continue
					heights.add(round(master.metrics[metric.id].position, 2))
		return tuple(sorted(heights, reverse=True))

	def describe(self, entry, value):
		fontIndex, font, layer, bounds = entry
		scope = self.prefInt("scope")
		context = []
		if scope == 2 and len(Glyphs.fonts) > 1:
			context.append(font.familyName)
		if scope >= 1 and len(font.masters) > 1:
			context.append(layer.master.name)
		details = f"{round(value, 1):g}"
		if context:
			details += " · " + " ".join(context)
		return f"{layer.parent.name} ({details})"

	def extremes(self, entries, valueFunction, useMax):
		values = [valueFunction(entry) for entry in entries]
		best = max(values) if useMax else min(values)
		return best, [entry for entry, value in zip(entries, values) if abs(value - best) < tolerance]

	def updateUI(self, sender=None):
		if not Glyphs.font or self.w is None:
			return
		scope = self.prefInt("scope")
		self.w.showLabels.enable(self.prefBool("showMetrics"))
		stepEnabled = scope == 0 or (scope == 1 and len(Glyphs.fonts) > 1)
		stepTooltips = {
			0: ("Select the previous master of the frontmost font.", "Select the next master of the frontmost font."),
			1: ("Bring the previous open font to the front.", "Bring the next open font to the front."),
			2: ("Stepping is not available when measuring all open fonts.", ) * 2,
		}[scope]
		for button, tooltip in zip((self.w.previousButton, self.w.nextButton), stepTooltips):
			button.enable(stepEnabled)
			button.setToolTip(tooltip)
		if scope != self.cachedScope:
			self.cachedEntries = self.collectEntries()
			self.cachedScope = scope
			self.cachedPaths = None
			self.cachedUnionRect = None
			self.cachedMetricLines = self.collectMetricLines()
			self.cachedDesignHeights = self.collectDesignMetricHeights()
			for entry in self.cachedEntries:
				self.cachedUnionRect = unionOfRects(self.cachedUnionRect, entry[3])
		entries = self.cachedEntries
		showAll = self.prefBool("showAll")
		if showAll and self.cachedPaths is None:
			self.cachedPaths = tuple(entry[2].completeBezierPath for entry in entries)

		categories = (
			("⬇️", lambda e: e[3].origin.y, False, "highLow", lowestColor, "bottom"),
			("⬆️", lambda e: e[3].origin.y + e[3].size.height, True, "highLow", highestColor, "top"),
			("⬅️", lambda e: e[3].origin.x, False, "leftRight", leftmostColor, "left"),
			("➡️", lambda e: e[3].origin.x + e[3].size.width, True, "leftRight", rightmostColor, "right"),
		)
		reportLines = {}
		overlays = []
		labels = []
		unionRect = None
		self.shownEntries = []
		shownKeys = set()
		for emoji, valueFunction, useMax, group, color, edge in categories:
			if not entries:
				reportLines[emoji] = f"{emoji} –"
				continue
			best, tied = self.extremes(entries, valueFunction, useMax)
			reportLines[emoji] = f"{emoji} " + ", ".join(self.describe(entry, best) for entry in tied)
			shown = self.prefBool("showHighLow") if group == "highLow" else self.prefBool("showLeftRight")
			if not shown:
				continue
			alpha = max(minimumAlpha, baseAlpha - alphaStep * (len(tied) - 1))
			for entry in tied:
				layer, bounds = entry[2], entry[3]
				overlays.append((layer.completeBezierPath, color.colorWithAlphaComponent_(alpha)))
				unionRect = unionOfRects(unionRect, bounds)
				key = layerKey(entry)
				if key not in shownKeys:
					shownKeys.add(key)
					self.shownEntries.append(entry)
			labels.append(("", f"{round(best, 1):g}", color, edge))
		reportOrder = ("⬆️", "⬇️", "⬅️", "➡️")
		self.w.report.set("\n".join(reportLines[emoji] for emoji in reportOrder))

		plainBBox = not self.prefBool("showHighLow") and not self.prefBool("showLeftRight") and self.prefBool("showBBox")
		if showAll or plainBBox:
			unionRect = unionOfRects(unionRect, self.cachedUnionRect)

		metricLines = self.cachedMetricLines if self.prefBool("showMetrics") else ()
		designHeights = self.cachedDesignHeights if self.prefBool("showDesignMetrics") else ()
		metricHeights = [line[0] for line in metricLines] + list(designHeights)
		fitRect = unionRect
		if metricHeights:
			if fitRect is None:
				fitRect = self.cachedUnionRect
			lowestHeight, highestHeight = min(metricHeights), max(metricHeights)
			horizontalOrigin, horizontalSize = (fitRect.origin.x, fitRect.size.width) if fitRect is not None else (0, 1000)
			fitRect = unionOfRects(fitRect, NSMakeRect(horizontalOrigin, lowestHeight, horizontalSize, highestHeight - lowestHeight))

		view = self.w.preview.getNSView()
		view.plainBBox = plainBBox
		view.designLines = designHeights
		view.showLabels = self.prefBool("showLabels")
		view.showNumbers = self.prefBool("showNumbers")
		view.allPaths = self.cachedPaths if showAll else ()
		view.allAlpha = allGlyphsAlphaForCount(len(entries))
		view.metricLines = metricLines
		view.fitRect = fitRect
		view.labels = tuple(labels)
		view.overlays = tuple(overlays)
		view.unionRect = unionRect
		view.showBBox = self.prefBool("showBBox")
		view.setNeedsDisplay_(True)
		self.w.openTabButton.enable(bool(self.shownEntries))

	def stepThrough(self, sender=None):
		font = Glyphs.font
		if not font:
			return
		step = -1 if sender is self.w.previousButton else 1
		if self.prefInt("scope") == 0:
			font.masterIndex = (font.masterIndex + step) % len(font.masters)
		else:
			fonts = tuple(Glyphs.fonts)
			targetFont = fonts[(fonts.index(font) + step) % len(fonts)]
			targetFont.parent.windowController().window().makeKeyAndOrderFront_(None)
		self.refresh()

	def refresh(self, sender=None):
		self.cachedScope = None
		self.updateUI()

	def optionKeyChanged(self, event):
		optionDown = bool(event.modifierFlags() & NSAlternateKeyMask)
		self.w.copyPNGButton.setTitle("Copy PDF" if optionDown else "Copy PNG")
		return event

	def removeMonitor(self, sender=None):
		if self.optionKeyMonitor is not None:
			NSEvent.removeMonitor_(self.optionKeyMonitor)
			self.optionKeyMonitor = None

	def copyImage(self, sender=None):
		view = self.w.preview.getNSView()
		pasteboard = NSPasteboard.generalPasteboard()
		if NSEvent.modifierFlags() & NSAlternateKeyMask:
			# PDF keeps the background of the current appearance, i.e. dark in Dark Mode
			view.transparent = False
			pdfData = view.dataWithPDFInsideRect_(view.bounds())
			pasteboard.clearContents()
			pasteboard.setData_forType_(pdfData, NSPasteboardTypePDF)
			message = "PDF copied to the clipboard."
		else:
			view.transparent = True
			bitmap = view.bitmapImageRepForCachingDisplayInRect_(view.bounds())
			view.cacheDisplayInRect_toBitmapImageRep_(view.bounds(), bitmap)
			view.transparent = False
			pngData = bitmap.representationUsingType_properties_(NSBitmapImageFileTypePNG, {})
			pasteboard.clearContents()
			pasteboard.setData_forType_(pngData, NSPasteboardTypePNG)
			message = "PNG copied to the clipboard."
		Glyphs.showNotification("Font BBoxer", message)

	def openTab(self, sender=None):
		layersByFont = {}
		fonts = {}
		for fontIndex, font, layer, bounds in self.shownEntries:
			layersByFont.setdefault(fontIndex, []).append(layer)
			fonts[fontIndex] = font
		for fontIndex, layers in layersByFont.items():
			fonts[fontIndex].newTab(layers)


if Glyphs.font:
	ReportHighestAndLowestGlyphs()
else:
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
