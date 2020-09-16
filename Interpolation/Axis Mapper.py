#MenuTitle: Axis Mapper
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Extracts, resets and inserts an ‘avar’ axis mapping for the Axis Mappings parameter.
"""

import vanilla
from axisMethods import *
from AppKit import NSFont
from Foundation import NSMutableDictionary

fallbackText = """
Only lines containing a dash "-" followed by a greater sign ">" are interpreted
Write comments freely, anything after a hashtag "#" will always be ignored
# SYNTAX: slider value the user *sees* -> slider value the user *gets*
"""

class AxisMapper( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 380
		windowHeight = 160
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 600 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Axis Mapper", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AxisMapper.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 4, 10, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), "Axis Mapping from user-visible (not native) values:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.axisPicker = vanilla.ComboBox( (inset, linePos-1, 60, 20), self.AxisListForFrontmostFont(), callback=self.SavePreferences, sizeStyle='small' )
		self.w.axisPicker.getNSComboBox().setToolTip_("Pick or type the 4-letter tag of the axis for which you want to edit the mapping.")
		self.w.axisReset = vanilla.SquareButton( (inset+65, linePos, 20, 18), "↺", sizeStyle='small', callback=self.resetAxisList )
		self.w.axisReset.getNSButton().setToolTip_("Will populate the axis picker with the tags for all axes in the frontmost font.")
		
		self.w.minText = vanilla.TextBox( (inset+100, linePos+2, 55, 14), "Axis Min:", sizeStyle='small', selectable=True )
		self.w.minValue = vanilla.EditText( (inset+100+55, linePos-1, 40, 19), self.MinimumForCurrentAxis(), callback=self.SavePreferences, sizeStyle='small' )
		tooltipText = "User-visible slider minimum, typically set with an Axis Location parameter. Not (necessarily) the native master value."
		self.w.minText.getNSTextField().setToolTip_(tooltipText)
		self.w.minValue.getNSTextField().setToolTip_(tooltipText)
		self.w.minValueReset = vanilla.SquareButton( (inset+100+60+40, linePos, 20, 18), "↺", sizeStyle='small', callback=self.resetMinimum )
		self.w.minValueReset.getNSButton().setToolTip_("Will attempt to guess the user-visible slider minimum of the frontmost font.")
		
		
		self.w.maxText = vanilla.TextBox( (inset+230, linePos+2, 55, 14), "Axis Max:", sizeStyle='small', selectable=True )
		self.w.maxValue = vanilla.EditText( (inset+230+55, linePos-1, 40, 19), self.MaximumForCurrentAxis(), callback=self.SavePreferences, sizeStyle='small' )
		tooltipText = "User-visible slider maximum, typically set with an Axis Location parameter. Not (necessarily) the native master value."
		self.w.maxText.getNSTextField().setToolTip_(tooltipText)
		self.w.maxValue.getNSTextField().setToolTip_(tooltipText)
		self.w.maxValueReset = vanilla.SquareButton( (inset+230+60+40, linePos, 20, 18), "↺", sizeStyle='small', callback=self.resetMaximum )
		self.w.maxValueReset.getNSButton().setToolTip_("Will attempt to guess the user-visible slider maximum of the frontmost font.")
		linePos += lineHeight
		
		self.w.mappingRecipe = vanilla.TextEditor( (0, linePos, -0, -20-inset*2), text=fallbackText.strip(), callback=self.SavePreferences, checksSpelling=False )
		legibleFont = NSFont.legibileFontOfSize_(NSFont.systemFontSize())
		textView = self.w.mappingRecipe.getNSTextView()
		textView.setFont_(legibleFont)
		
		# Buttons:
		self.w.recipeButton = vanilla.Button( (inset, -20-inset, 120, -inset), "Reset Recipe", sizeStyle='regular', callback=self.ResetRecipe )
		self.w.recipeButton.getNSButton().setToolTip_("Construct a fallback axis mapping recipe for axis and the min/max values above, based on the existing active instances. Can be a good start for creating new mappings. Respects the weightClass settings for the 'wght' axis.")

		self.w.extractButton = vanilla.Button( (inset+130, -20-inset, 120, -inset), "Extract Recipe", sizeStyle='regular', callback=self.ExtractAxisMapping )
		self.w.extractButton.getNSButton().setToolTip_("Extract the axis mapping recipe for the chosen axis from an existing Axis Mappings parameter, and into the min/max values specified above. Will do nothing if it fails. Great for editing existing mappings.")
		
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Map", sizeStyle='regular', callback=self.AxisMapperMain )
		self.w.runButton.getNSButton().setToolTip_("Write the current mapping recipe into an Axis Mappings parameter for the frontmost font.")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Axis Mapper' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def AxisListForFrontmostFont(self, sender=None):
		thisFont = Glyphs.font
		if thisFont:
			axes = thisFont.axes
			if axes:
				return [a.axisTag for a in axes]
		return ()
	
	def allMasterValuesForAxisTag(self, sender=None, axisTag="wght"):
		collectedValues = []
		thisFont = Glyphs.font
		if thisFont:
			axes = thisFont.axes
			if axes:
				for axis in axes:
					if axis.axisTag == axisTag:
						collectedValues = []
						for master in thisFont.masters:
							axisLocationParameter = master.customParameters["Axis Location"]
							axisValue = None
							
							# prefer axis location parameter
							if axisLocationParameter:
								for location in axisLocationParameter:
									if location.objectForKey_("Axis") == axis.name:
										axisValue = location.objectForKey_("Location")
							
							# default to native value if there is no axis location parameter:
							if axisValue is None:
								axisValue = masterValueForAxisTag(master,axisTag=axisTag)
							
							if not axisValue is None:
								collectedValues.append(float(axisValue))
							
						return collectedValues

		return collectedValues
	
	def MinimumForCurrentAxis(self, sender=None):
		currentAxisTag = self.w.axisPicker.get()
		if currentAxisTag:
			values = self.allMasterValuesForAxisTag(axisTag=currentAxisTag)
			if values:
				return min(values)
		return 0 # fallback value

	def MaximumForCurrentAxis(self, sender=None):
		currentAxisTag = self.w.axisPicker.get()
		if currentAxisTag:
			values = self.allMasterValuesForAxisTag(axisTag=currentAxisTag)
			if values:
				return max(values)
		return 100 # fallback value
	
	def resetMinimum(self, sender=None):
		value = self.MinimumForCurrentAxis()
		self.w.minValue.set(value)

	def resetMaximum(self, sender=None):
		value = self.MaximumForCurrentAxis()
		self.w.maxValue.set(value)
	
	def resetAxisList(self, sender=None):
		axisList = self.AxisListForFrontmostFont()
		self.w.axisPicker.setItems(axisList)
		if axisList:
			self.w.axisPicker.set(axisList[0])
	
	def ResetRecipe(self, sender=None):
		text = ""
		font = Glyphs.font
		axisTag = self.w.axisPicker.get()
		if font and axisTag:
			nativeMasterMin, nativeMasterMax = extremeMasterValuesNative(font, axisTag=axisTag)
			nativeStyleMin, nativeStyleMax = extremeStyleValuesNative(font, axisTag=axisTag)
			
			userMasterMin, userMasterMax = float(self.w.minValue.get()), float(self.w.maxValue.get())
			
			mappingDict = {
				userMasterMin: "%i -> %i # Min" % (userMasterMin, userMasterMin),
				userMasterMax: "%i -> %i # Max" % (userMasterMax, userMasterMax),
			}
			
			for style in font.instances:
				if style.active:
					nativeValue = styleValueForAxisTag(style, axisTag=axisTag)
					coeff = coefficient(nativeValue, nativeMasterMin, nativeMasterMax)
					trueSliderValue = valueForCoefficient(coeff, userMasterMin, userMasterMax)
					visibleSliderValue = trueSliderValue
					
					# better guess for weight axis:
					if axisTag=="wght":
						weightClass = style.weightClassValue()
						if userMasterMin <= weightClass <= userMasterMax:
							visibleSliderValue = weightClass
					
					mappingDict[visibleSliderValue] = "%i -> %i # %s" % (visibleSliderValue, trueSliderValue, style.name)
			
			for mappingValue in sorted(mappingDict.keys()):
				line = mappingDict[mappingValue]
				text += line
				text += "\n"
				
		text += "\n"
		text += "\nBased on "
		if font.filepath:
			text += "%s\n" % font.filepath.lastPathComponent()
		else:
			text += "%s (unsaved file)\n" % font.familyName
		text += fallbackText
		self.w.mappingRecipe.set(text.strip())
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults["com.mekkablue.AxisMapper.minValue"] = self.w.minValue.get()
			Glyphs.defaults["com.mekkablue.AxisMapper.maxValue"] = self.w.maxValue.get()
			Glyphs.defaults["com.mekkablue.AxisMapper.axisPicker"] = self.w.axisPicker.get()
			Glyphs.defaults["com.mekkablue.AxisMapper.mappingRecipe"] = self.w.mappingRecipe.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault("com.mekkablue.AxisMapper.minValue", 0)
			Glyphs.registerDefault("com.mekkablue.AxisMapper.maxValue", 100)
			Glyphs.registerDefault("com.mekkablue.AxisMapper.axisPicker", "wght")
			Glyphs.registerDefault("com.mekkablue.AxisMapper.mappingRecipe", fallbackText)
			
			# load previously written prefs:
			self.w.minValue.set( Glyphs.defaults["com.mekkablue.AxisMapper.minValue"] )
			self.w.maxValue.set( Glyphs.defaults["com.mekkablue.AxisMapper.maxValue"] )
			self.w.axisPicker.set( Glyphs.defaults["com.mekkablue.AxisMapper.axisPicker"] )
			self.w.mappingRecipe.set( Glyphs.defaults["com.mekkablue.AxisMapper.mappingRecipe"] )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def ExtractAxisMapping(self, sender=None):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Axis Mapper' could not write preferences.")
			
			text = ""
			axisTag = Glyphs.defaults["com.mekkablue.AxisMapper.axisPicker"]
			thisFont = Glyphs.font # frontmost font
			if thisFont:
				mappings = thisFont.customParameters["Axis Mappings"]
				if mappings:
					axisMapping = mappings.objectForKey_(axisTag)
					if axisMapping:
						minValue = float(Glyphs.defaults["com.mekkablue.AxisMapper.minValue"])
						maxValue = float(Glyphs.defaults["com.mekkablue.AxisMapper.maxValue"])
						minValueNative, maxValueNative = extremeMasterValuesNative(thisFont,axisTag=axisTag)
						for nativeUserValue in sorted(axisMapping.allKeys()):
							nativeTargetValue = axisMapping.objectForKey_(nativeUserValue)
							
							# user value:
							coeff = coefficient(nativeUserValue, minValueNative, maxValueNative)
							userValue = valueForCoefficient(coeff, minValue, maxValue)
							
							# target value:
							coeff = coefficient(nativeTargetValue, minValueNative, maxValueNative)
							targetValue = valueForCoefficient(coeff, minValue, maxValue)
							
							text += "%g -> %g # native: %i -> %i\n" % (userValue, targetValue, nativeUserValue, nativeTargetValue)
			if text:
				text += "\nBased on "
				if thisFont.filepath:
					text += "%s\n" % thisFont.filepath.lastPathComponent()
				else:
					text += "%s (unsaved file)\n" % thisFont.familyName
				text += "Range translated: %i-%i → %i-%i:\n" % (minValueNative, maxValueNative, minValue, maxValue)
				text += fallbackText
				Glyphs.defaults["com.mekkablue.AxisMapper.mappingRecipe"] = text.strip()
				self.LoadPreferences()
		except Exception as e:
			raise e
	
	def AxisMapperMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Axis Mapper' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Axis Mapper Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				minValue = float(Glyphs.defaults["com.mekkablue.AxisMapper.minValue"])
				maxValue = float(Glyphs.defaults["com.mekkablue.AxisMapper.maxValue"])
				mappingRecipe = Glyphs.defaults["com.mekkablue.AxisMapper.mappingRecipe"]
				axisTag = Glyphs.defaults["com.mekkablue.AxisMapper.axisPicker"]
				
				print("🔠 Building Mapping for: %s"%axisTag)
				
				axisMapping = NSMutableDictionary.alloc().init()
				
				# axis extremes must be there:
				nativeLow, nativeHigh = extremeMasterValuesNative(thisFont,axisTag=axisTag)
				for masterExtreme in (nativeLow, nativeHigh):
					axisMapping.addObject_forKey_( masterExtreme, masterExtreme )
				print("✅ Added axis extremes to mapping: %i→%i, %i→%i"%(nativeLow,nativeLow, nativeHigh,nativeHigh))
				
				
				# process line
				for line in mappingRecipe.splitlines():
					if "#" in line:
						line = line[:line.find("#")]
					if "->" in line:
						line = line.strip()
						userValue, targetValue = [float(v.strip()) for v in line.split("->")]
						userCoeff = coefficient(userValue,minValue,maxValue)
						targetCoeff = coefficient(targetValue,minValue,maxValue)
						nativeUserValue = valueForCoefficient(userCoeff,nativeLow,nativeHigh)
						nativeTargetValue = valueForCoefficient(targetCoeff,nativeLow,nativeHigh)
						axisMapping.addObject_forKey_(nativeTargetValue,nativeUserValue)
						print("✅ Translating %i→%i to %i→%i"%(userValue, targetValue, nativeUserValue, nativeTargetValue))
				
				parameterName = "Axis Mappings"
				mappings = Font.customParameters[parameterName]
				if not mappings:
					print("🙌 Adding new %s parameter"%parameterName)
					mappings = NSMutableDictionary.alloc().initWithObject_forKey_(axisMapping, "wght")
					mappings.addObject_forKey_( axisMapping, axisTag )
				else:
					print("🧩 Inserting %s mapping into existing %s parameter"%(axisTag,parameterName))
					mappings.setObject_forKey_( axisMapping, axisTag )
				thisFont.customParameters[parameterName] = mappings
	
			# Final report:
			Glyphs.showNotification( 
				"‘%s’ mapping for %s" % (axisTag, thisFont.familyName),
				"Inserted ‘%s’ mapping with %i entries. Details in Macro Window" % (axisTag, len(axisMapping.allKeys())),
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Axis Mapper Error: %s" % e)
			import traceback
			print(traceback.format_exc())

if Glyphs.versionNumber < 3.0:
	Message(title="Glyphs Version Error", message="This script requires GLyphs 3.0 or later.", OKButton=None)
else:
	AxisMapper()