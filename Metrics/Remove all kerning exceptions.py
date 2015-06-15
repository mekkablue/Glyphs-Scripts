#MenuTitle: Remove all kerning exceptions
# -*- coding: utf-8 -*-
__doc__="""
Removes all kernings glyph-glyph, group-glyph, and glyph-group; only keeps group-group kerning.
"""

import GlyphsApp

Kerning = Glyphs.font.kerning
ClassExtension = ".rot"

def addToKeysOnAllLevels( d, ext ):
	nd = d.copy()
	while len( nd ) > 0:
		nd.popitem()
	
	for k in d:
		if k[0] == "@":
			if isinstance( d[k], type(d) ):
				d[k] = addToKeysOnAllLevels( d[k], ext )
			
			if ext in k:
				newKeyName = k
			else:
				newKeyName = k+ext

			nd[ newKeyName ] = d[k]
			print "--->", k, d[k]
	
	return nd

def fixGlyphGroups( g ):
	if g.leftKerningGroup	:
		LKG = g.leftKerningGroup
	else:
		LKG = ""
	
	if g.rightKerningGroup:
		RKG = g.rightKerningGroup
	else:
		RKG = ""
	
	if not "rot" in LKG and len(LKG) > 0:
		g.leftKerningGroup = LKG + ".rot"
	
	if not "rot" in RKG and len(RKG) > 0:
		g.rightKerningGroup = RKG + ".rot"
	
	print g.name


for MasterKerningDict in Kerning:
	print "Cleaning up kerning in Master ID", MasterKerningDict, "..."
	Kerning[MasterKerningDict] = addToKeysOnAllLevels( Kerning[MasterKerningDict], ".rot" )
	
for g in Glyphs.font.glyphs:
	fixGlyphGroups( g )
		
print "Done."

