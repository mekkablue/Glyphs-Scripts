#MenuTitle: Make smcp from c2sc
"""
Makes component based smcp glyphs,
using the c2sc glyphs as components
"""

import GlyphsApp

Font = Glyphs.orderedDocuments()[0].font
Doc  = Glyphs.currentDocument
FontMaster = Doc.selectedFontMaster()
selectedGlyphs = [ x.parent for x in Doc.selectedLayers() ]

def c2scToSmcpName( c2scname ):
	"""Turns 'Aacute.c2sc' into 'aacute.smcp'."""
	glyphname = c2scname[:c2scname.find(".")].lower()
	suffix = c2scname[c2scname.find("."):].replace("c2sc", "smcp")
	return glyphname + suffix

def process( c2scGlyph ):
	# Check if the smcpGlyph already exists
	smcpName = c2scToSmcpName( c2scGlyph.name )
	if Font.glyphs[ smcpName ] == None:

		# Create the smcpGlyph:
		smcpGlyph = GSGlyph()
		smcpGlyph.name = smcpName
		Font.glyphs.append( smcpGlyph )
	
		# Fill up smcpGlyph's layers with corresponding c2scGlyphs as components:
		c2scComponent = GSComponent( c2scGlyph.name )
		for thisLayer in smcpGlyph.layers:
			thisLayer.components.append( c2scComponent )

Font.willChangeValueForKey_("glyphs")

for thisGlyph in selectedGlyphs:
	print "Processing", thisGlyph.name
	process( thisGlyph )

Font.didChangeValueForKey_("glyphs")

