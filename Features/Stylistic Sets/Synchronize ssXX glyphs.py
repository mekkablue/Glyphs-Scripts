#MenuTitle: Synchronize ssXX glyphs
# -*- coding: utf-8 -*-
__doc__="""
Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs.
E.g. you have a.ss01 b.ss01 c.ss01 a.ss02 c.ss02 --> the script creates b.ss02
"""

Font       = Glyphs.font
allGlyphs  = [ x.name for x in list( Font.glyphs ) ]
linelength = 70

def ssXXsuffix( i ):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	if i < 1:
		i = 1
	elif i > 20:
		i = 20
	return ".ss%0.2d" % i
	
def stripsuffix( glyphname ):
	"""Returns the glyphname without the dot suffix."""
	dotindex = glyphname.find(".")
	return glyphname[:dotindex]

i = 1
ssXX_exists = True

while ssXX_exists:
	ssXX = ssXXsuffix(i)
	ssXXglyphs = [ x for x in allGlyphs if x.find( ssXX ) is not -1 ]
	if len(ssXXglyphs) == 0:
		i-=1
		ssXX = ssXXsuffix(i)
		ssXXglyphs = [ x for x in allGlyphs if x.find( ssXX ) is not -1 ]
		ssXX_exists = False
	else:
		i+=1

if i == 0:
	print "No ssXX glyphs in the font. Aborting."
else:
	print "Highest ssXX:", ssXX
	print "Creating",
	for XX in range( i ):
	
		ssXXglyphs = [ x for x in allGlyphs if x.find( ssXXsuffix( XX+1 ) ) is not -1 ]
		baseglyphs = [ stripsuffix( x ) for x in ssXXglyphs ]
	
		for YY in range( i ):
			if XX != YY:
				allGlyphs = [ x.name for x in list( Font.glyphs ) ] # neu holen, Glyphen haben sich u.U. schon geaendert
		
				for thisglyphname in baseglyphs:
					targetglyphname = thisglyphname + ssXXsuffix( YY+1 )
			
					if not targetglyphname in allGlyphs:
						sourceglyphname = thisglyphname + ssXXsuffix( XX+1 )
						sourceglyph = Font.glyphs[ sourceglyphname ]
						targetglyph = sourceglyph.copy()
						targetglyph.name = targetglyphname
						Font.glyphs.append( targetglyph )
						print targetglyphname,

	print