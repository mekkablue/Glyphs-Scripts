#MenuTitle: Find and Replace in Layer Names
"""
Replaces strings in layer names of all selected glyphs.
Useful for adjusting layers for the bracket trick:
http://glyphsapp.com/blog/alternating-glyph-shapes/
"""

import GlyphsApp
import vanilla

class replaceInLayerNames(object):

	def __init__(self):
		self.w = vanilla.FloatingWindow((380, 40), "Replace text in layer names (ignores Masters)")

		self.w.textSearch = vanilla.TextBox((15, 12+2, 67, 14), "Search for:", sizeStyle='small')
		self.w.searchFor = vanilla.EditText((15+67, 12, 60, 19), "[130]", sizeStyle='small')
		
		self.w.textReplace = vanilla.TextBox((150, 12+2, 67, 14), "Replace by:", sizeStyle='small')
		self.w.replaceBy = vanilla.EditText((150+67, 12, 60, 19), "[150]", sizeStyle='small')

		self.w.replaceButton = vanilla.Button((-80, 12+1, -15, 17), "Replace", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.replaceButton )
		
		self.w.center()
		self.w.open()
	
	def buttonCallback(self, sender):
		Doc  = Glyphs.currentDocument
		Font = Glyphs.font
		selectedLayers = Doc.selectedLayers()
		numberOfMasters = len( Font.masters )
		
		searchFor = self.w.searchFor.get()
		replaceBy = self.w.replaceBy.get()
		
		Font.disableUpdateInterface()
		
		for g in Glyphs.font.glyphs:
			if len( g.layers ) > numberOfMasters:
				for l in [ x for x in g.layers ][numberOfMasters:]:
					if searchFor in l.name:
						l.name = l.name.replace( searchFor, replaceBy )
						print g.name, ":", l.name
		
		Font.enableUpdateInterface()

replaceInLayerNames()
