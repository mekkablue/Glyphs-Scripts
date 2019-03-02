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
		self.mostImportantObjects = [
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
		]
		
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
		
		# Listing of methods:
		self.w.methodList = vanilla.List(
			(0, 40, -0, -0),
			dir(GSLayer),
			autohidesScrollers=False,
			drawVerticalLines=True,
			doubleClickCallback=self.copySelection,
			rowHeight=19,
		)
		self.w.methodList.getNSTableView().tableColumns()[0].setWidth_(501)
		
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
			
	def MethodReporterMain( self, sender ):
		try:
			className = self.w.objectPicker.get()
			filterString = self.w.filter.get()
				
			try:
				if not "*" in filterString:
					methodList = [ f for f in dir(eval(className)) if filterString.lower() in f.lower() ]
				elif filterString[0] == "*":
					methodList = [ f for f in dir(eval(className)) if f.lower().endswith(filterString.lower().replace("*","")) ]
				elif filterString.endswith("*"):
					methodList = [ f for f in dir(eval(className)) if f.lower().startswith(filterString.lower().replace("*","")) ]
			except Exception as e:
				methodList = []
			
			self.w.methodList.set(methodList)
			
			if not self.SavePreferences( self ):
				print "Note: 'Method Reporter' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Method Reporter Error: %s" % e

MethodReporter()