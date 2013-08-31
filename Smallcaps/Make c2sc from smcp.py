#MenuTitle: Make c2sc from smcp
"""
Makes component based c2sc glyphs, using the smcp glyphs as components.
Ignores selected glyphs without an .smcp ending.
"""

import GlyphsApp

Font = Glyphs.font
selectedGlyphs = [ x.parent for x in Font.selectedLayers if x.parent.name[-5:] == ".smcp" ]

def smcpToC2scName( smcpname ):
	"""Turns 'aacute.smcp' into 'Aacute.c2sc'."""
	if smcpname[0:2] in ["ae","oe","ij"]:
		glyphname = smcpname[0:2].upper() + smcpname[2:smcpname.find(".")]
	else:
		glyphname = smcpname[:smcpname.find(".")].title()
	suffix = smcpname[smcpname.find("."):].replace("smcp", "c2sc")
	return glyphname + suffix

def process( smcpGlyph ):
	
	# Check if the c2scGlyph already exists
	smcpName = smcpGlyph.name
	c2scName = smcpToC2scName( smcpName )
	
	if Font.glyphs[ c2scName ] == None:
		
		# Create the c2scGlyph:
		c2scGlyph = GSGlyph()
		c2scGlyph.name = c2scName
		Font.glyphs.append( c2scGlyph ) # now there must be a Font.glyphs[ c2scName ]
		
		# Fill up c2scGlyph's layers with corresponding smcpGlyphs as components:
		c2scGlyph = Font.glyphs[ c2scName ]
		print "Processing %s >>> %s (%i layers):" % (smcpGlyph.name, c2scGlyph.name, len([l for l in c2scGlyph.layers]))
		
		for m in range(len( Font.masters )):
			currentMaster = Font.masters[ m ]
			currentLayer = c2scGlyph.layers[ currentMaster.id ]
			print "   Master: %s" % currentMaster.name
			smcpComponent = GSComponent( smcpName )
			currentLayer.components.append( smcpComponent )
	else:
		print "%s already exists." % c2scName

for thisGlyph in selectedGlyphs:
	process( thisGlyph )
