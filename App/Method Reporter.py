#MenuTitle: Method Reporter
# -*- coding: utf-8 -*-
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
		print e
		return False

class MethodReporter( object ):
	def __init__( self ):
		self.mostImportantObjects = (
			"GSLayer",
			"GSAlignmentZone",
			"GSAnchor",
			"GSAnnotation",
			"GSApplication",
			"GSBackgroundImage",
			"GSClass",
			"GSComponent",
			"GSCustomParameter",
			"GSEditViewController",
			"GSGlyphEditView",
			"GSFeature",
			"GSFeaturePrefix",
			"GSFont",
			"GSFontMaster",
			"GSGlyph",
			"GSGlyphInfo",
			"GSGlyphsInfo",
			"GSGuideLine",
			"GSHint",
			"GSInstance",
			"GSNode",
			"GSPath",
			"GSPathSegment",
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
			"FTPointArray",
			"Glyph_g_l_y_f",
			"GSProjectDocument",
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
			(10, 10, 120, 19),
			self.mostImportantObjects,
			sizeStyle='small',
			completes=True,
			continuous=False,
			callback=self.MethodReporterMain
		)
		self.w.objectPicker.set("GSLayer")
		self.w.objectPicker.getNSComboBox().setToolTip_("Type a class name here. Names will autocomplete.")
		
		# Filter:
		self.w.text2 = vanilla.TextBox(
			(140, 13, 35, 14),
			"Filter:",
			sizeStyle='small'
		)
		self.w.filter = vanilla.EditText(
			(180, 10, -10, 19 ),
			"",
			sizeStyle='small',
			callback=self.MethodReporterMain
		)
		self.w.filter.getNSTextField().setToolTip_("Type one or more search terms here. Case is ignored. Use * as wildcard at beginning, middle or end of term. Multiple search terms are AND concatendated.")
		
		# Listing of methods:
		self.w.methodList = vanilla.List(
			(0, 40, -0, -0),
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
			print "Note: 'Method Reporter' could not load preferences. Will resort to defaults"
		
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
			methodname = self.w.methodList[index]
			classname = self.w.objectPicker.get()
			method = "%s.%s"%(classname,methodname)
			
			# brings macro window to front, clears its log, outputs help for method:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()
			eval("help(%s)"%method)
			
			# puts method in clipboard:
			if not setClipboard(method):
				print "Warning: could not set clipboard."
		except Exception as e:
			Glyphs.showMacroWindow()
			print "Method Reporter Error:\nCould not copy to clipboard.\n%s" % e
	
	def methodList(self, className):
		elidableMethods = dir(NSObject)
		if className == "NSObject":
			return elidableMethods
		else:
			shortenedMethods = [method for method in dir(eval(className)) if not method in elidableMethods and not method.startswith(".")]
			return shortenedMethods
			
	def MethodReporterMain( self, sender ):
		try:
			className = self.w.objectPicker.get()
			filterStringEntry = self.w.filter.get().strip()
			filterStrings = filterStringEntry.split(" ")
			
			try:
				methodList = self.methodList(className)
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
				print "Note: 'Method Reporter' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Method Reporter Error: %s" % e

MethodReporter()