#MenuTitle: Copy Layer to Layer
"""Copies one master to another master in selected glyphs."""

#import GlyphsApp
import vanilla

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

		for i in range( len( Glyphs.currentDocument.font.masters ) ):
			x = Glyphs.currentDocument.font.masters[i]
			myMasterList.append( '%i: %s' % (i, x.name) )
		
		return myMasterList
	
	def MasterChangeCallback(self, sender):
		if self.w.master_from.get() == self.w.master_into.get():
			self.w.copybutton.enable( False )
		else:
			self.w.copybutton.enable( True )

	def buttonCallback(self, sender):
		Font = Glyphs.font
		Doc = Glyphs.currentDocument
		selectedGlyphs = [ x.parent for x in Font.selectedLayers ]

		index_from = self.w.master_from.get()
		index_into = self.w.master_into.get()
		compYesNo  = self.w.include_components.get()
				
		for thisGlyph in selectedGlyphs:
			try:
				Font.disableUpdateInterface()
			
				print "Processing", thisGlyph.name
			
				num_from  = len( thisGlyph.layers[ index_from ].paths )
				num_into  = len( thisGlyph.layers[ index_into ].paths )
				comp_from = len( thisGlyph.layers[ index_from ].components )
				comp_into = len( thisGlyph.layers[ index_into ].components )
			
				if num_into != 0:
					print "- Cleaning out paths in target layer"
					for i in range( num_into )[::-1]:
						del thisGlyph.layers[index_into].paths[i]

				if num_from > 0:
					print "- Copying paths from source layer"
					for thisPath in thisGlyph.layers[index_from].paths:
						newPath = GSPath()

						for n in thisPath.nodes:
							newNode = GSNode()
							newNode.type = n.type
							newNode.setPosition_( (n.x, n.y) )
							newPath.addNode_( newNode )

						newPath.closed = thisPath.closed
						thisGlyph.layers[index_into].paths.append( newPath )

				if comp_into != 0 and compYesNo == True:
					print "- Cleaning out components in target layer"
					for i in range( comp_into )[::-1]:
						del thisGlyph.layers[index_into].components[i]
			
				if comp_from > 0 and compYesNo == True:
					print "- Copying components from source layer:"
					for thisComp in thisGlyph.layers[index_from].components:
						compName = str( thisComp.componentName ) # str() probably not necessary anymore, but once fixed a problem
						newComp = GSComponent( compName )
						print "--", compName
						thisGlyph.layers[index_into].components.append( newComp )
			
				Font.enableUpdateInterface()
			except Exception, e:
				print e
			
		self.w.close()

MasterFiller()
