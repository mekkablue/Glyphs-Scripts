#MenuTitle: Move anchors
"""Move anchors for selected glyphs."""

#import GlyphsApp
import vanilla

class AnchorMover(object):

	def __init__(self):
		self.w = vanilla.FloatingWindow((340, 40), "Move anchors")

		self.w.text_anchor = vanilla.TextBox((15, 12+2, 45, 14), "Move", sizeStyle='small')
		self.w.anchor_name = vanilla.PopUpButton((50, 12, 80, 17), self.GetAnchorNames(), sizeStyle='small', callback=self.AnchorChangeCallback)
		
		self.w.text_value = vanilla.TextBox((135, 12+2, 55, 14), "to height", sizeStyle='small')
		self.w.anchor_value = vanilla.EditText((190, 12, 50, 19), "0.0", sizeStyle='small')
		#self.w.anchor_value.bind( "+", self.ValuePlus1 )

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
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		thisLayer = [ x for x in selectedLayers if x.anchors[anchor_name] ][0] # first available glyph that has this anchor
		x = str( thisLayer.anchors[anchor_name].y ) # get its anchor value
		self.w.anchor_value.set( x )

	def buttonCallback(self, sender):
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		
		anchor_index = self.w.anchor_name.get()
		anchor_name  = str( self.w.anchor_name.getItems()[anchor_index] )
		try:
			anchor_y = float( self.w.anchor_value.get() )
		except:
			anchor_y = 0.0

		for thisLayer in selectedLayers:
			try:
				thisLayer.anchors[anchor_name].y = anchor_y
			except:
				print "Failed to move anchor in " + thisLayer.parent.name + " to " + anchor_y
	
	def GetAnchorNames(self):
		myAnchorList = []
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		
		for thisLayer in selectedLayers:
			l = thisLayer.anchors
			AnchorNames = [l[x].name for x in range(len(l))]

			for thisAnchorName in AnchorNames:
				if thisAnchorName not in myAnchorList:
					myAnchorList.append( str(thisAnchorName) )
		
		return sorted(myAnchorList)

AnchorMover()
