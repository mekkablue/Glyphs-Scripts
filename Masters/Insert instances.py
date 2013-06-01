#MenuTitle: Insert instances
# -*- coding: utf-8 -*-
"""Inserts instances, based on the Luc(as) an Pablo algorithms."""
from __future__ import division
import vanilla
import GlyphsApp

rangemin = 3
rangemax = 11

def distribute_lucas(min, max, n):
    q = max / min
    return [ min * q**(i/(n-1)) for i in range(n) ]
 
def distribute_equal(min, max, n):
    d = (max - min) / (n-1)
    return [ min + i*d for i in range(n) ]
 
def distribute_pablo(min, max, n):
    es = distribute_equal(min, max, n)
    ls = distribute_lucas(min, max, n)
    return [ l*(1-i/(n-1)) + e*(i/(n-1)) for (i, e, l) in zip(range(n), es, ls) ]

class InstanceMaker( object ):
	"""GUI for injecting instances."""
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (350, 260), "Insert weight instances", minSize=(350, 260), maxSize=(350, 350), autosaveName="com.mekkablue.InstanceMaker.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 75, 14), "Insert", sizeStyle='small' )
		self.w.numberOfInstances = vanilla.PopUpButton( (15+40, 12, 50, 17), [str(x) for x in range( 3, 12 )], callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (15+40+55, 12+2, 120, 14), "instances with prefix", sizeStyle='small' )
		self.w.prefix = vanilla.EditText( (15+40+55+120, 12-1, -15, 19), "A-", callback=self.UpdateSample, sizeStyle='small')

		self.w.text_3 =  vanilla.TextBox( (15-1, 40+2, 60, 14), "from:", sizeStyle='small')
		self.w.master1 = vanilla.ComboBox((15+40, 40-1, 50, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_4 =  vanilla.TextBox( (15+40+55, 40+2, 55, 14), "through:", sizeStyle='small')
		self.w.master2 = vanilla.ComboBox((15+40+55+55, 40-1, 50, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_5 =  vanilla.TextBox( (15+40+55+55+55, 40+2, 55, 14), "at width:", sizeStyle='small')
		self.w.width =   vanilla.EditText((15+40+45+55+55+65, 40-1, -15, 19), "100", callback=self.SavePreferences, sizeStyle='small')
		
		self.w.text_6 = vanilla.TextBox( (15-1, 68+2, 60, 14), "using", sizeStyle='small')
		self.w.algorithm = vanilla.PopUpButton((15+40, 68, 80, 17), [ "Pablo", "Luc(as)", "linear" ], callback=self.UpdateSample, sizeStyle='small' )
		self.w.text_7 = vanilla.TextBox( (15+40+85, 68+2, 110, 14), "distribution:", sizeStyle='small')
		
		self.w.existingInstances = vanilla.RadioGroup((15, 100, -10, 60), [ "Leave existing instances as they are", "Deactivate existing instances", "Delete existing instances" ], callback=self.SavePreferences, sizeStyle = 'small' )
		self.w.existingInstances.set( 0 )
		
		self.w.sample = vanilla.Box( (15, 170, -15, -30-15) )
		self.w.sample.text = vanilla.TextBox( (5, 5, -5, -5), "", sizeStyle='small')
		
		self.w.createButton = vanilla.Button((-80-15, -20-15, -15, -15), "Create", sizeStyle='regular', callback=self.CreateInstances )
		self.w.setDefaultButton( self.w.createButton )
		
		if not self.LoadPreferences( ):
			print "Error: Could not load preferences. Will resort to defaults."

		self.w.open()
		self.UpdateSample( self )
	
	def MasterList( self, factor ):
		Font = Glyphs.font
		MasterValues = sorted( [m.weightValue for m in Font.masters], key=lambda m: m * factor )
		return MasterValues
	
	def Distribution( self ):
		a = float( self.w.master1.get() )
		b = float( self.w.master2.get() )
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
		try:
			distributedValues = self.Distribution( )
			n = len( distributedValues )
			prefix = self.w.prefix.get()
			sampleText = "Will create %i instances: %s" % ( n, ", ".join( prefix+"{0:.0f}".format(weight) for weight in distributedValues ))
			
			if self.w.algorithm.getItems()[self.w.algorithm.get()] == "Luc(as)":
				sampleText += ", growth: %.1f%%" % ( (distributedValues[1] / distributedValues[0]) *100-100 )
			
			self.w.sample.text.set( sampleText )
			self.SavePreferences( self )
		except Exception, e:
			print e
	
	def DealWithExistingInstances( self ):
		instancesChoice = self.w.existingInstances.get()
		
		if instancesChoice == 1: # deactivate
			for thisInstance in Glyphs.font.instances:
				thisInstance.active = False
		elif instancesChoice == 2: # delete
			while len( Glyphs.font.instances ) != 0:
				Glyphs.font.removeInstanceAtIndex_(0)
				
		return True
		
	def SavePreferences( self, sender ):
		Glyphs.defaults["com.mekkablue.InstanceMaker.numberOfInstances"] = self.w.numberOfInstances.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"] = self.w.prefix.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.master1"] = self.w.master1.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.master2"] = self.w.master2.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.width"] = self.w.width.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.algorithm"] = self.w.algorithm.get()
		Glyphs.defaults["com.mekkablue.InstanceMaker.existingInstances"] = self.w.existingInstances.get()
		
		return True

	def LoadPreferences( self ):
		try:
			self.w.numberOfInstances.set( Glyphs.defaults["com.mekkablue.InstanceMaker.numberOfInstances"] )
			self.w.prefix.set( Glyphs.defaults["com.mekkablue.InstanceMaker.prefix"] )
			self.w.master1.set( Glyphs.defaults["com.mekkablue.InstanceMaker.master1"] )
			self.w.master2.set( Glyphs.defaults["com.mekkablue.InstanceMaker.master2"] )
			self.w.width.set( Glyphs.defaults["com.mekkablue.InstanceMaker.width"] )
			self.w.algorithm.set( Glyphs.defaults["com.mekkablue.InstanceMaker.algorithm"] )
			self.w.existingInstances.set( Glyphs.defaults["com.mekkablue.InstanceMaker.existingInstances"] )
		except:
			return False
		
		return True
	
	def CreateInstances( self, sender ):
		try:
			if self.DealWithExistingInstances( ):
				distributedValues = self.Distribution( )
				widthValue = float( self.w.width.get() )
				prefix = self.w.prefix.get()
		
				for thisWeight in distributedValues:
					newInstance = GSInstance()
					newInstance.active = True
					newInstance.name = prefix + "{0:.0f}".format( thisWeight )
					newInstance.weightValue = thisWeight
					newInstance.widthValue = widthValue
					newInstance.isItalic = False
					newInstance.isBold = False
					
					Glyphs.font.addInstance_( newInstance )
			
			if not self.SavePreferences( self ):
				print "Error writing preferences."
			
			self.w.close()
		except Exception, e:
			raise e

InstanceMaker()
