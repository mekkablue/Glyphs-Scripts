#MenuTitle: Create pseudorandom calt feature from ssXX glyphs
"""Create pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font."""

Font           = Glyphs.orderedDocuments()[0].font
Doc            = Glyphs.currentDocument
allGlyphs  = [ x.name for x in list( Font.glyphs ) ]
linelength     = 70

def ssXXsuffix(i):
	"""Turns an integer into an ssXX ending between .ss01 and .ss20, e.g. 5 -> '.ss05'."""
	if i < 1:
		i = 1
	elif i > 20:
		i = 20
	return ".ss"+("00"+str(i))[-2:]

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
	exit()
else:
	print "Creating classes up to", ssXX, "with", len( ssXXglyphs ), "glyphs."

# defaultclass: a b c ...
defaultglyphs = [x[:-5] for x in ssXXglyphs]
defaultclass = GSClass()
defaultclass.name = "@default"
defaultclass.code = " ".join( defaultglyphs ) + " space"
Font.classes.append( defaultclass )

# ssXXclass: a.ssXX b.ssXX c.ssXX ...
for XX in range(i):
	ssXXClass = GSClass()
	ssXXClass.name = "@calt"+str(XX)
	ssXXClass.code = " ".join( [ x + ssXXsuffix(XX+1) for x in defaultglyphs ] ) + " space"
	print XX, ssXXClass.name
	Font.classes.append( ssXXClass )
	
# OT feature
print "Creating OT feature: calt"
caltFeature = GSFeature()
caltFeature.name = "calt"
featuretext = ""
for j in range( i*(linelength//i+1), 0, -1 ):
	newline = "  sub @default' " + "@default "*j + "by @calt" + str( ( range(i)*(linelength//i+2) )[j] ) + ";\n"
	featuretext = featuretext + newline

caltFeature.code = featuretext
Font.features.append( caltFeature )