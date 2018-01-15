#MenuTitle: Make smcp from c2sc
# -*- coding: utf-8 -*-
__doc__="""
Makes component based smcp glyphs, using the c2sc glyphs as components.
Ignores selected glyphs without a .c2sc ending.
"""



Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers if x.parent.name[-5:] == ".smcp" ]

def c2scToSmcpName( c2scname ):
	"""Turns 'Aacute.c2sc' into 'aacute.smcp'."""
	glyphname = c2scname[:c2scname.find(".")].lower()
	suffix = c2scname[c2scname.find("."):].replace("c2sc", "smcp")
	return glyphname + suffix

def process( c2scGlyph ):
	
	# Check if the smcpGlyph already exists
	c2scName = c2scGlyph.name
	smcpName = c2scToSmcpName( c2scGlyph.name )
	
	if Font.glyphs[ smcpName ] == None:

		# Create the smcpGlyph:
		smcpGlyph = GSGlyph()
		smcpGlyph.name = smcpName
		Font.glyphs.append( smcpGlyph ) # now there must be a Font.glyphs[ smcpName ]
	
		# Fill up smcpGlyph's layers with corresponding c2scGlyphs as components:
		smcpGlyph = Font.glyphs[ c2scName ]
		print "Processing %s >>> %s (%i layers):" % (c2scGlyph.name, smcpGlyph.name, len([l for l in smcpGlyph.layers]))

		for m in range(len( Font.masters )):
			currentMaster = Font.masters[ m ]
			currentLayer = smcpGlyph.layers[ currentMaster.id ]
			print "   Master: %s" % currentMaster.name
			c2scComponent = GSComponent( c2scName )
			currentLayer.components.append( c2scComponent )

	else:
		print "%s already exists." % c2scName

Font.disableUpdateInterface()

for thisGlyph in selectedGlyphs:
	process( thisGlyph )

Font.enableUpdateInterface()
