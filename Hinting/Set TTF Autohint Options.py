#MenuTitle: Set TTF Autohint Options
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__="""
Set options for existing 'TTF Autohint Options' Custom Parameters.
"""

import vanilla
from Foundation import NSPoint

parameterName = "TTFAutohint options"
# availableOptions = ("adjust-subglyphs", "composites", "default-script", "dehint", "detailed-info", "fallback-script", "fallback-stem-width", "hinting-limit", "hinting-range-max", "hinting-range-min", "ignore-restrictions", "increase-x-height", "no-info", "stem-width-mode", "strong-stem-width", "symbol", "ttfa-table", "windows-compatibility", "x-height-snapping-exceptions")
valuelessOptions = ("windows-compatibility", "adjust-subglyphs", "detailed-info", "ignore-restrictions", "ttfa-table", "composites", "symbol", "dehint", "no-info")
availableOptionsDict = {
	"adjust-subglyphs": "adjust-subglyphs",
	"composites": "hint-composites",
	"default-script": "default-script",
	"dehint": "dehint",
	"detailed-info": "ttfautohint-info",
	"fallback-script": "fallback-script",
	"fallback-stem-width": "fallback-stem-width",
	"hinting-limit": "hinting-limit",
	"hinting-range-max": "hint-set-range-minimum-hint-set-range-maximum",
	"hinting-range-min": "hint-set-range-minimum-hint-set-range-maximum",
	"ignore-restrictions": "miscellaneous",
	"increase-x-height": "x-height-increase-limit",
	"no-info": "ttfautohint-info",
	"stem-width-mode": "stem-width-and-positioning-mode",
	"strong-stem-width": "stem-width-and-positioning-mode",
	"symbol": "symbol-font",
	"ttfa-table": "add-ttfa-info-table",
	"windows-compatibility": "windows-compatibility",
	"x-height-snapping-exceptions": "x-height-snapping-exceptions",
}

availableOptions = sorted(availableOptionsDict.keys())

def removeFromAutohintOptions( thisInstance, removeOption ):
	parameter = thisInstance.customParameters[parameterName]
	if parameter:
		ttfAutohintOptions = parameter.split(u" ")
		popList = []
		optionToBeRemoved = "--%s" % removeOption.strip()
		for i, currentOption in enumerate(ttfAutohintOptions):
			if currentOption.split(u"=")[0] == optionToBeRemoved:
				popList.append(i)
		if popList:
			for j in sorted( popList )[::-1]:
				ttfAutohintOptions.pop(j)
			thisInstance.customParameters[parameterName] = " ".join(ttfAutohintOptions)
		else:
			print("-- Warning: '%s' not found." % removeOption)

def dictToParameterValue( ttfAutohintDict ):
	parameterValue = ""
	for key in ttfAutohintDict:
		parameterValue += " "
		if not ttfAutohintDict[key]:
			parameterValue += "--%s" % key.strip(" -")
		else:
			value = str(ttfAutohintDict[key]).strip()
			parameterValue += "--%s=%s" % ( key.strip(" -"), value )
	return parameterValue.strip()

def ttfAutohintDict( parameterValue ):
	"""Returns a dict for a TTFAutohint parameter value."""
	ttfAutohintDict = {}
	for ttfAutohintOption in parameterValue.split("--"):
		if "=" in ttfAutohintOption:
			[key, value] = ttfAutohintOption.split("=")
			value = value.strip()
		else:
			key = ttfAutohintOption
			value = None
		if key:
			ttfAutohintDict[key.strip(" -")] = value
	return ttfAutohintDict

def glyphInterpolation( thisGlyph, thisInstance ):
	try:
		interpolatedFont = thisInstance.pyobjc_instanceMethods.interpolatedFont()
		interGlyph = interpolatedFont.glyphForName_(thisGlyph.name)
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			interpolatedLayer = interGlyph.layer0()
		else:
			# GLYPHS 2
			interpolatedLayer = interGlyph.layerForKey_(interpolatedFont.fontMasterID())
		
		thisFont = thisGlyph.parent
		if not thisInstance.customParameters["Grid Spacing"] and not ( thisFont.gridMain() / thisFont.gridSubDivision() ):
			interpolatedLayer.roundCoordinates()
		if len( interpolatedLayer.paths ) != 0:
			return interpolatedLayer
		else:
			return None
	except Exception as e:
		import traceback
		print(traceback.format_exc())
		return None

