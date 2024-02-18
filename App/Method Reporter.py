# MenuTitle: Method Reporter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Searches in PyObjC method names of a chosen object.
"""

import vanilla
from AppKit import NSObject, NSPasteboard, NSStringPboardType
# from pydoc import help
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


def setClipboard(myText):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_([NSStringPboardType], None)
		myClipboard.setString_forType_(myText, NSStringPboardType)
		return True
	except Exception as e:
		print(e)
		import traceback
		print(traceback.format_exc())
		return False


class MethodReporter(mekkaObject):
	prefDict = {
		"objectPicker": "GSLayer",
		"filter": "",
	}

	def __init__(self):
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
			"GSBackgroundImage",
			"GSClass",
			"GSControlLayer",
			"GSCustomParameter",
			"GSEditViewController",
			"GlyphsPreviewPanel",
			"GSFeature",
			"GSFeaturePrefix",
			"GSFontMaster",
			"GSFontInfoValue",
			"GSFontInfoValueLocalized",
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
			"Glyph_g_l_y_f",
		)

		# Window 'self.w':
		windowWidth = 250
		windowHeight = 200
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 850  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Method Reporter",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI ELEMENTS:

		# Method Picker:
		self.w.objectPicker = vanilla.ComboBox((3, 2, 133, 24), self.mostImportantObjects, completes=True, continuous=False, callback=self.MethodReporterMain)
		self.w.objectPicker.set("GSLayer")
		self.w.objectPicker.getNSComboBox().setToolTip_("Type a class name here. Names will autocomplete.")

		# Filter:
		self.w.textFilter = vanilla.TextBox((140, 6, 35, 14), "Find:", sizeStyle='small')
		self.w.filter = vanilla.EditText((173, 1, -1, 24), "", callback=self.MethodReporterMain)
		self.w.filter.getNSTextField().setToolTip_("Type one or more (space-separated) search terms here. Case is ignored. Use * as wildcard at beginning, middle or end of term. Multiple search terms are AND-concatenated.")

		# Listing of methods:
		self.w.methodList = vanilla.List((0, 26, -0, -0), self.methodList("GSLayer"), autohidesScrollers=False, drawVerticalLines=True, doubleClickCallback=self.copySelection, rowHeight=19)
		self.w.methodList.getNSTableView().tableColumns()[0].setWidth_(501)
		self.w.methodList.getNSTableView().setToolTip_("Double click an entry to copy it to the clipboard and display its help() in Macro Window.")

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.bind("resize", self.adjustGUIObjects)
		self.w.open()
		self.w.makeKey()
		self.MethodReporterMain(None)

	def adjustGUIObjects(self, sender=None):
		windowLeft, windowTop, windowWidth, windowHeight = self.w.getPosSize()
		if windowWidth > 350:
			fifth = int(windowWidth * 0.4)

			posSizeObjectPicker = list(self.w.objectPicker.getPosSize())
			posSizeObjectPicker[2] = fifth - 7
			self.w.objectPicker.setPosSize(posSizeObjectPicker)

			posSizeTextFilter = list(self.w.textFilter.getPosSize())
			posSizeTextFilter[0] = fifth
			self.w.textFilter.setPosSize(posSizeTextFilter)

			posSizeFilter = list(self.w.filter.getPosSize())
			posSizeFilter[0] = fifth + 33
			self.w.filter.setPosSize(posSizeFilter)
		else:
			self.w.objectPicker.setPosSize((3, 2, 133, 24))
			self.w.textFilter.setPosSize((140, 6, 35, 14))
			self.w.filter.setPosSize((173, 1, -1, 24))

	def copySelection(self, sender):
		try:
			index = self.w.methodList.getSelection()[0]
			methodName = self.w.methodList[index]
			className = self.w.objectPicker.get()
			method = "%s.%s" % (className, methodName)

			# help in macro window:
			self.outputHelpForMethod(method)

			# puts method in clipboard:
			if not setClipboard(method):
				print("Warning: could not set clipboard.")
			else:
				print("\n%s copied in clipboard, ready for pasting." % method)

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
			helpStatement = "help(%s)" % method
			print("%s\n" % helpStatement)
			eval(helpStatement)
		except:
			if "." in method:
				dotIndex = method.find(".")
				firstPart = method[:dotIndex]
				secondPart = method[dotIndex:]
			else:
				firstPart = method
				secondPart = ""
			helpStatement = "help(NSClassFromString('%s')%s)" % (firstPart, secondPart)
			print("%s\n" % helpStatement)
			eval(helpStatement)
		Glyphs.showMacroWindow()

	def fullMethodName(self, className, methodName):
		"""
		Adds () if necessary.
		"""
		method = "%s.%s" % (className, methodName)
		methodType = type(eval(method))
		typeString = methodType.__name__
		if typeString != "property":
			methodName += "()"
		return methodName

	def methodList(self, className):
		elidableMethods = [method for method in dir(NSObject) if not method.startswith("__")]
		if className == "NSObject":
			return [
				self.fullMethodName(className, method) for method in elidableMethods if not method.startswith(".") and not method.startswith("_") and not method.startswith("SCN_")
			]
		else:
			try:
				actualClass = eval(className)
			except:
				newClassName = f"NSClassFromString('{className}')"
				actualClass = eval(newClassName)
				className = newClassName

			shortenedMethods = [
				self.fullMethodName(className, method) for method in dir(actualClass)
				if method not in elidableMethods and not method.startswith(".") and not method.startswith("_")
			]
			return shortenedMethods

	def MethodReporterMain(self, sender):
		try:
			className = self.w.objectPicker.get()
			filterStringEntry = self.w.filter.get().strip()
			filterStrings = filterStringEntry.split(" ")

			try:
				methods = self.methodList(className)  # fails for NSMutableArray
				methods = set(methods)
				methodList = sorted(methods)
				for filterString in filterStrings:
					if "*" not in filterString:
						methodList = [f for f in methodList if filterString.lower() in f.lower()]
					elif filterString.startswith("*"):
						methodList = [f for f in methodList if f.lower().endswith(filterString.lower()[1:])]
					elif filterString.endswith("*"):
						methodList = [f for f in methodList if f.lower().startswith(filterString.lower()[:-1])]
					else:
						asteriskPos = filterString.find("*")
						beginning = filterString[:asteriskPos].lower()
						ending = filterString[asteriskPos + 1:].lower()
						methodList = [f for f in methodList if f.lower().startswith(beginning) and f.lower().endswith(ending)]
			except:
				methodList = []

			self.w.methodList.set(methodList)

			self.SavePreferences()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Method Reporter Error: %s" % e)


MethodReporter()
