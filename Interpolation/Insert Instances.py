#MenuTitle: Insert Instances
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Inserts instances, based on the Luc(as), Pablo, and Maciej algorithms.
"""

from GlyphsApp import *
from Foundation import NSDictionary
import vanilla

rangemin = 3
rangemax = 11

naturalNames = (
	"Hairline",
	"Thin",
	"Extralight",
	"Light",
	"Regular",
	"Medium",
	"Semibold",
	"Bold",
	"Extrabold",
	"Black",
	"Extrablack",
)

weightClasses = {
	"Hairline":1,
	"Thin":100,
	"Extralight":200,
	"Light":300,
	"Regular":400,
	"Medium":500,
	"Semibold":600,
	"Bold":700,
	"Extrabold":800,
	"Black":900,
	"Extrablack":1000,
}

weightClassesOldNames = {
	"Hairline":"Thin:1",
	"Thin":"Thin",
	"Extralight":"ExtraLight",
	"Light":"Light",
	"Regular":"Regular",
	"Medium":"Medium",
	"Semibold":"SemiBold",
	"Bold":"Bold",
	"Extrabold":"ExtraBold",
	"Black":"Black",
	"Extrablack":"Black:1000",
}


def distribute_lucas( min, max, n ):
	if min==0:
		min=max/1000.0
	q = max / min
	return [ min * q**(i/(n-1)) for i in range(n) ]

def distribute_reverselucas( min, max, n ):
	if min==0:
		min=max/1000.0
	q = max / min
	return [ min + max - min * q**(i/(n-1)) for i in range(n-1,-1,-1) ]
 
def distribute_equal( min, max, n ):
	d = (max - min) / (n-1)
	return [ min + i*d for i in range(n) ]
 
def distribute_pablo( min, max, n ):
	es = distribute_equal(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [ l*(1-i/(n-1)) + e*(i/(n-1)) for (i, e, l) in zip(range(n), es, ls) ]

def distribute_schneider( min, max, n ):
	ps = distribute_pablo(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [ (p+l)*0.5 for (p, l) in zip(ps, ls) ]

def distribute_abraham( min, max, n ):
	es = distribute_equal(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [ e*(1-(i/(n-1))**1.25) + l*(i/(n-1))**1.25 for (i, e, l) in zip(range(n), es, ls) ]

def distribute_maciej( lightMasterWeightX, lightMasterWeightY, boldMasterWeightX, boldMasterWeightY, interpolationWeightX ):
	"""
	Algorithm by Maciej Ratajski
	http://jsfiddle.net/Dm2Zk/1/
	"""
	interpolationPointX =  ( interpolationWeightX - lightMasterWeightX ) / ( boldMasterWeightX - lightMasterWeightX )
	interpolationWeightY = ( ( 1 - interpolationPointX ) * ( lightMasterWeightY / lightMasterWeightX - boldMasterWeightY / boldMasterWeightX ) + boldMasterWeightY / boldMasterWeightX ) * interpolationWeightX
	interpolationPointY =  ( interpolationWeightY - lightMasterWeightY) / ( boldMasterWeightY - lightMasterWeightY )
		
	return round( ( boldMasterWeightX - lightMasterWeightX ) * interpolationPointY + lightMasterWeightX, 1 )

def axisLocationEntry( axisName, locationValue ):
	return NSDictionary.alloc().initWithObjects_forKeys_(
		(axisName, locationValue),
		("Axis", "Location")
	)

class InstanceMaker( object ):
	"""GUI for injecting instances."""
	
	prefID = "com.mekkablue.InstanceMaker"
	
	def __init__( self ):
		
		# Window 'self.w':
		windowWidth  = 360
		windowHeight = 400
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 300   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Insert weight instances", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)

		linePos, inset, lineHeight = 12, 15, 26
		
		self.w.text_1 = vanilla.TextBox( (inset-1, linePos+2, 75, 14), "Insert", sizeStyle='small' )
		self.w.numberOfInstances = vanilla.PopUpButton( (inset+40, linePos, 50, 17), [str(x) for x in range( 3, 12 )], callback=self.UpdateSample, sizeStyle='small' )
		self.w.numberOfInstances.getNSPopUpButton().setToolTip_("Choose how many instances you want to add. A full weight spectrum has 9 weights.")
		self.w.text_2 = vanilla.TextBox( (inset+40+55, linePos+2, 120, 14), "instances with prefix", sizeStyle='small' )
		self.w.prefix = vanilla.EditText( (inset+40+55+120, linePos-1, -inset, 19), "A-", callback=self.UpdateSample, sizeStyle='small')
		self.w.prefix.getNSTextField().setToolTip_(u"Choose text that is added at the beginning of each instance, e.g., ‘Condensed’.")
		linePos += lineHeight
		
		self.w.text_3  = vanilla.TextBox( (inset-1, linePos+2, 60, 14), "from:", sizeStyle='small')
		self.w.master1 = vanilla.ComboBox((inset+35, linePos-1, 62, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.master1.getNSComboBox().setToolTip_("Weight value for the first instance being added, typically the stem width of your lightest weight.")
		self.w.text_4  = vanilla.TextBox( (inset+50+55*1, linePos+2, 55, 14), "through:", sizeStyle='small')
		self.w.master2 = vanilla.ComboBox((inset+50+55*2, linePos-1, 62, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.master2.getNSComboBox().setToolTip_("Weight value for the last instance being added, typically the stem width of your boldest weight.")
		self.w.text_5  = vanilla.TextBox( (inset+65+55*3, linePos+2, 55, 14), "at width:", sizeStyle='small')
		self.w.width   = vanilla.EditText((inset+65+55*4, linePos-1, -inset, 19), "100", callback=self.UpdateSample, sizeStyle='small')
		self.w.width.getNSTextField().setToolTip_("The Width value for the instances being added. Default is 100. Adapt accordingly if you are adding condensed or extended instances.")
		linePos += lineHeight
		
		self.w.text_6 = vanilla.TextBox( (inset-1, linePos+2, 60, 14), "using", sizeStyle='small')
		self.w.algorithm = vanilla.PopUpButton((inset+35, linePos, 110, 17), ("linear", "Pablo", "Schneider", "Abraham", "Luc(as)", "Reverse Luc(as)"), callback=self.UpdateSample, sizeStyle='small' )
		self.w.algorithm.getNSPopUpButton().setToolTip_("The way the Weight values are distributed between the first and last master values you entered above. Linear means equal steps between instances. Luc(as) (after Lucas de Groot) means the same growth percentage between instances. Pablo (after Pablo Impallari) is like Luc(as) at first, then becomes increasingly linear, i.e., flat in the periphery and steep in the middle. Schneider (after Lukas Schneider) is half way between Pablo and Luc(as) algorithms. Abraham (after Abraham Lee) is linear at first, then becomes increasingly like Luc(as), i.e. steep in the periphery, flat in the middle.\n\nFor a wide spectrum from thin to very bold, try Pablo or Schneider.\n\nFor spectrums from thin to average weights, try Abraham or Luc(as). They tend to have large jumps at the end, which are usually found in the center of the weight spectrum (Regular to Semibold). Smaller jumps are preferable in the periphery, i.e., for very light and very dark weights.\n\nFor going from average to very bold weights, try Reverse Luc(as). It has the big jumps at the beginning, and smaller steps at the end.")
		self.w.text_7 = vanilla.TextBox( (inset+40+110, linePos+2, 110, 14), "distribution.", sizeStyle='small')
		self.w.help_instances = vanilla.HelpButton((-15-21, linePos+2, -inset, 20), callback=self.openURL )
		linePos += lineHeight
		
		self.w.existingInstances = vanilla.RadioGroup((inset+20, linePos, -10, 60), ("Leave existing instances as they are", "Deactivate existing instances", "Delete existing instances"), callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.existingInstances.set( 0 )
		linePos += int(lineHeight*2.4)
		
		self.w.naturalNames = vanilla.CheckBox((inset, linePos, inset+225, 19), u"Use ‘natural’ weight names, starting at:", value=False, callback=self.UpdateSample, sizeStyle='small' )
		self.w.naturalNames.getNSButton().setToolTip_("Prefill with standard names and style linking. If turned off, will use the Weight number as instance name.")
		self.w.firstName = vanilla.PopUpButton((inset+225, linePos, -inset, 17), naturalNames, callback=self.UpdateSample, sizeStyle='small' )
		self.w.firstName.getNSPopUpButton().setToolTip_("If you use natural weight names, choose here the name of your lightest weight.")
		try: # workaround for macOS 10.9
			self.w.firstName.enable( self.w.naturalNames.getNSButton().isEnabled() )
		except:
			pass
		linePos += lineHeight-8
		
		if Glyphs.versionNumber >= 3:
			self.w.axisLocation = vanilla.CheckBox( (inset+20, linePos, 220, 20), u"Set Axis Location for each instance", value=True, callback=self.SavePreferences, sizeStyle='small' )
			self.w.axisLocationMaster = vanilla.CheckBox( (inset+227, linePos, -inset, 20), u"and master", value=True, callback=self.SavePreferences, sizeStyle='small' )
			self.w.axisLocation.getNSButton().setToolTip_(u"If enabled, will add an Axis Location parameter with the proper usWeightClass value in Font Info → Exports.\n\nHINT: Do not forget to set Axis Location parameters for each master in Font Info → Masters, and remove the Axis Mappings parameter in Font Info → Font if you have one.")
			self.w.axisLocationMaster.getNSButton().setToolTip_(u"If enabled, will attempt to set Axis Locations for masters as well. Only works if there is an instance that matches the respective master.")
			linePos += lineHeight-8

		self.w.italicStyle = vanilla.CheckBox( (inset+20, linePos, -inset, 20), u"Italic suffixes and style linking", value=False, callback=self.UpdateSample, sizeStyle='small' )
		self.w.italicStyle.getNSButton().setToolTip_(u"If enabled, will add the word ‘Italic’ to all instances, and also add italic style linking.")
		linePos += lineHeight
		
		self.w.maciej        = vanilla.CheckBox((inset, linePos-1, 160, 19), "Maciej y distribution from:", value=False, callback=self.UpdateSample, sizeStyle='small' )
		self.w.maciej.getNSButton().setToolTip_("An algorithm proposed by Maciej Ratajski, which introduces slightly different interpolation for y coordinates. Will add interpolationWeightY parameters to the instances. If these value differ greatly from the weight interpolation values, interpolation of your diagonals may suffer.")
		self.w.text_maciej_1 = vanilla.TextBox( (inset+165+55, linePos+2, 55, 19), "through:", sizeStyle='small')
		self.w.maciej_light  = vanilla.ComboBox((inset+160, linePos-1, 55, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.maciej_bold   = vanilla.ComboBox((inset+160+55+55, linePos-1, -inset, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small' )
		linePos += lineHeight-6

		self.w.text_maciej_2 = vanilla.TextBox( (inset+15, linePos, -40, 40), "Provide horizontal stem widths in extreme masters to interpolate contrast rather than stems.", sizeStyle='small', selectable=True )
		self.w.help_maciej   = vanilla.HelpButton((-inset-21, linePos+4, -inset, 20), callback=self.openURL )
		self.w.help_maciej.getNSButton().setToolTip_("Will open a website with a detailed description of the Maciej algorithm. Requires an internet connection.")
		linePos += int(lineHeight*1.2)
		
		self.w.shouldRound   = vanilla.CheckBox((inset, linePos, 200, 20), "Round all interpolation values", value=True, callback=self.UpdateSample, sizeStyle='small' )
		self.w.shouldRound.getNSButton().setToolTip_("If enabled, will round all calculated weight values to integers. Usually a good idea.")
		
		self.w.keepWindowOpen = vanilla.CheckBox( (inset+200, linePos, -inset, 20), "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.keepWindowOpen.getNSButton().setToolTip_("If checked, will not close this window after applying the distribution.")
		linePos += lineHeight
		
		self.w.sample = vanilla.Box( (inset, linePos, -inset, -30-inset) )
		self.w.sample.text = vanilla.TextBox( (5, 5, -5, -5), "", sizeStyle='small')
		
		# buttons:
		self.w.createButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.CreateInstances )
		self.w.setDefaultButton( self.w.createButton )
		
		if not self.LoadPreferences():
			print("Error: Could not load preferences. Will resort to defaults.")

		self.w.open()
		self.UpdateSample( self )
		self.w.makeKey()
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def axisTag(self, axis):
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			return axis.axisTag
		else:
			# Glyphs 2 code
			return axis["Tag"]

	def axisID(self, axis):
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			return axis.axisId
		else:
			# Glyphs 2 code
			# Glyphs 2 axis doesn't have an id
			return None
	
	def weightID(self, thisFont):
		weightAxisID = None
		if thisFont.axes:
			weightAxis = thisFont.axes[0] # default
			weightAxisID = self.axisID(weightAxis)
			for axis in thisFont.axes:
				axisTag = self.axisTag(axis)
				if axisTag == "wght":
					weightAxisID = self.axisID(axis)
		return weightAxisID

	def widthID(self, thisFont):
		widthAxisID = None # None
		for axis in thisFont.axes:
			if self.axisTag(axis) == "wdth":
				widthAxisID = self.axisID(axis)
		return widthAxisID
	
	def MasterList( self, factor ):
		thisFont = Glyphs.font
		MasterValues = ()
		if thisFont:
			try:
				# GLYPHS 3:
				if thisFont.axes:
					weightAxisID = self.weightID(thisFont)
					if weightAxisID:
						MasterValues = sorted( [m.axisValueValueForId_(weightAxisID) for m in thisFont.masters], key=lambda m: m * factor )
			except:
				# GLYPHS 2:
				import traceback
				print(traceback.format_exc())
				MasterValues = sorted( [m.weightValue for m in thisFont.masters], key=lambda m: m * factor )
				
		return MasterValues
	
	def Distribution( self ):
		a = self.w.master1.get().floatValue()
		b = self.w.master2.get().floatValue()
		n = int( self.w.numberOfInstances.getItems()[self.w.numberOfInstances.get()] )
		
		algorithm = self.w.algorithm.getItems()[self.w.algorithm.get()]
		if algorithm == "Pablo":
			distributedValues = distribute_pablo( a, b, n )
		elif algorithm == "Luc(as)":
			distributedValues = distribute_lucas( a, b, n )
		elif algorithm == "Reverse Luc(as)":
			distributedValues = distribute_reverselucas( a, b, n )
		elif algorithm == "Schneider":
			distributedValues = distribute_schneider( a, b, n )
		elif algorithm == "Abraham":
			distributedValues = distribute_abraham( a, b, n )
		else:
			distributedValues = distribute_equal( a, b, n )
		
		return distributedValues
	
	def UpdateSample( self, sender=None ):
		# Query UI entries and write preview text
		self.SavePreferences()
		
		try:
			usesNaturalNames = self.pref("naturalNames")
			
			# update UI elements:
			if usesNaturalNames:
				currentSelectionIndex = self.pref("firstName")
				numOfInstances = int( self.w.numberOfInstances.getItem() )
				availableInstanceNames = naturalNames[:-numOfInstances+1]
				numOfAvailableInstanceNames = len(availableInstanceNames)
				self.w.firstName.setItems( availableInstanceNames )
				if not currentSelectionIndex < len(availableInstanceNames):
					self.w.firstName.set(numOfAvailableInstanceNames-1)
				else:
					self.w.firstName.set(currentSelectionIndex)
				self.w.firstName.enable(True)
			else:
				self.w.firstName.enable(False)
				
			# store UI changes in defaults:
			self.SavePreferences()
			
			if self.pref("shouldRound"):
				rounding = 0
			else:
				rounding = 1
			
			distributedValues = [ round(value,rounding) for value in self.Distribution() ]
			n = len( distributedValues )
			prefix = self.pref("prefix")
			sampleText = "Will create %i instances: " % n
			
			if usesNaturalNames:
				sampleText += ", ".join( "%s%s (%.01f)" % (prefix,self.italicStyleName(name),weight) for name,weight in zip(naturalNames[currentSelectionIndex:], distributedValues) )
			else:
				sampleText += ", ".join( "%s%.0f (%.01f)" % (prefix,weight,weight) for weight in distributedValues )
			
			max = float(distributedValues[-1])
			min = float(distributedValues[0])
			growth = (max/min)**(1.0/(n-1))
			if self.w.algorithm.getItem() == "Luc(as)":
				sampleText += ",%s growth: %.1f%%" % ( 
					" average" if self.pref("shouldRound") else "",
					(growth-1)*100,
				)
			
			if self.pref("maciej"):
				maciejValues = self.MaciejValues()
				if maciejValues:
					maciejList = [ str( round( distribute_maciej( maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], w), rounding) ) for w in distributedValues ]
					sampleText += "\n\nWill add interpolationWeightY parameters to the respective instances: %s" % ( ", ".join( maciejList ) + "." )
			
			self.w.sample.text.set( sampleText )
		except Exception as e:
			print(e)
	
	def DealWithExistingInstances( self ):
		instancesChoice = self.w.existingInstances.get()
		
		if instancesChoice == 1: # deactivate
			for thisInstance in Glyphs.font.instances:
				thisInstance.active = False
		elif instancesChoice == 2: # delete
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				Glyphs.font.instances = [i for i in Glyphs.font.instances if i.type != INSTANCETYPESINGLE]
			else:
				# GLYPHS 2
				Glyphs.font.instances = None
			
		return True
	
	def updateUI(self, sender=None):
		# Natural names:
		onOff = self.pref("naturalNames")
		self.w.italicStyle.enable(onOff)
		if Glyphs.versionNumber >=3:
			self.w.axisLocation.enable(onOff)
		
		# Maciej:
		onOff = self.pref("maciej")
		self.w.text_maciej_1.enable(onOff)
		self.w.maciej_light.enable(onOff)
		self.w.maciej_bold.enable(onOff)
		
		# axis locations for master:
		onOff = self.pref("axisLocation")
		self.w.axisLocationMaster.enable(onOff)
		
		
	def SavePreferences( self, sender=None ):
		try:
			Glyphs.defaults[ self.domain("numberOfInstances") ] = self.w.numberOfInstances.get()
			Glyphs.defaults[ self.domain("prefix") ] = self.w.prefix.get()
			Glyphs.defaults[ self.domain("master1") ] = self.w.master1.get()
			Glyphs.defaults[ self.domain("master2") ] = self.w.master2.get()
			Glyphs.defaults[ self.domain("width") ] = self.w.width.get()
			Glyphs.defaults[ self.domain("algorithm") ] = self.w.algorithm.get()
			Glyphs.defaults[ self.domain("existingInstances") ] = self.w.existingInstances.get()
			Glyphs.defaults[ self.domain("maciej") ] = self.w.maciej.get()
			Glyphs.defaults[ self.domain("maciej1") ] = self.w.maciej_light.get()
			Glyphs.defaults[ self.domain("maciej2") ] = self.w.maciej_bold.get()
			Glyphs.defaults[ self.domain("shouldRound") ] = self.w.shouldRound.get()
			Glyphs.defaults[ self.domain("naturalNames") ] = self.w.naturalNames.get()
			Glyphs.defaults[ self.domain("firstName") ] = self.w.firstName.get()
			Glyphs.defaults[ self.domain("italicStyle") ] = self.w.italicStyle.get()
			Glyphs.defaults[ self.domain("keepWindowOpen") ] = self.w.keepWindowOpen.get()
			if Glyphs.versionNumber >= 3:
				Glyphs.defaults[ self.domain("axisLocation") ] = self.w.axisLocation.get()
				Glyphs.defaults[ self.domain("axisLocationMaster") ] = self.w.axisLocationMaster.get()
			
			self.updateUI(sender)
		except:
			import traceback
			print(traceback.format_exc())
			return False

		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault( self.domain("numberOfInstances"), "6")
			Glyphs.registerDefault( self.domain("prefix"), "A-")
			Glyphs.registerDefault( self.domain("master1"), self.MasterList(1))
			Glyphs.registerDefault( self.domain("master2"), self.MasterList(-1))
			Glyphs.registerDefault( self.domain("width"), "100")
			Glyphs.registerDefault( self.domain("algorithm"), 0)
			Glyphs.registerDefault( self.domain("existingInstances"), False)
			Glyphs.registerDefault( self.domain("maciej"), False)
			Glyphs.registerDefault( self.domain("maciej1"), self.MasterList(1))
			Glyphs.registerDefault( self.domain("maciej2"), self.MasterList(-1))
			Glyphs.registerDefault( self.domain("shouldRound"), True)
			Glyphs.registerDefault( self.domain("naturalNames"), True)
			Glyphs.registerDefault( self.domain("firstName"), 1)
			Glyphs.registerDefault( self.domain("italicStyle"), 0)
			Glyphs.registerDefault( self.domain("keepWindowOpen"), 1)
			if Glyphs.versionNumber >= 3:
				Glyphs.registerDefault( self.domain("axisLocation"), 1)
				Glyphs.registerDefault( self.domain("axisLocationMaster"), 1)

			self.w.numberOfInstances.set( self.pref("numberOfInstances") )
			self.w.prefix.set( self.pref("prefix") )
			self.w.master1.set( self.pref("master1") )
			self.w.master2.set( self.pref("master2") )
			self.w.width.set( self.pref("width") )
			self.w.algorithm.set( self.pref("algorithm") )
			self.w.existingInstances.set( self.pref("existingInstances") )
			self.w.maciej.set( self.pref("maciej") )
			self.w.maciej_light.set( self.pref("maciej1") )
			self.w.maciej_bold.set( self.pref("maciej2") )
			self.w.shouldRound.set( self.pref("shouldRound") )
			self.w.naturalNames.set( self.pref("naturalNames") )
			self.w.firstName.set( self.pref("firstName") )
			self.w.italicStyle.set( self.pref("italicStyle") )
			self.w.keepWindowOpen.set( self.pref("keepWindowOpen") )
			if Glyphs.versionNumber >= 3:
				self.w.axisLocation.set( self.pref("axisLocation") )
				self.w.axisLocationMaster.set( self.pref("axisLocationMaster") )
			
			self.updateUI()
		except:
			import traceback
			print(traceback.format_exc())
			return False
		
		return True
	
	def openURL( self, sender ):
		URL = None
		if sender == self.w.help_instances:
			URL = "http://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances"
		if sender == self.w.help_maciej:
			URL = "https://web.archive.org/web/20171017001354/http://www.maciejratajski.com/theory/interpolation-of-contrast"
			# URL = "http://www.maciejratajski.com/theory/interpolation-of-contrast/"
		if URL:
			import webbrowser
			webbrowser.open( URL )
	
	def MaciejValues( self ):
		lightX = self.w.master1.get().floatValue()
		boldX  = self.w.master2.get().floatValue()
		lightY = self.w.maciej_light.get().floatValue()
		boldY  = self.w.maciej_bold.get().floatValue()
		if lightX and boldX and lightY and boldY:
			return [ lightX, lightY, boldX, boldY ]
		else:
			return False
	
	def italicStyleName(self, styleName):
		if self.pref("italicStyle"):
			styleName = "%s Italic" % styleName
			styleName = styleName.replace("Regular Italic", "Italic")
		return styleName
	
	def CreateInstances( self, sender ):
		try:
			theFont = Glyphs.font
			paramName = "Axis Location"
			
			if self.DealWithExistingInstances():
				distributedValues = self.Distribution()
				try:
					widthValue = float(self.pref("width"))
				except:
					widthValue = 100.0
				prefix = self.pref("prefix")
				maciejYesOrNo = self.pref("maciej")
				roundingYesOrNo  = self.pref("shouldRound")
				
				if maciejYesOrNo:
					maciejValues = self.MaciejValues()
					# invalid if entered values are empty or invalid:
					if not maciejValues:
						maciejYesOrNo = False
		
				numOfInstances = int( self.pref("numberOfInstances") )
				currentSelectionIndex = int(self.pref("firstName"))
				instanceNames = naturalNames[currentSelectionIndex:]
				
				for i,thisWeight in enumerate(distributedValues):
					if roundingYesOrNo:
						thisWeight = round(thisWeight)
					
					# create new instance:
					newInstance = GSInstance()
					newInstance.active = True
					weightClassValue = None
					
					# determine names, style linking, weight class, etc.:
					if self.pref("naturalNames"):
						# weight style name (no italic)
						styleName = instanceNames[i]
						
						# weightclass
						weightClassOldName = weightClassesOldNames[styleName]
						weightClassValue = weightClasses[styleName]
						if ":" in weightClassOldName:
							weightClassValue = int(weightClassOldName.split(":")[1].strip())
							weightClassOldName = weightClassOldName.split(":")[0].strip()
						
						try:
							# GLYPHS 3:
							newInstance.setWeightClassValue_(weightClassValue)
						except:
							# GLYPHS 2:
							newInstance.weightClass = weightClassOldName
							if weightClassValue % 100:
								newInstance.customParameters["weightClass"] = weightClassValue
						
						# style name (with italic) and style linking
						newInstance.name = "%s%s" % (prefix, self.italicStyleName(styleName))
						if styleName == "Bold":
							newInstance.isBold = True
							newInstance.linkStyle = "%sRegular" % prefix
						
						# italic style linking:
						if self.pref("italicStyle"):
							newInstance.isItalic = True
							newInstance.linkStyle = newInstance.name.replace("Italic","").strip()

							# link bold italic to regular:
							if styleName in ("Regular", "Bold"):
								newInstance.linkStyle = "%sRegular"%prefix
						else:
							newInstance.isItalic = False
						
						# fix style linking to mere "Regular" (should be empty):
						if newInstance.linkStyle == "Regular":
							newInstance.linkStyle = None
						
					else:
						newInstance.name = "%s%i" % (prefix, thisWeight)
						newInstance.isBold = False
					
					if theFont:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3:
							weightID = self.weightID(theFont)
							widthID = self.widthID(theFont)
							if weightID:
								newInstance.setAxisValueValue_forId_(thisWeight, weightID)
							if widthID:
								newInstance.setAxisValueValue_forId_(widthValue, widthID)
							
							# Axis Location:
							if self.pref("axisLocation") and self.pref("naturalNames"):
								axisLocations = []
								for thisAxis in theFont.axes:
									if thisAxis.name == "Weight":
										if weightClassValue != None:
											value = weightClassValue
										else:
											value = 400
									elif thisAxis.name == "Width":
										value = widthValue
									else:
										value = 0
									axisLocations.append( axisLocationEntry(thisAxis.name, value) )
								if axisLocations:
									newInstance.customParameters[paramName] = tuple(axisLocations)
									
						else:
							# GLYPHS 2:
							newInstance.weightValue = thisWeight
							newInstance.widthValue = widthValue

						if maciejYesOrNo:
							interpolationY = distribute_maciej( maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], float( thisWeight ) )
							if roundingYesOrNo:
								interpolationY = round(interpolationY)
							newInstance.customParameters["InterpolationWeightY"] = ("%.1f" % interpolationY).replace(".0","")
					
						# add the created instance:
						theFont.instances.append( newInstance )
						newInstance.updateInterpolationValues()
					else:
						print("Error: No current font.")
				
				# set Axis Location for masters if possible:
				if Glyphs.versionNumber>=3 and theFont and self.pref("naturalNames") and self.pref("axisLocation") and self.pref("axisLocationMaster"):
					for thisMaster in theFont.masters:
						for thisInstance in [i for i in theFont.instances if i.type==0]:
							if thisMaster.axes == thisInstance.axes:
								thisMaster.customParameters[paramName] = thisInstance.customParameters[paramName]
								break
				
			if not self.SavePreferences():
				print("Error writing preferences.")
			
			if not self.pref("keepWindowOpen"):
				self.w.close()
		except Exception as e:
			print(e)
			import traceback
			print(traceback.format_exc())
	
InstanceMaker()