def idotlessMeasure(instance):
	thisFont = instance.font
	idotless = thisFont.glyphs["idotless"]
	idotlessLayer = glyphInterpolation( idotless, instance )
	if idotlessLayer:
		measureHeight = idotlessLayer.bounds.size.height * 0.5
		measureStartX = idotlessLayer.bounds.origin.x - 10
		measureEndX   = measureStartX + idotlessLayer.bounds.size.width + 20
		measureStart = NSPoint( measureStartX, measureHeight )
		measureEnd   = NSPoint( measureEndX, measureHeight )
		intersections = idotlessLayer.intersectionsBetweenPoints( measureStart, measureEnd, components=True )
		if not len(intersections)>2:
			return None
		else:
			firstIntersection = intersections[1]
			lastIntersection = intersections[-2]
			idotlessWidth = lastIntersection.x - firstIntersection.x
			return idotlessWidth
	else:
		return None
	
def writeOptionsToInstance( optionDict, instance ):
	value = dictToParameterValue(optionDict)
	try:
		if Glyphs.versionNumber >= 3:
			# GLYPHS 3
			instanceWeightValue = instance.axes[0]
		else:
			# GLYPHS 2
			instanceWeightValue = instance.weightValue
	except Exception as e:
		instanceWeightValue = None
		print("⚠️ Error determining the instance weight value:\n%s"%e)
		import traceback
		print(traceback.format_exc())
	
	if not instanceWeightValue is None:
		value = value.replace( "--fallback-stem-width=*", "--fallback-stem-width=%i"%instanceWeightValue )
	
	if "fallback-stem-width=idotless" in value:
		actualStemWidth = idotlessMeasure(instance)
		if actualStemWidth:
			value = value.replace( "--fallback-stem-width=idotless", "--fallback-stem-width=%i"%actualStemWidth )
		else:
			print("Warning: Could not measure stem width of idotless in instance '%s'." % instance.name)
			return # do nothing
	instance.customParameters[parameterName] = value

