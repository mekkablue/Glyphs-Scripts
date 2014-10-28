#MenuTitle: Copy Layer to Layer
# -*- coding: utf-8 -*-
__doc__="""
Copies one master to another master in selected glyphs.
"""

import GlyphsApp
import vanilla
import math

def getComponentScaleX_scaleY_rotation( self ):
		a = self.transform[0]
		b = self.transform[1]
		c = self.transform[2]
		d = self.transform[3]

		scale_x = math.sqrt(math.pow(a,2)+math.pow(b,2))
		scale_y = math.sqrt(math.pow(c,2)+math.pow(d,2))
		if (b<0 and c<0):
			scale_y = scale_y * -1

		rotation = math.atan2(b, a) * (180/math.pi)
		
		return [scale_x, scale_y, rotation]	
		
		
class MasterFiller( object ):

	def __init__( self ):
		self.w = vanilla.FloatingWindow((300, 120), "Copy layer to layer")

		self.w.text_1 = vanilla.TextBox((15, 12+2, 120, 14), "Copy paths from", sizeStyle='small')
		self.w.master_from = vanilla.PopUpButton((120, 12, -15, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)
		
		self.w.text_2 = vanilla.TextBox((15, 32+2, 120, 14), "into selection of", sizeStyle='small')
		self.w.master_into = vanilla.PopUpButton((120, 32, -15, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)

		self.w.include_components = vanilla.CheckBox((15, 52+2, -100, 20), "Include components", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.include_anchors = vanilla.CheckBox((15, 52+20, -100, 20), "Include anchors", sizeStyle='small', callback=self.SavePreferences, value=True)
		self.w.include_metrics = vanilla.CheckBox((15, 52+38, -100, 20), "Include metrics", sizeStyle='small', callback=self.SavePreferences, value=True)

		self.w.copybutton = vanilla.Button((-80, -30, -15, -10), "Copy", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.copybutton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Copy Layer to Layer' could not load preferences. Will resort to defaults."
		
		self.w.open()
		self.w.master_into.set(1)
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MasterFiller.include_components"] = self.w.include_components.get()
			Glyphs.defaults["com.mekkablue.MasterFiller.include_anchors"] = self.w.include_anchors.get()
			Glyphs.defaults["com.mekkablue.MasterFiller.include_metrics"] = self.w.include_metrics.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.include_components.set( Glyphs.defaults["com.mekkablue.MasterFiller.include_components"] )
			self.w.include_anchors.set( Glyphs.defaults["com.mekkablue.MasterFiller.include_anchors"] )
			self.w.include_metrics.set( Glyphs.defaults["com.mekkablue.MasterFiller.include_metrics"] )
		except:
			return False
			
		return True
	
	def GetMasterNames( self ):
		myMasterList = []

		for i in range( len( Glyphs.currentDocument.font.masters ) ):
			x = Glyphs.currentDocument.font.masters[i]
			myMasterList.append( '%i: %s' % (i, x.name) )
		
		return myMasterList
	
	def MasterChangeCallback( self, sender ):
		if self.w.master_from.get() == self.w.master_into.get():
			self.w.copybutton.enable( False )
		else:
			self.w.copybutton.enable( True )
			
	def copyPathsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all paths from sourceLayer to targetLayer"""
		num_from  = len( sourceLayer.paths )
		num_into  = len( targetLayer.paths )
		
		if num_into != 0:
			print "- Cleaning out paths in target layer"
			for i in range( num_into )[::-1]:
				del targetLayer.paths[i]

		if num_from > 0:
			print "- Copying paths"
			for thisPath in sourceLayer.paths:
				newPath = GSPath()

				for n in thisPath.nodes:
					newNode = GSNode()
					newNode.type = n.type
					newNode.connection = n.connection
					newNode.setPosition_( (n.x, n.y) )
					newPath.addNode_( newNode )

				newPath.closed = thisPath.closed
				targetLayer.paths.append( newPath )
	
	def copyComponentsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all components from sourceLayer to targetLayer."""
		comp_from = len( sourceLayer.components )
		comp_into = len( targetLayer.components )
		
		if comp_into != 0:
			print "- Cleaning out components in target layer"
			for i in range( comp_into )[::-1]:
				del targetLayer.components[i]
	
		if comp_from > 0:
			print "- Copying components:"
			for thisComp in sourceLayer.components:
				compName = str( thisComp.componentName ) # str() probably not necessary anymore, but once fixed a problem
				newComp = GSComponent( compName )
				newComp.setPosition_( (thisComp.x, thisComp.y) )
				ScaleX_scaleY_rotation = getComponentScaleX_scaleY_rotation(thisComp)
				newComp.setScaleX_scaleY_rotation_(ScaleX_scaleY_rotation[0],ScaleX_scaleY_rotation[1],ScaleX_scaleY_rotation[2])
				print "-- Component: %s" % ( compName )
				targetLayer.components.append( newComp )

	def copyAnchorsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies all anchors from sourceLayer to targetLayer."""
		anch_from = len( sourceLayer.anchors )
		anch_into = len( targetLayer.anchors )
		
		if anch_into != 0:
			print "- Cleaning out anchors in target layer"
			sourceLayer.setAnchors_( None )
		
		if anch_from > 0:
			print "- Copying anchors from source layer:"
			for thisAnchor in sourceLayer.anchors:
				anchorName = thisAnchor.name
				anchorPosition = NSPoint( thisAnchor.x, thisAnchor.y )
				newAnchor = GSAnchor( anchorName, anchorPosition )
				print "-- %s (%i, %i)" % ( anchorName, anchorPosition.x, anchorPosition.y )
				targetLayer.addAnchor_( newAnchor )
	
	def copyMetricsFromLayerToLayer( self, sourceLayer, targetLayer ):
		"""Copies width of sourceLayer to targetLayer."""
		sourceWidth = sourceLayer.width
		if targetLayer.width != sourceWidth:
			targetLayer.width = sourceWidth
			print "- Copying width (%.1f)" % sourceWidth
		else:
			print "- Width not changed (already was %.1f)" % sourceWidth

	def buttonCallback( self, sender ):
		Glyphs.clearLog()
		Glyphs.showMacroWindow()
		print "Copy Layer to Layer Protocol:"

		Font = Glyphs.font
		Doc = Glyphs.currentDocument
		selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

		index_from = self.w.master_from.get()
		index_into = self.w.master_into.get()
		compYesNo  = self.w.include_components.get()
		anchYesNo  = self.w.include_anchors.get()
		metrYesNo  = self.w.include_metrics.get()
				
		for thisGlyph in selectedGlyphs:
			try:
				
				print "\nProcessing", thisGlyph.name
				sourcelayer = thisGlyph.layers[ index_from ]
				targetlayer = thisGlyph.layers[ index_into ]
				
				Font.disableUpdateInterface()
				
				# copy paths:
				self.copyPathsFromLayerToLayer( sourcelayer, targetlayer )
				
				# copy components:
				if compYesNo:
					self.copyComponentsFromLayerToLayer( sourcelayer, targetlayer )
					
				# copy anchors:
				if anchYesNo:
					self.copyAnchorsFromLayerToLayer( sourcelayer, targetlayer )
				
				# copy metrics:
				if metrYesNo:
					self.copyMetricsFromLayerToLayer( sourcelayer, targetlayer )
					
				Font.enableUpdateInterface()
			except Exception, e:
				print e
			
		self.w.close()

MasterFiller()
