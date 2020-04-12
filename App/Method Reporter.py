#MenuTitle: Method Reporter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Searches in PyObjC method names of a chosen object.
"""

import vanilla
from AppKit import NSPasteboard, NSStringPboardType, NSUserDefaults

def setClipboard( myText ):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_( [NSStringPboardType], None )
		myClipboard.setString_forType_( myText, NSStringPboardType )
		return True
	except Exception as e:
		print(e)
		import traceback
		print(traceback.format_exc())
		return False

class MethodReporter( object ):
	def __init__( self ):
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
			"GSFeature",
			"GSFeaturePrefix",
			"GSFontMaster",
			"GSGlyphEditView",
			"GSGlyphInfo",
			"GSGlyphsInfo",
			"GSGuide",
			"GSGuideLine",
			"GSHint",
			"GSInstance",
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
			"FTPointArray",
			"Glyph_g_l_y_f",
		)
		
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 200
		windowWidthResize  = 400 # user can resize width by this value
		windowHeightResize = 650 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Method Reporter", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.MethodReporter.mainwindow" # stores last window position and size
		)
		
		# UI ELEMENTS:
		
		# Method Picker:
		self.w.objectPicker = vanilla.ComboBox(
			(3, 2, 133, 24),
			self.mostImportantObjects,
			sizeStyle='regular',
			completes=True,
			continuous=False,
			callback=self.MethodReporterMain
		)
		self.w.objectPicker.set("GSLayer")
		self.w.objectPicker.getNSComboBox().setToolTip_("Type a class name here. Names will autocomplete.")
		
		# Filter:
		self.w.text2 = vanilla.TextBox(
			(140, 6, 35, 14),
			"Find:",
			sizeStyle='small'
		)
		self.w.filter = vanilla.EditText(
			(173, 1, -1, 24 ),
			"",
			sizeStyle='regular',
			callback=self.MethodReporterMain
		)
		self.w.filter.getNSTextField().setToolTip_("Type one or more (space-separated) search terms here. Case is ignored. Use * as wildcard at beginning, middle or end of term. Multiple search terms are AND-concatenated.")
		
		# Listing of methods:
		self.w.methodList = vanilla.List(
			(0, 26, -0, -0),
			self.methodList("GSLayer"),
			autohidesScrollers=False,
			drawVerticalLines=True,
			doubleClickCallback=self.copySelection,
			rowHeight=19,
		)
		self.w.methodList.getNSTableView().tableColumns()[0].setWidth_(501)
		self.w.methodList.getNSTableView().setToolTip_("Double click an entry to copy it to the clipboard and display its help() in Macro Window.")
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Method Reporter' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		self.MethodReporterMain(None)
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MethodReporter.filter"] = self.w.filter.get()
			Glyphs.defaults["com.mekkablue.MethodReporter.objectPicker"] = self.w.objectPicker.get()
		except:
			return False
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.MethodReporter.objectPicker", "GSLayer",)
			Glyphs.registerDefault("com.mekkablue.MethodReporter.filter", "")
			self.w.objectPicker.set( Glyphs.defaults["com.mekkablue.MethodReporter.objectPicker"] )
			self.w.filter.set( Glyphs.defaults["com.mekkablue.MethodReporter.filter"] )
		except:
			return False
		return True

	def copySelection( self, sender ):
		try:
			index = self.w.methodList.getSelection()[0]
			methodName = self.w.methodList[index]
			className = self.w.objectPicker.get()
			method = "%s.%s" % ( className, methodName )
			
			# help in macro window:
			self.outputHelpForMethod(method)
			
			# puts method in clipboard:
			if not setClipboard(method):
				print("Warning: could not set clipboard.")
			else:
				print("\n%s copied in clipboard, ready for pasting."%method)
				
		except Exception as e:
			Glyphs.showMacroWindow()
			import traceback
			print(traceback.format_exc())
	
	def outputHelpForMethod(self, method):
		# strip parentheses if necessary:
		if method.endswith("()"):
			method = method[:-2]
		
		# brings macro window to front, clears its log, outputs help for method:
		Glyphs.clearLog()
		helpStatement = "help(%s)" % method
		eval(helpStatement)
		Glyphs.showMacroWindow()
		
	def fullMethodName(self, className, methodName):
		"""
		Adds () if necessary.
		"""
		method = "%s.%s" % (className,methodName)
		methodType = type(eval(method))
		typeString = methodType.__name__
		if typeString != "property":
			methodName += "()"
		return methodName
	
	def methodList(self, className):
		elidableMethods = [method for method in dir(NSObject) if not method.startswith("__")]
		if className == "NSObject":
			return [
				self.fullMethodName(className,method) for method in elidableMethods 
				if not method.startswith(".")
			]
		else:
			try:
				actualClass = eval(className)
			except:
				newClassName = "NSClassFromString('%s')"%className
				actualClass = eval(newClassName)
				className = newClassName
				
			shortenedMethods = [
				self.fullMethodName(className,method) for method in dir(actualClass) 
				if not method in elidableMethods 
				and not method.startswith(".")
			]
			return shortenedMethods
			
	def MethodReporterMain( self, sender ):
		try:
			className = self.w.objectPicker.get()
			filterStringEntry = self.w.filter.get().strip()
			filterStrings = filterStringEntry.split(" ")
			
			try:
				methodList = sorted(set(self.methodList(className)))
				for filterString in filterStrings:
					if not "*" in filterString:
						methodList = [ f for f in methodList if filterString.lower() in f.lower() ]
					elif filterString.startswith("*"):
						methodList = [ f for f in methodList if f.lower().endswith(filterString.lower()[1:]) ]
					elif filterString.endswith("*"):
						methodList = [ f for f in methodList if f.lower().startswith(filterString.lower()[:-1]) ]
					else:
						asteriskPos = filterString.find("*")
						beginning = filterString[:asteriskPos].lower()
						ending = filterString[asteriskPos+1:].lower()
						methodList = [ f for f in methodList if f.lower().startswith(beginning) and f.lower().endswith(ending) ]
			except:
				methodList = []
			
			self.w.methodList.set(methodList)
			
			if not self.SavePreferences( self ):
				print("Note: 'Method Reporter' could not write preferences.")
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Method Reporter Error: %s" % e)

MethodReporter()