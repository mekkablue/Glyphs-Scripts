#MenuTitle: Copy kerning classes from smcp to c2sc
# -*- coding: utf-8 -*-
__doc__="""
Goes through all selected .c2sc glyphs that have no kerning classes,
checks if there is a corresponding .smcp glyph,
and if so, copies the .smcp kerning classes to the .c2sc glyph.
"""



Font = Glyphs.font
exceptionlist = [ "Germandbls.c2sc" ]
selectedC2SCs = [ x.parent for x in Font.selectedLayers if x.parent.name[-5:] == ".c2sc" ]

def c2scToSmcpName( c2scname ):
	"""Turns 'Aacute.c2sc' into 'aacute.smcp'."""
	glyphname = c2scname[:c2scname.find(".")].lower()
	suffix = c2scname[c2scname.find("."):].replace("c2sc", "smcp")
	return glyphname + suffix

def process( c2scGlyph ):
	c2scName = c2scGlyph.name
	smcpName = c2scToSmcpName( c2scGlyph.name )
		
	# Check if the smcpGlyph exists
	if Font.glyphs[ smcpName ] != None:
		smcpGlyph = Font.glyphs[ smcpName ]
		c2scGlyph.leftKerningGroup = smcpGlyph.leftKerningGroup
		c2scGlyph.rightKerningGroup = smcpGlyph.rightKerningGroup
		print "Processing %s <<< %s." % (c2scGlyph.name, smcpGlyph.name)
	else:
		print "%s: no %s in font." % (c2scGlyph.name, smcpGlyph.name)

Font.disableUpdateInterface()

for thisGlyph in selectedC2SCs:
	if thisGlyph.name not in exceptionlist and thisGlyph.leftKerningGroup == None and thisGlyph.rightKerningGroup == None:
		process( thisGlyph )

Font.enableUpdateInterface()