class SetTTFAutohintOptions( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 470
		windowHeight = 110
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Set in All TTF Autohint Options", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SetTTFAutohintOptions.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.helpButton = vanilla.HelpButton((13, 12, 21, 20), callback=self.openURL)
		self.w.helpButton.getNSButton().setToolTip_("Opens the ttfAutohint documentation for the currently selected option on freetype.org.")
		
		self.w.ttfAutohintOption = vanilla.PopUpButton( (38, 13, 175, 17), availableOptions, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ttfAutohintOption.getNSPopUpButton().setToolTip_("Available ttfAutohint options. Pick one from the list. Careful: also contains deprecated options. Refer to the documentation (click on the Help Button on the left), know what you are doing.")
		
		self.w.optionValue = vanilla.EditText( (220, 12, -67-50, 20), "value", callback=self.SavePreferences, sizeStyle = 'small')
		self.w.optionValue.getNSTextField().setToolTip_("Value for the currently selected option, if any. Some options can only be set or removed, some have a value.")
		
		self.w.explanation = vanilla.TextBox( (15-1, 40, -5, -5), "Adds or sets this option in all TTF Autohint Options parameters in the current font. For fallback-stem-width, use * for entering the respective instance weight value, and idotless for measuring the width of the interpolated dotless i. The Del button removes this TTFA option from all instances.", sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-60-50, 10, -15-50, 22), "Set", sizeStyle='regular', callback=self.SetTTFAutohintOptionsMain )
		self.w.runButton.getNSButton().setToolTip_("Updates all TTF Autohint Options parameters with the current option (and value, if any) to all instances in the font.")
		
		self.w.delButton = vanilla.Button((-60, 10, -15, 22), "Del", sizeStyle='regular', callback=self.RemoveOption )
		self.w.delButton.getNSButton().setToolTip_("Removes the current option from all TTF Autohint Options parameters in all instances in the font.")

		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Set TTF Autohint Options' could not load preferences. Will resort to defaults")
		
		# enable or disable the edit box
		self.editValueField()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def openURL( self, sender ):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://www.freetype.org/ttfautohint/doc/ttfautohint.html"
			currentlySelectedOption = self.w.ttfAutohintOption.getItem()
			if currentlySelectedOption in availableOptionsDict.keys():
				urlExtension = availableOptionsDict[currentlySelectedOption]
				if urlExtension:
					URL = "%s#%s" % ( URL, urlExtension )
		if URL:
			import webbrowser
			webbrowser.open( URL )
	
	def editValueField(self):
		optionName = self.currentOptionName()
		if optionName in valuelessOptions:
			self.w.optionValue.enable(onOff=False)
			self.w.optionValue.set( "" )
		else:
			self.w.optionValue.enable(onOff=True)
			ttfAutohintOption = "com.mekkablue.SetTTFAutohintOptions.%s" % optionName
			self.w.optionValue.set( Glyphs.defaults[ttfAutohintOption] )
		
	def currentOptionName(self):
		optionIndex = Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"]
		if optionIndex is None:
			optionIndex = 0
			Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"] = 0
		optionName = availableOptions[int(optionIndex)]
		return optionName
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"] = self.w.ttfAutohintOption.get()
			Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.optionValue"] = self.w.optionValue.get()
		except:
			return False
		
		if sender==self.w.ttfAutohintOption:
			# picked an option from the pop-up, populate value field:
			self.editValueField()
		else:
			# store entered value in prefs:
			ttfAutohintOption = "com.mekkablue.SetTTFAutohintOptions.%s" % self.currentOptionName()
			Glyphs.defaults[ttfAutohintOption] = self.w.optionValue.get()
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.SetTTFAutohintOptions.optionValue": "",
					"com.mekkablue.SetTTFAutohintOptions.adjust-subglyphs": "",
					"com.mekkablue.SetTTFAutohintOptions.composites": "",
					"com.mekkablue.SetTTFAutohintOptions.default-script": "latn",
					"com.mekkablue.SetTTFAutohintOptions.dehint": "",
					"com.mekkablue.SetTTFAutohintOptions.detailed-info": "",
					"com.mekkablue.SetTTFAutohintOptions.fallback-script": "latn",
					"com.mekkablue.SetTTFAutohintOptions.fallback-stem-width": "*",
					"com.mekkablue.SetTTFAutohintOptions.hinting-limit": "48",
					"com.mekkablue.SetTTFAutohintOptions.hinting-range-max": "36",
					"com.mekkablue.SetTTFAutohintOptions.hinting-range-min": "",
					"com.mekkablue.SetTTFAutohintOptions.ignore-restrictions": "",
					"com.mekkablue.SetTTFAutohintOptions.increase-x-height": "",
					"com.mekkablue.SetTTFAutohintOptions.no-info": "",
					"com.mekkablue.SetTTFAutohintOptions.strong-stem-width": "gG",
					"com.mekkablue.SetTTFAutohintOptions.stem-width-mode": "qss",
					"com.mekkablue.SetTTFAutohintOptions.symbol": "",
					"com.mekkablue.SetTTFAutohintOptions.ttfa-table": "",
					"com.mekkablue.SetTTFAutohintOptions.windows-compatibility": "",
					"com.mekkablue.SetTTFAutohintOptions.x-height-snapping-exceptions": "",
					"com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption": 0,
				}
			)
			self.w.ttfAutohintOption.set( Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"] )
		except:
			return False
			
		return True
	
	def RemoveOption(self, sender):
		try:
			optionIndex = int(Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"])
			optionName = availableOptions[optionIndex]
			for thisInstance in Glyphs.font.instances:
				if thisInstance.customParameters[parameterName]:
					removeFromAutohintOptions( thisInstance, optionName )
					print("Removing %s from instance '%s'." % (
						optionName,
						thisInstance.name,
					))
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set TTF Autohint Options Error: %s" % e)
			import traceback
			print(traceback.format_exc())
		
	
	def SetTTFAutohintOptionsMain( self, sender ):
		try:
			if not self.SavePreferences( self ):
				print("Note: 'Set TTF Autohint Options' could not write preferences.")
			
			optionIndex = int(Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.ttfAutohintOption"])
			optionName = availableOptions[optionIndex]
			enteredValue = Glyphs.defaults["com.mekkablue.SetTTFAutohintOptions.%s"%optionName]
			
			firstDoc = Glyphs.orderedDocuments()[0]
			if firstDoc.isKindOfClass_(GSProjectDocument):
				# Frontmost doc is a .glyphsproject file:
				thisFont = firstDoc.font() # frontmost project file
				instances = firstDoc.instances()
			else:
				# Frontmost doc is a .glyphs file:
				thisFont = Glyphs.font # frontmost font
				instances = thisFont.instances
			
			if enteredValue != "" or optionName in valuelessOptions:
				for thisInstance in instances:
					if not thisInstance.customParameters[parameterName] is None:
						optionDict = ttfAutohintDict( thisInstance.customParameters[parameterName] )
						optionDict[ optionName ] = enteredValue
						writeOptionsToInstance( optionDict, thisInstance )
						print("Set %s in instance '%s'." % (
							optionName,
							thisInstance.name,
						))
					else:
						print("No TTF Autohint parameter in instance '%s'. %s not set." % (
							thisInstance.name,
							optionName,
						))
			else:
				Message("Script Error", "Illegal value entered.", OKButton=None)
			
			# self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set TTF Autohint Options Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SetTTFAutohintOptions()