#MenuTitle: Remove all Kerning Exceptions
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Removes all kernings glyph-glyph, group-glyph, and glyph-group; only keeps group-group kerning.
"""

Kerning = Glyphs.font.kerning
ClassExtension = "" # e.g. set to ".rot" for testing purposes

def addToKeysOnAllLevels( d, ext ):
	nd = d.copy()
	while len( nd ) > 0:
		nd.popitem()
	
	for k in d:
		if k[0] == "@":
			if isinstance( d[k], type(d) ):
				d[k] = addToKeysOnAllLevels( d[k], ext )
			
			if ext and not ext in k:
				newKeyName = k+ext
			else:
				newKeyName = k

			nd[ newKeyName ] = d[k]
			print("--->", k, d[k])
	
	return nd

def fixGlyphGroups( g, ext ):
	if g.leftKerningGroup	:
		LKG = g.leftKerningGroup
	else:
		LKG = ""
	
	if g.rightKerningGroup:
		RKG = g.rightKerningGroup
	else:
		RKG = ""
	
	if ext:
		if not ext in LKG and len(LKG) > 0:
			g.leftKerningGroup = LKG + ext
	
		if not ext in RKG and len(RKG) > 0:
			g.rightKerningGroup = RKG + ext
	
	print(g.name)


for MasterKerningDict in Kerning:
	print("Cleaning up kerning in Master ID", MasterKerningDict, "...")
	Kerning[MasterKerningDict] = addToKeysOnAllLevels( Kerning[MasterKerningDict], ClassExtension )
	
for g in Glyphs.font.glyphs:
	fixGlyphGroups( g, ClassExtension )
		
print("Done.")

