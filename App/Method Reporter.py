# MenuTitle: Method Reporter
__doc__ = """
Searches in PyObjC method names of a chosen object.
"""

import vanilla
from AppKit import NSObject, NSWindowStyleMaskResizable
from Foundation import NSSize
from GlyphsApp import Glyphs
from mekkablue import setClipboard, mekkaObject


class MethodReporter(mekkaObject):
	prefDict = {
		"objectPicker": "GSLayer",
		"filter": "",
	}

	def __init__(self):
		self.methodCache = {}  # listing the methods of a big class takes a while, so do it only once

		if Glyphs.versionNumber < 4.0:
			infoValueObjects = ("GSFontInfoValue", "GSFontInfoValueLocalized")
		else:
			# Glyphs 4 renamed GSFontInfoValue* to GSInfoValue*
			infoValueObjects = ("GSInfoValue", "GSInfoValueLocalized")

		self.mostImportantObjects = (
			"GSLayer",
			"GSGlyph",
			"GSFont",
			"GSPath",
			"GSComponent",
			"GSAlignmentZone",
			"GSAnchor",
			"GSAnnotation",
			"GSApplication",
			"Glyphs",
			"GSBackgroundImage",
			"GSClass",
			"GSControlLayer",
			"GSCustomParameter",
			"GSDocument",
			"GSWindowController",
			"GSEditViewController",
			"GlyphsPreviewPanel",
			"GSFeature",
			"GSFeaturePrefix",
			"GSFontMaster",
		) + infoValueObjects + (
			"GSGlyphEditView",
			"GSGlyphInfo",
			"GSGlyphsInfo",
			"GSGuide",
			"GSGuideLine",
			"GSHint",
			"GSInstance",
			"GSMetricValue",
			"GSNode",
			"GSPathPen",
			"GSPathSegment",
			"GSProjectDocument",
			"GSAxis",
			"GSSmartComponentAxis",
			# NS object
			"NSBezierPath",
			"NSColor",
			"NSAffineTransform",
			"NSAffineTransformStruct",
			"NSDate",
			"NSImage",
			"NSTextField",
			"NSComboBox",
			"NSPopUpButton",
			"NSButton",
			"NSString",
			"NSMutableArray",
			"FTPointArray",
			# TT glyph
			"Glyph_g_l_y_f",
			# tools
			"SelectTool",
			"ReporterPlugin",
			"PalettePlugin",
			"GeneralPlugin",
			"FilterWithoutDialog",
			"FilterWithDialog",
			"FileFormatPlugin",
			# vanilla
			"vanilla",
		)

		# Window 'self.w':
		windowWidth = 320
		windowHeight = 260
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 850  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Method Reporter",
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI ELEMENTS:
		inset = 8

		# Method Picker:
		self.w.objectPicker = vanilla.ComboBox("auto", self.mostImportantObjects, completes=True, continuous=False, callback=self.MethodReporterMain, sizeStyle="small")
		self.w.objectPicker.setToolTip("Type a class name here. Names will autocomplete.")

		# Filter:
		self.w.textFilter = vanilla.TextBox("auto", "Find:", sizeStyle="small")
		self.w.filter = vanilla.EditText("auto", "", callback=self.MethodReporterMain, sizeStyle="small")
		tooltip = "Type one or more (space-separated) search terms here. Case is ignored. Use * as wildcard at beginning, middle or end of term. Multiple search terms are AND-concatenated.\n\nIf one of the search terms is ‘_*’, it will display methods that start with underscores. They are otherwise left out to reduce clutter."
		self.w.textFilter.setToolTip(tooltip)
		self.w.filter.setToolTip(tooltip)

		# Listing of methods:
		self.w.methodList = vanilla.List("auto", [], autohidesScrollers=False, drawVerticalLines=True, doubleClickCallback=self.copySelection, rowHeight=19)
		self.w.methodList.getNSTableView().tableColumns()[0].setWidth_(501)
		self.w.methodList.getNSTableView().setToolTip_("Double click an entry to copy it to the clipboard and display its help() in Macro Window.")

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[objectPicker(150)]-gap-[textFilter]-gap-[filter]-inset-|",
				"H:|[methodList]|",
				"V:|-inset-[objectPicker]-inset-[methodList(>=100)]|",
				{"view1": self.w.textFilter, "attribute1": "centerY", "view2": self.w.objectPicker, "attribute2": "centerY"},
				{"view1": self.w.filter, "attribute1": "centerY", "view2": self.w.objectPicker, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in both directions. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.setContentMinSize_(NSSize(windowWidth, windowHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, windowHeight + windowHeightResize))

		self.MethodReporterMain(None)

	def copySelection(self, sender):
		try:
			selection = self.w.methodList.getSelection()
			if not selection:
				return
			methodName = self.w.methodList[selection[0]]
			className = self.w.objectPicker.get()
			method = f"{className}.{methodName}"

			# help in macro window:
			self.outputHelpForMethod(method)

			# puts method in clipboard:
			if not setClipboard(method):
				print("⚠️ Warning: could not set clipboard.")
			else:
				print(f"\n{method} copied in clipboard, ready for pasting.")

		except Exception as e:
			print(e)
			Glyphs.showMacroWindow()
			import traceback
			print(traceback.format_exc())

	def outputHelpForMethod(self, method):
		# strip parentheses if necessary:
		if method.endswith("()"):
			method = method[:-2]

		# brings macro window to front, clears its log, outputs help for method:
		Glyphs.clearLog()
		try:
			helpStatement = f"help({method})"
			print(f"{helpStatement}\n")
			eval(helpStatement)
		except Exception:
			if "." in method:
				dotIndex = method.find(".")
				firstPart = method[:dotIndex]
				secondPart = method[dotIndex:]
			else:
				firstPart = method
				secondPart = ""
			helpStatement = f"help(NSClassFromString('{firstPart}'){secondPart})"
			print(f"{helpStatement}\n")
			eval(helpStatement)
		Glyphs.showMacroWindow()

	def fullMethodName(self, className, methodName):
		"""
		Adds () if necessary.
		"""
		try:
			methodType = type(eval(f"{className}.{methodName}"))
		except Exception:
			# a single attribute that cannot be evaluated must not spoil the whole listing
			return methodName
		if methodType.__name__ != "property":
			methodName += "()"
		return methodName

	def methodList(self, className, allowUnderscored=False):
		cacheKey = (className, allowUnderscored)
		if cacheKey in self.methodCache:
			return self.methodCache[cacheKey]

		elidableMethods = [method for method in dir(NSObject) if not method.startswith("__")]
		if className == "NSObject":
			methods = [
				self.fullMethodName(className, method) for method in elidableMethods
				if not method.startswith(".") and not method.startswith("_") and not method.startswith("SCN_")
			]
		else:
			try:
				actualClass = eval(className)
			except Exception:
				newClassName = f"NSClassFromString('{className}')"
				actualClass = eval(newClassName)
				className = newClassName

			methods = [
				self.fullMethodName(className, method) for method in dir(actualClass)
				if method not in elidableMethods and not method.startswith(".")
				and (allowUnderscored or not method.startswith("_"))
			]
		self.methodCache[cacheKey] = methods
		return methods

	def MethodReporterMain(self, sender):
		try:
			className = self.w.objectPicker.get().strip()
			filterStrings = self.w.filter.get().strip().split(" ")

			try:
				shouldAllowUnderscored = "_*" in filterStrings
				methods = self.methodList(className, allowUnderscored=shouldAllowUnderscored)  # fails for NSMutableArray
				methodList = sorted(set(methods))
				for filterString in filterStrings:
					filterString = filterString.lower()
					if "*" not in filterString:
						methodList = [f for f in methodList if filterString in f.lower()]
					elif filterString.startswith("*"):
						methodList = [f for f in methodList if f.lower().endswith(filterString[1:])]
					elif filterString.endswith("*"):
						methodList = [f for f in methodList if f.lower().startswith(filterString[:-1])]
					else:
						asteriskPos = filterString.find("*")
						beginning = filterString[:asteriskPos]
						ending = filterString[asteriskPos + 1:]
						methodList = [f for f in methodList if f.lower().startswith(beginning) and f.lower().endswith(ending)]
			except Exception:
				# an unknown class name (e.g., while typing) simply gives an empty list
				methodList = []

			self.w.methodList.set(methodList)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Method Reporter Error: {e}")


MethodReporter()
