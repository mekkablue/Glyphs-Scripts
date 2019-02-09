#MenuTitle: Insert instances
# -*- coding: utf-8 -*-
from __future__ import division
__doc__="""
Inserts instances, based on the Luc(as), Pablo, and Maciej algorithms.
"""
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
	"Hairline":50,
	"Thin":100,
	"Extralight":200,
	"Light":300,
	"Regular":400,
	"Medium":500,
	"Semibold":600,
	"Bold":700,
	"Extrabold":800,
	"Black":900,
	"Extrablack":950,
}

weightClassesOldNames = {
	"Hairline":"Thin:50",
	"Thin":"Thin",
	"Extralight":"ExtraLight",
	"Light":"Light",
	"Regular":"Regular",
	"Medium":"Medium",
	"Semibold":"SemiBold",
	"Bold":"Bold",
	"Extrabold":"ExtraBold",
	"Black":"Black",
	"Extrablack":"Black:950",
}


def distribute_lucas( min, max, n ):
	q = max / min
	return [ min * q**(i/(n-1)) for i in range(n) ]
 
def distribute_equal( min, max, n ):
	d = (max - min) / (n-1)
	return [ min + i*d for i in range(n) ]
 
def distribute_pablo( min, max, n ):
	es = distribute_equal(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [ l*(1-i/(n-1)) + e*(i/(n-1)) for (i, e, l) in zip(range(n), es, ls) ]

def distribute_maciej( lightMasterWeightX, lightMasterWeightY, boldMasterWeightX, boldMasterWeightY, interpolationWeightX ):
	"""
	Algorithm by Maciej Ratajski
	http://jsfiddle.net/Dm2Zk/1/
	"""
	interpolationPointX =  ( interpolationWeightX - lightMasterWeightX ) / ( boldMasterWeightX - lightMasterWeightX )
	interpolationWeightY = ( ( 1 - interpolationPointX ) * ( lightMasterWeightY / lightMasterWeightX - boldMasterWeightY / boldMasterWeightX ) + boldMasterWeightY / boldMasterWeightX ) * interpolationWeightX
	interpolationPointY =  ( interpolationWeightY - lightMasterWeightY) / ( boldMasterWeightY - lightMasterWeightY )
		
	return round( ( boldMasterWeightX - lightMasterWeightX ) * interpolationPointY + lightMasterWeightX, 1 )

class InstanceMaker( object ):
	"""GUI for injecting instances."""
	def __init__( self ):
		
		# Window 'self.w':
		windowWidth  = 360
		windowHeight = 380
		windowWidthResize  = 0 # user can resize width by this value
		windowHeightResize = 300   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Insert weight instances", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.InstanceMaker.mainwindow" # stores last window position and size
		)
		inset, lineheight = 15, 12
		
		self.w.text_1 = vanilla.TextBox( (inset-1, lineheight+2, 75, 14), "Insert", sizeStyle='small' )
		self.w.numberOfInstances = vanilla.PopUpButton( (inset+40, lineheight, 50, 17), [str(x) for x in range( 3, 12 )], callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (inset+40+55, lineheight+2, 120, 14), "instances with prefix", sizeStyle='small' )
		self.w.prefix = vanilla.EditText( (inset+40+55+120, lineheight-1, -inset, 19), "A-", callback=self.UpdateSample, sizeStyle='small')
		lineheight += 28
		
		self.w.text_3  = vanilla.TextBox( (inset-1, lineheight+2, 60, 14), "from:", sizeStyle='small')
		self.w.master1 = vanilla.ComboBox((inset+35, lineheight-1, 62, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_4  = vanilla.TextBox( (inset+50+55*1, lineheight+2, 55, 14), "through:", sizeStyle='small')
		self.w.master2 = vanilla.ComboBox((inset+50+55*2, lineheight-1, 62, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_5  = vanilla.TextBox( (inset+65+55*3, lineheight+2, 55, 14), "at width:", sizeStyle='small')
		self.w.width   = vanilla.EditText((inset+65+55*4, lineheight-1, -inset, 19), "100", callback=self.UpdateSample, sizeStyle='small')
		lineheight += 28
		
		self.w.text_6 = vanilla.TextBox( (inset-1, lineheight+2, 60, 14), "using", sizeStyle='small')
		self.w.algorithm = vanilla.PopUpButton((inset+40, lineheight, 80, 17), [ "Pablo", "Luc(as)", "linear" ], callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_7 = vanilla.TextBox( (inset+40+85, lineheight+2, 110, 14), "distribution:", sizeStyle='small')
		self.w.help_instances = vanilla.HelpButton((-15-21, lineheight+2, -inset, 20), callback=self.openURL )
		lineheight += 32
		
		self.w.existingInstances = vanilla.RadioGroup((inset+30, lineheight, -10, 60), [ "Leave existing instances as they are", "Deactivate existing instances", "Delete existing instances" ], callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.existingInstances.set( 0 )
		lineheight += 70
		
		self.w.naturalNames = vanilla.CheckBox((inset, lineheight-1, inset+230, 19), u"Use ‘natural’ weight names, starting at:", value=False, callback=self.UpdateSample, sizeStyle='small' )
		self.w.firstName = vanilla.PopUpButton((inset+230, lineheight, -inset, 17), naturalNames, callback=self.UpdateSample, sizeStyle='small' )
		self.w.firstName.enable( self.w.naturalNames.getNSButton().isEnabled() )
		lineheight += 28
		
		self.w.maciej        = vanilla.CheckBox((inset, lineheight-1, 160, 19), "Maciej y distribution from:", value=False, callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_maciej_1 = vanilla.TextBox( (inset+165+55, lineheight+2, 55, 19), "through:", sizeStyle='small')
		self.w.text_maciej_2 = vanilla.TextBox( (inset+15, lineheight+2+20, -40, 40), "Provide horizontal stem widths in extreme masters to interpolate contrast rather than stems.", sizeStyle='small', selectable=True )
		self.w.maciej_light  = vanilla.ComboBox((inset+160, lineheight-1, 55, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.maciej_bold   = vanilla.ComboBox((inset+160+55+55, lineheight-1, -inset, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.help_maciej   = vanilla.HelpButton((-inset-21, lineheight+6+20, -inset, 20), callback=self.openURL )
		lineheight += 60
		
		self.w.shouldRound   = vanilla.CheckBox((inset, lineheight, -inset, 19), "Round all interpolation values", value=True, callback=self.UpdateSample, sizeStyle='small' )
		lineheight += 30
		
		self.w.sample = vanilla.Box( (inset, lineheight, -inset, -30-inset) )
		self.w.sample.text = vanilla.TextBox( (5, 5, -5, -5), "", sizeStyle='small')
		
		self.w.createButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Create", sizeStyle='regular', callback=self.CreateInstances )
		self.w.setDefaultButton( self.w.createButton )
		
		if not self.LoadPreferences():
			print "Error: Could not load preferences. Will resort to defaults."

		self.w.open()
		self.UpdateSample( self )
		self.w.makeKey()
	
	def MasterList( self, factor ):
		thisFont = Glyphs.font
		if thisFont:
			MasterValues = sorted( [m.weightValue for m in thisFont.masters], key=lambda m: m * factor )
			return MasterValues
		else:
			return ()
	
	def Distribution( self ):
		a = self.w.master1.get().floatValue()
		b = self.w.master2.get().floatValue()
		n = int( self.w.numberOfInstances.getItems()[self.w.numberOfInstances.get()] )
		
		algorithm = self.w.algorithm.getItems()[self.w.algorithm.get()]
		if algorithm == "Pablo":
			distributedValues = distribute_pablo( a, b, n )
		elif algorithm == "Luc(as)":
			distributedValues = distribute_lucas( a, b, n )
		else:
			distributedValues = distribute_equal( a, b, n )
		
		return distributedValues
	
	def UpdateSample( self, sender ):
		# Query UI entries and write preview text
		self.SavePreferences( None )
		
		try:
			usesNaturalNames = Glyphs.defaults["com.mekkablue.InstanceMaker.naturalNames"]
			
			# update UI elements:
			if usesNaturalNames:
				currentSelectionIndex = Glyphs.defaults["com.mekkablue.InstanceMaker.firstName"]
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
			self.SavePreferences( None )
			
			if Glyphs.defaults["com.mekkablue.InstanceMaker.shouldRound"]:
				rounding = 0
			else:
				rounding = 1
			
			distributedValues = [ round(value,rounding) for value in self.Distribution() ]
			n = len( distributedValues )
			prefix = Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"]
			sampleText = "Will create %i instances: " % n
			
			if usesNaturalNames:
				sampleText += ", ".join( "%s%s (%.01f)" % (prefix,name,weight) for name,weight in zip(naturalNames[currentSelectionIndex:], distributedValues) )
			else:
				sampleText += ", ".join( "%s%.0f (%.01f)" % (prefix,weight,weight) for weight in distributedValues )
			
			max = float(distributedValues[-1])
			min = float(distributedValues[0])
			growth = (max/min)**(1.0/(n-1))
			if self.w.algorithm.getItem() == "Luc(as)":
				sampleText += ",%s growth: %.1f%%" % ( 
					" average" if Glyphs.defaults["com.mekkablue.InstanceMaker.shouldRound"] else "",
					(growth-1)*100,
				)
			
			if Glyphs.defaults["com.mekkablue.InstanceMaker.maciej"]:
				maciejValues = self.MaciejValues()
				if maciejValues:
					maciejList = [ str( round( distribute_maciej( maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], w), rounding) ) for w in distributedValues ]
					sampleText += "\n\nWill add interpolationWeightY parameters to the respective instances: %s" % ( ", ".join( maciejList ) + "." )
			
			self.w.sample.text.set( sampleText )
		except Exception, e:
			print e
	
	def DealWithExistingInstances( self ):
		instancesChoice = self.w.existingInstances.get()
		
		if instancesChoice == 1: # deactivate
			for thisInstance in Glyphs.font.instances:
				thisInstance.active = False
		elif instancesChoice == 2: # delete
			Glyphs.font.instances = None
		return True
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.InstanceMaker.numberOfInstances"] = self.w.numberOfInstances.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"] = self.w.prefix.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.master1"] = self.w.master1.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.master2"] = self.w.master2.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.width"] = self.w.width.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.algorithm"] = self.w.algorithm.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.existingInstances"] = self.w.existingInstances.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.maciej"] = self.w.maciej.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.maciej1"] = self.w.maciej_light.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.maciej2"] = self.w.maciej_bold.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.shouldRound"] = self.w.shouldRound.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.naturalNames"] = self.w.naturalNames.get()
			Glyphs.defaults["com.mekkablue.InstanceMaker.firstName"] = self.w.firstName.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.numberOfInstances", "6")
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.prefix", "A-")
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.master1", self.MasterList(1))
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.master2", self.MasterList(-1))
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.width", "100")
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.algorithm", 0)
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.existingInstances", False)
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.maciej", False)
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.maciej1", self.MasterList(1))
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.maciej2", self.MasterList(-1))
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.shouldRound", True)
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.naturalNames", True)
			Glyphs.registerDefault("com.mekkablue.InstanceMaker.firstName", 1)

			self.w.numberOfInstances.set( Glyphs.defaults["com.mekkablue.InstanceMaker.numberOfInstances"] )
			self.w.prefix.set( Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"] )
			self.w.master1.set( Glyphs.defaults["com.mekkablue.InstanceMaker.master1"] )
			self.w.master2.set( Glyphs.defaults["com.mekkablue.InstanceMaker.master2"] )
			self.w.width.set( Glyphs.defaults["com.mekkablue.InstanceMaker.width"] )
			self.w.algorithm.set( Glyphs.defaults["com.mekkablue.InstanceMaker.algorithm"] )
			self.w.existingInstances.set( Glyphs.defaults["com.mekkablue.InstanceMaker.existingInstances"] )
			self.w.maciej.set( Glyphs.defaults["com.mekkablue.InstanceMaker.maciej"] )
			self.w.maciej_light.set( Glyphs.defaults["com.mekkablue.InstanceMaker.maciej1"] )
			self.w.maciej_bold.set( Glyphs.defaults["com.mekkablue.InstanceMaker.maciej2"] )
			self.w.shouldRound.set( Glyphs.defaults["com.mekkablue.InstanceMaker.shouldRound"] )
			self.w.naturalNames.set( Glyphs.defaults["com.mekkablue.InstanceMaker.naturalNames"] )
			self.w.firstName.set( Glyphs.defaults["com.mekkablue.InstanceMaker.firstName"] )
		except:
			return False
		
		return True
	
	def openURL( self, sender ):
		URL = None
		if sender == self.w.help_instances:
			URL = "http://www.glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances"
		if sender == self.w.help_maciej:
			URL = "http://www.maciejratajski.com/theory/interpolation-of-contrast/"
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
		
	def CreateInstances( self, sender ):
		try:
			if self.DealWithExistingInstances():
				
				# Glyphs.defaults["com.mekkablue.InstanceMaker.master1"]
				# Glyphs.defaults["com.mekkablue.InstanceMaker.master2"]
				#
				# Glyphs.defaults["com.mekkablue.InstanceMaker.algorithm"]
				# Glyphs.defaults["com.mekkablue.InstanceMaker.existingInstances"]
				#
				# Glyphs.defaults["com.mekkablue.InstanceMaker.maciej1"]
				# Glyphs.defaults["com.mekkablue.InstanceMaker.maciej2"]
				
				distributedValues = self.Distribution()
				widthValue = float(Glyphs.defaults["com.mekkablue.InstanceMaker.width"]) #self.w.width.get().floatValue()
				prefix = Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"] #self.w.prefix.get()
				maciejYesOrNo = Glyphs.defaults["com.mekkablue.InstanceMaker.maciej"] #self.w.maciej.get()
				roundingYesOrNo  = Glyphs.defaults["com.mekkablue.InstanceMaker.shouldRound"] #self.w.shouldRound.get()
				
				if maciejYesOrNo:
					maciejValues = self.MaciejValues()
					# invalid if entered values are empty or invalid:
					if not maciejValues:
						maciejYesOrNo = False
		
				numOfInstances = int( Glyphs.defaults["com.mekkablue.InstanceMaker.numberOfInstances"] )
				currentSelectionIndex = int(Glyphs.defaults["com.mekkablue.InstanceMaker.firstName"])
				instanceNames = naturalNames[currentSelectionIndex:]
				
				for i,thisWeight in enumerate(distributedValues):
					if roundingYesOrNo:
						thisWeight = round(thisWeight)
						
					newInstance = GSInstance()
					newInstance.active = True
					if Glyphs.defaults["com.mekkablue.InstanceMaker.naturalNames"]:
						styleName = instanceNames[i]
						newInstance.name = "%s%s" % (prefix, styleName)
						newInstance.isBold = styleName=="Bold"
						weightClassOldName = weightClassesOldNames[styleName]
						weightClassValue = weightClasses[styleName]
						if ":" in weightClassOldName:
							weightClassValue = int(weightClassOldName.split(":")[1].strip())
							weightClassOldName = weightClassOldName.split(":")[0].strip()
						
						newInstance.weightClass = weightClassOldName
						if weightClassValue % 100:
							newInstance.customParameters["weightClass"] = weightClassValue
					else:
						newInstance.name = "%s%i" % (prefix, thisWeight)
						newInstance.isBold = False
					newInstance.weightValue = thisWeight
					newInstance.widthValue = widthValue
					newInstance.isItalic = False
					
					if maciejYesOrNo:
						interpolationY = distribute_maciej( maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], float( thisWeight ) )
						if roundingYesOrNo:
							interpolationY = round(interpolationY)
						newInstance.customParameters["InterpolationWeightY"] = ("%.1f" % interpolationY).replace(".0","")
					
					theFont = Glyphs.font
					if theFont:
						theFont.instances.append( newInstance )
						newInstance.updateInterpolationValues()
					else:
						print "Error: No current font."
			
			if not self.SavePreferences( self ):
				print "Error writing preferences."
			
			self.w.close()
		except Exception, e:
			print e
			import traceback
			print traceback.format_exc()

InstanceMaker()
