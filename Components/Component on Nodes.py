#MenuTitle: Components on Nodes
# -*- coding: utf-8 -*-
"""GUI for placing a component on each node in the selected layers."""

import vanilla
import GlyphsApp
windowHeight = 135

def deleteAllComponents( thisLayer ):
	print "  Deleting %i existing components." % ( len(thisLayer.components) )
	while len(thisLayer.components) > 0:
		print "  Deleting component", thisLayer.components[0].componentName
		del thisLayer.components[0]

def getAllCoordinates( thisLayer ):
	layerCoords = []
	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			layerCoords += [[thisNode.x, thisNode.y]]
	
	return layerCoords

def process( thisLayer, thisComponentName ):
	myCoords = getAllCoordinates( thisLayer )
	print "-- Placing %i instances of %s in %s." % ( len(myCoords), thisComponentName, thisLayer.parent.name )
	for thisCoordPair in myCoords:
		x = thisCoordPair[0]
		y = thisCoordPair[1]
		
		newComp = GSComponent( thisComponentName , NSPoint( x, y ) )
		thisLayer.addComponent_(newComp)

class ComponentsOnNodes( object ):
	def __init__( self ):
		self.w = vanilla.FloatingWindow( (350, windowHeight), "Components on Nodes", minSize=(300, windowHeight), maxSize=(500, windowHeight), autosaveName="com.mekkablue.ComponentsOnNodes.mainwindow" )

		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 15+70, 14), "Place glyph", sizeStyle='small' )
		self.w.componentEdit = vanilla.EditText( (15+70, 12-1, -15, 19), "pixel", callback=self.SavePreferences, sizeStyle='small' )
		self.w.text_2 = vanilla.TextBox( (15-1, 12+25, -15, 14), "as component on all nodes in selected layers.", sizeStyle='small' )
		self.w.replaceComponents = vanilla.CheckBox((15+3, 12+25+20, -15, 18), "Replace existing components", value=True, sizeStyle='small', callback=self.SavePreferences )
		
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Insert", sizeStyle='regular', callback=self.ComponentsOnNodesMain )
		self.w.setDefaultButton( self.w.runButton )
		
		try:
			self.LoadPreferences( )
		except:
			pass

		self.w.open()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.ComponentsOnNodes.componentEdit"] = self.w.componentEdit.get()
			Glyphs.defaults["com.mekkablue.ComponentsOnNodes.replaceComponents"] = self.w.replaceComponents.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.componentEdit.set( Glyphs.defaults["com.mekkablue.ComponentsOnNodes.componentEdit"] )
			self.w.replaceComponents.set( Glyphs.defaults["com.mekkablue.ComponentsOnNodes.replaceComponents"] )
		except:
			return False
			
		return True

	def ComponentsOnNodesMain( self, sender ):
		try:
			Doc  = Glyphs.currentDocument
			Font = Glyphs.font
			FontMaster = Doc.selectedFontMaster()
			selectedLayers = Doc.selectedLayers()
			componentName = self.w.componentEdit.get()
			deleteExistingComps = self.w.replaceComponents.get()
			
			Font.disableUpdateInterface()

			for thisLayer in selectedLayers:
				thisGlyph = thisLayer.parent
				print "Processing", thisGlyph.name

				if deleteExistingComps:
					deleteAllComponents( thisLayer )

				thisGlyph.undoManager().beginUndoGrouping()
				process( thisLayer, componentName )
				thisGlyph.undoManager().endUndoGrouping()

			Font.enableUpdateInterface()
			
			
			if not self.SavePreferences( self ):
				print "Note: could not write preferences."
			
			self.w.close()
		except Exception, e:
			raise e

ComponentsOnNodes()
