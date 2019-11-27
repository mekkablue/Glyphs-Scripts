#MenuTitle: Find and Replace Components
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Replaces components in selected glyphs (GUI).
"""

import vanilla

def replaceComponent( thisLayer, oldCompName, newCompName ):
	try:
		for i in range( len( thisLayer.components )):
			if thisLayer.components[i].componentName == oldCompName:
				thisLayer.components[i].componentName = newCompName
	except Exception as e:
		print("Failed to replace %s for %s in %s." % ( oldCompName, newCompName, thisLayer.parent.name ))
		print(e)

class ComponentReplacer(object):

	def __init__( self):
		self.w = vanilla.FloatingWindow((400, 80), "Replace Components in Selection", minSize=(400, 80), maxSize=(500, 80), autosaveName="com.mekkablue.ReplaceComponents.mainwindow" )

		self.w.textReplace = vanilla.TextBox((15, 12+2, 65, 14), "Replace", sizeStyle='small')
		self.w.componentName = vanilla.PopUpButton((65, 12, 80, 17), self.GetComponentNames(), sizeStyle='small')
		self.w.resetComponentName = vanilla.SquareButton((65+80+10, 12, 20, 18), u"↺", sizeStyle='small', callback=self.SetComponentNames )

		self.w.textBy = vanilla.TextBox((65+80+40, 12+2, 25, 14), "by", sizeStyle='small')
		self.w.componentNewName = vanilla.EditText((65+80+40+30, 12, -120, 19), "glyph.alt", sizeStyle='small', callback=self.SavePrefs)
		self.w.resetComponentNewName = vanilla.SquareButton((-110, 12, -90, 18), u"↺", sizeStyle='small', callback=self.ResetComponentNewName )

		self.w.includeAllLayers = vanilla.CheckBox((15+3, 35, -15, 18), "Include all layers", value=True, sizeStyle='small', callback=self.SavePrefs )

		self.w.replaceButton = vanilla.Button((-80, 12+1, -15, 17), "Replace", sizeStyle='small', callback=self.ButtonCallback )
		self.w.setDefaultButton( self.w.replaceButton )

		if not self.LoadPrefs( ):
			print("Note: Could not load preferences. Will resort to defaults.")

		self.w.open()

	def ButtonCallback( self, sender ):
		Font = Glyphs.font
		selectedLayers = Font.selectedLayers
		
		oldComponentName  = self.w.componentName.getItems()[self.w.componentName.get()]
		newComponentName  = self.w.componentNewName.get()
		includeAllLayers = self.w.includeAllLayers.get()
		
		Font.disableUpdateInterface()
		
		if includeAllLayers:
			selectedGlyphs = [ l.parent for l in selectedLayers ]
			for thisGlyph in selectedGlyphs:
				for thisLayer in thisGlyph.layers:
					replaceComponent( thisLayer, oldComponentName, newComponentName )
		else:
			for thisLayer in selectedLayers:
				replaceComponent( thisLayer, oldComponentName, newComponentName )
		
		Font.enableUpdateInterface()
		
		return True
	
	def GetComponentNames( self):
		myComponentList = set()
		selectedGlyphs = [ l.parent for l in Glyphs.font.selectedLayers ]
		
		for thisGlyph in selectedGlyphs:
			for thisLayer in thisGlyph.layers:
				for thisComponent in thisLayer.components:
					myComponentList.add( thisComponent.componentName )
		
		# myComponentList.sort( key=len, reverse=False )
		return sorted( list( myComponentList ))
	
	def SetComponentNames( self, sender ):
		myComponentList = self.GetComponentNames()
		self.w.componentName.setItems( myComponentList )
		return True
	
	def ResetComponentNewName( self, sender ):
		glyphName = Glyphs.font.selectedLayers[0].parent.name
		ending = glyphName[ glyphName.find("."): ]
		oldComponentName  = self.w.componentName.getItems()[self.w.componentName.get()]
		self.w.componentNewName.set( oldComponentName + ending )
		return True
	
	def SavePrefs( self, sender ):
		Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"] = self.w.componentNewName.get()
		Glyphs.defaults["com.mekkablue.ReplaceComponents.includeAllLayers"] = self.w.includeAllLayers.get()
		return True
	
	def LoadPrefs( self ):
		try:
			self.w.componentNewName.set( Glyphs.defaults["com.mekkablue.ReplaceComponents.newCompName"] )
			self.w.includeAllLayers.set( Glyphs.defaults["com.mekkablue.ReplaceComponents.includeAllLayers"] )
			return True
		except:
			return False

ComponentReplacer()
