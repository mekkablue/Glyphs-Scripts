#MenuTitle: Anchor Mover 1.1
"""Vertically move anchors in selected glyphs (GUI)."""

import GlyphsApp
import vanilla

class AnchorMover(object):
	def __init__(self):
		self.w = vanilla.FloatingWindow((340, 40), "Move anchors")

		self.w.text_anchor = vanilla.TextBox((15, 12+2, 45, 14), "Move", sizeStyle='small')
		self.w.anchor_name = vanilla.PopUpButton((50, 12, 80, 17), self.GetAnchorNames(), sizeStyle='small', callback=self.AnchorChangeCallback)
		
		self.w.text_value = vanilla.TextBox((135, 12+2, 55, 14), "to height", sizeStyle='small')
		self.w.anchor_value = vanilla.EditText((190, 12, 50, 19), "0.0", sizeStyle='small')

		self.w.movebutton = vanilla.Button((-80, 12+1, -15, 17), "Move", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.movebutton )

		self.w.open()
		self.AnchorChangeCallback( self )
		
	def ValuePlus1(self, sender):
		anchor_y = float( self.w.anchor_value.get() )
		self.w.anchor_value.set( str(anchor_y + 1.0) )
	
	def AnchorChangeCallback(self, sender):
		anchor_index = self.w.anchor_name.get()
		anchor_name  = str( self.w.anchor_name.getItems()[anchor_index] )
		selectedLayers = Glyphs.font.selectedLayers
		thisLayer = [ x for x in selectedLayers if x.anchors[anchor_name] ][0] # first available glyph that has this anchor
		x = str( thisLayer.anchors[anchor_name].y ) # get its anchor value
		self.w.anchor_value.set( x )

	def buttonCallback(self, sender):
		selectedLayers = Glyphs.font.selectedLayers
		print "Processing %i glyphs..." % len( selectedLayers )
		
		anchor_index = self.w.anchor_name.get()
		anchor_name  = str( self.w.anchor_name.getItems()[anchor_index] )
		try:
			anchor_y = float( self.w.anchor_value.get() )
		except:
			anchor_y = 0.0
		
		# print anchor_index, anchor_name, anchor_y #DEBUG
		
		for thisLayer in selectedLayers:
			# print "Changing %s in %s..." % (anchor_name, thisLayer.parent.name) #DEBUG
			try:
				if len( thisLayer.anchors ) > 0:
					thisLayer.setDisableUpdates()
					for thisAnchor in thisLayer.anchors:
						if thisAnchor.name == anchor_name:
							old_anchor_y = thisAnchor.y
							if old_anchor_y != anchor_y:
								thisAnchor.y = anchor_y
								print "Moved %s anchor in %s from %s to %s." % ( anchor_name, thisLayer.parent.name, old_anchor_y, thisAnchor.y )
			except:
				print "Error: Failed to move anchor in %s to %s." % ( thisLayer.parent.name, anchor_y )
			finally:
				thisLayer.setEnableUpdates()	
		
		print "Done."
	
	def GetAnchorNames(self):
		myAnchorList = []
		selectedLayers = Glyphs.font.selectedLayers
		
		for thisLayer in selectedLayers:
			AnchorNames = list( thisLayer.anchors.keys() ) # hack to avoid traceback

			for thisAnchorName in AnchorNames:
				if thisAnchorName not in myAnchorList:
					myAnchorList.append( str(thisAnchorName) )
		
		return sorted( myAnchorList )

AnchorMover()
