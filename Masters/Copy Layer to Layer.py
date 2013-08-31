#MenuTitle: Copy Layer to Layer
"""Copies one master to another master in selected glyphs."""

#import GlyphsApp
import vanilla
import traceback

class MasterFiller(object):

	def __init__(self):
		self.w = vanilla.FloatingWindow((300, 84), "Copy layer to layer")
		
		self.w.text_1 = vanilla.TextBox((15, 12+2, 120, 14), "Copy paths from", sizeStyle='small')
		self.w.master_from = vanilla.PopUpButton((120, 12, 80, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)
		
		self.w.text_2 = vanilla.TextBox((15, 32+2, 120, 14), "into selection of", sizeStyle='small')
		self.w.master_into = vanilla.PopUpButton((120, 32, 80, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)
		
		self.w.include_components = vanilla.CheckBox((15, 52+2, -100, 20), "Include components", sizeStyle='small', value=True)
		
		self.w.copybutton = vanilla.Button((-80, 52+2, -15, 17), "Copy", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.copybutton )
		
		self.w.open()
		self.w.master_into.set(1)
	
	def GetMasterNames(self):
		myMasterList = []
		Font = Glyphs.font
		i = 0
		for x in Font.masters:
			myMasterList.append( '%i: %s' % (i, x.name) )
			i+=1
		
		return myMasterList
	
	def MasterChangeCallback(self, sender):
		if self.w.master_from.get() == self.w.master_into.get():
			self.w.copybutton.enable( False )
		else:
			self.w.copybutton.enable( True )
	
	def buttonCallback(self, sender):
		Font = Glyphs.font
		selectedGlyphs = [ x.parent for x in Font.selectedLayers ]
		
		index_from = self.w.master_from.get()
		index_into = self.w.master_into.get()
		compYesNo  = self.w.include_components.get()
		
		for thisGlyph in selectedGlyphs:
			thisGlyph.beginUndo()
			try:
				print "Processing", thisGlyph.name
				From_Layer = thisGlyph.layers[ index_from ]
				Into_Layer = thisGlyph.layers[ index_into ]
				
				print "- Copying content from source layer"
				
				Copy = From_Layer.copy()
				Into_Layer.paths = Copy.paths
				if compYesNo:
					Into_Layer.components = Copy.components
				Into_Layer.width = Copy.width
				# Into_Layer.anchors = Copy.anchors
				
			except Exception, e:
				print e
			thisGlyph.endUndo()
			
		self.w.close()

MasterFiller()
