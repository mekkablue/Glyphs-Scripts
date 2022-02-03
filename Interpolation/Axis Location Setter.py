#MenuTitle: Axis Location Setter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Batch-set axis locations for all instances with a certain name particle. E.g., set an axis location for all Condensed instances.
"""

from Foundation import NSDictionary
import vanilla

def axisLocationEntry( axisName, locationValue ):
	return NSDictionary.alloc().initWithObjects_forKeys_(
		(axisName, locationValue),
		("Axis", "Location")
	)

class AxisLocationSetter( object ):
	prefID = "com.mekkablue.AxisLocationSetter"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 270
		windowHeight = 180
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Axis Location Setter", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 10, 12, 23
		self.w.descriptionText1 = vanilla.TextBox( (inset, linePos+2, -inset, 14), "In all masters/instances with name particle:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.particle = vanilla.ComboBox( (inset, linePos-1, -inset-25, 19), self.particlesOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences )
		self.w.particleUpdateButton = vanilla.SquareButton( (-inset-20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.update )
		linePos += lineHeight
		
		self.w.descriptionText2 = vanilla.TextBox( (inset, linePos+2, 50, 14), "For axis", sizeStyle='small', selectable=True )
		self.w.axisName = vanilla.PopUpButton( (inset+50, linePos, -100-inset, 17), self.axesOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences )
		self.w.descriptionText21 = vanilla.TextBox( (-100-inset, linePos+2, -inset, 14), ", set coordinates:", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.descriptionText3 = vanilla.TextBox( (inset, linePos+2, 50, 14), "Internal:", sizeStyle='small', selectable=True )
		self.w.internalAxisValue = vanilla.EditText( (inset+50, linePos-1, 45, 19), "0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.internalAxisValue.getNSTextField().setPlaceholderString_("no change")
		self.w.descriptionText31 = vanilla.TextBox( (inset+50+45, linePos+2, 95, 14), "→ External:", sizeStyle='small', selectable=True )
		self.w.externalAxisValue = vanilla.EditText( (-45-inset, linePos-1, -inset, 19), "0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.externalAxisValue.getNSTextField().setPlaceholderString_("no change")
		# record for resize:
		self.coordLinePos = linePos
		self.coordInset = inset
		linePos += lineHeight
		
		self.w.includeInstances = vanilla.CheckBox( (inset, linePos, 120, 20), "Apply to instances", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeMasters = vanilla.CheckBox( (inset+130, linePos, -inset, 20), "Apply to masters", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Set", sizeStyle='regular', callback=self.AxisLocationSetterMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ 'Axis Location Setter' could not load preferences. Will resort to defaults")
			self.updateUI()
		
		# Open window and focus on it:
		self.windowResize()
		self.w.bind("resize", self.windowResize)
		self.w.open()
		self.w.makeKey()
	
	def windowResize(self, sender=None):
		linePos = self.coordLinePos
		inset = self.coordInset
		left, top, width, height = self.w.getPosSize()
		textWidth = 60
		disposableWidth = width - 2*inset - textWidth -50 - 10
		fieldWidth = int(0.5*disposableWidth)
		
		self.w.internalAxisValue.setPosSize( (inset+50, linePos-1, fieldWidth, 19) )
		self.w.descriptionText31.setPosSize( (inset+50+fieldWidth+5, linePos+2, -fieldWidth-inset, 14) )
		self.w.externalAxisValue.setPosSize( (-fieldWidth-inset, linePos-1, -inset, 19) )
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def update(self, sender=None):
		self.w.particle.setItems( self.particlesOfCurrentFont() )
		self.w.axisName.setItems( self.axesOfCurrentFont() )
	
	def updateUI(self, sender=None):
		onOff = self.w.includeInstances.get() or self.w.includeMasters.get()
		onOff = onOff and bool(self.w.particle.get().strip())
		self.w.runButton.enable(onOff)
	
	def particlesOfCurrentFont(self, sender=None):
		particles = []
		currentFont = Glyphs.font
		if currentFont:
			for i in currentFont.instances:
				for particle in i.name.split(" "):
					if not particle in particles:
						particles.append(particle)
				if not i.name in particles:
					particles.append(i.name)
			particles.sort()
		return particles
	
	def axesOfCurrentFont(self, sender=None):
		axes = []
		currentFont = Glyphs.font
		if currentFont:
			for a in currentFont.axes:
				if not a.name in axes:
					axes.append(a.name)
		return axes
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("particle")] = self.w.particle.get()
			Glyphs.defaults[self.domain("axisName")] = self.w.axisName.getItem()
			Glyphs.defaults[self.domain("internalAxisValue")] = self.w.internalAxisValue.get()
			Glyphs.defaults[self.domain("externalAxisValue")] = self.w.externalAxisValue.get()
			Glyphs.defaults[self.domain("includeInstances")] = self.w.includeInstances.get()
			Glyphs.defaults[self.domain("includeMasters")] = self.w.includeMasters.get()
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("particle"), "Bold")
			Glyphs.registerDefault(self.domain("axisName"), "Weight")
			Glyphs.registerDefault(self.domain("internalAxisValue"), "")
			Glyphs.registerDefault(self.domain("externalAxisValue"), 0)
			Glyphs.registerDefault(self.domain("includeInstances"), False)
			Glyphs.registerDefault(self.domain("includeMasters"), False)
			
			# load previously written prefs:
			self.w.particle.set( self.pref("particle") )
			axisName = self.pref("axisName")
			axisNameIndex = max(0, self.w.axisName.getItems().index(axisName))
			self.w.axisName.set( axisNameIndex )
			self.w.internalAxisValue.set( self.pref("internalAxisValue") )
			self.w.externalAxisValue.set( self.pref("externalAxisValue") )
			self.w.includeInstances.set( self.pref("includeInstances") )
			self.w.includeMasters.set( self.pref("includeMasters") )
			
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False
	
	def setInternalCoordinate(self, thisInstance, thisAxisName, newAxisValue):
		theFont = thisInstance.font
		axisLocations = []
		for i,thisAxis in enumerate(theFont.axes):
			if thisAxis.name == thisAxisName:
				thisInstance.setAxisValueValue_forId_(newAxisValue, thisAxis.axisId)
				return True
		return False
		
	def setAxisLocationCoordinate( self, thisInstance, thisAxisName, newAxisValue ):
		paramName = "Axis Location"
		existingParameter = thisInstance.customParameters[paramName]
	
		theFont = thisInstance.font
		axisLocations = []
		for i,thisAxis in enumerate(theFont.axes):
			# determine the axis value:
			value = None
			if thisAxis.name == thisAxisName:
				# set the requested axis value:
				value = newAxisValue
			elif existingParameter:
				# preserve existing axis value:
				for entry in existingParameter:
					if thisAxis.name == entry["Axis"]:
						value = entry["Location"]
			if value==None:
				# otherwise replicate internal coordinate:
				if isinstance(thisInstance, GSFontMaster):
					value = thisInstance.axisValueValueForId_(thisAxis.axisId)
				else:
					value = thisInstance.coordinateForAxisIndex_(i)
			
			# add axis location entry:
			axisLocations.append( axisLocationEntry(thisAxis.name, value) )
		
		# add collected entries as axis location parameter:
		if axisLocations:
			thisInstance.customParameters[paramName] = tuple(axisLocations)
			return True
		
		return False
	
	def fontHasAxisWithName(self, font, axisName):
		for axis in font.axes:
			if axis.name == axisName:
				return True
		return False
	
	def particleIsPartOfName(self, particle, instanceName):
		# PROBLEM: finding particle "Bold Italic" (with whitespace) should not find "SemiBold Italic"
		delim = "🧙"
		modifiedInstanceName = delim.join(instanceName.split())
		modifiedParticle = delim.join(particle.split())
	
		# remove particle in the MIDDLE of the name:
		searchTerm = "%s%s%s" % (delim, modifiedParticle, delim)
		if searchTerm in modifiedInstanceName:
			return True
	
		# remove particle at the END of the name:
		searchTerm = "%s%s" % (delim, modifiedParticle)
		if modifiedInstanceName.endswith(searchTerm):
			return True
		
		# remove particle at the BEGINNING of the name:
		searchTerm = "%s%s" % (modifiedParticle, delim)
		if modifiedInstanceName.startswith(searchTerm):
			return True
		
		return False

	def AxisLocationSetterMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Axis Location Setter' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="Axis Location Setter requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Axis Location Setter Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				particle = self.pref("particle")
				axisName = self.pref("axisName")
				internalAxisValue = self.pref("internalAxisValue")
				externalAxisValue = self.pref("externalAxisValue")
				includeInstances = self.pref("includeInstances")
				includeMasters = self.pref("includeMasters")
				
				if not self.fontHasAxisWithName(thisFont, axisName):
					Message(
						title="Axis Location Setter Error",
						message="The frontmost font does not have an axis called ‘%s’." % axisName,
						OKButton=None
						)
					print("❌ Axis ‘%s’ not found." % axisName)
				else:	
					instanceCount = 0
					if includeInstances:
						for thisInstance in thisFont.instances:
							if self.particleIsPartOfName(particle, thisInstance.name):
								instanceCount += 1
								if externalAxisValue != "":
									if self.setAxisLocationCoordinate( thisInstance, axisName, externalAxisValue ):
										print("ℹ️ EXTERNAL %s = %s in %s" % (axisName, externalAxisValue, thisInstance.name))
								if internalAxisValue != "":
									if self.setInternalCoordinate( thisInstance.name, axisName, internalAxisValue ):
										print("ℹ️ INTERNAL %s = %s in %s" % (axisName, internalAxisValue, thisInstance.name))

					masterCount = 0
					if includeMasters:
						for thisMaster in thisFont.masters:
							if self.particleIsPartOfName(particle, thisMaster.name):
								masterCount += 1
								if externalAxisValue != "":
									if self.setAxisLocationCoordinate( thisMaster, axisName, externalAxisValue ):
										print("Ⓜ️ EXTERNAL %s = %s in %s" % (axisName, externalAxisValue, thisMaster.name))
								if internalAxisValue != "":
									if self.setInternalCoordinate( thisMaster.name, axisName, internalAxisValue ):
										print("Ⓜ️ INTERNAL %s = %s in %s" % (axisName, internalAxisValue, thisMaster.name))

					# Final report:
					message = "Coordinates updated in %i instances and %i masters. Details in Macro Window" % (instanceCount, masterCount)
					print("\n%s" % message)
					Glyphs.showNotification( 
						"%s: Done" % (thisFont.familyName),
						message,
						)

				print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Axis Location Setter Error: %s" % e)
			import traceback
			print(traceback.format_exc())

if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	AxisLocationSetter()	
else:
	# GLYPHS 2
	Message(title="Axis Location Setter Error", message="This script requires at least Glyphs 3. Sorry.", OKButton=None)

