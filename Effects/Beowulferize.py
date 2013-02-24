#MenuTitle: Beowulferize
"""Turns selected glyphs into a pseudorandom Beowulf-lookalike."""

# Please adjust to your own needs:

alphabets = 5    # how many variants of each glyph will be created
shatter = 12     # how far each single node may be moved each time
reiterations = 2 # how often a node may be moved
linelength = 70  # maximum number of letters in a line for which the feature works

import GlyphsApp
import random
random.seed()

Doc         = Glyphs.currentDocument
Font        = Glyphs.font
glyphen     = [ x.parent for x in Doc.selectedLayers() ]
listOfNames = [ thisGlyph.name for thisGlyph in glyphen ]

def randomize( min, max ):
	return random.randint( min, max )

def glyphcopy( source, target ):
	sourceGlyph = glyphen[ source ]
	targetGlyph = sourceGlyph.copy()
	glyphen.append( targetGlyph )
	Font.glyphs.append(targetGlyph)

def process( thisGlyph ):
	FontMaster = Doc.selectedFontMaster()
	thisLayer = thisGlyph.layers[FontMaster.id]
	
	thisGlyph.undoManager().beginUndoGrouping()

	for thisPath in thisLayer.paths:
		for thisNode in thisPath.nodes:
			randomize_x = randomize( -shatter, shatter )
			randomize_y = randomize( -shatter, shatter )
			thisNode.x = thisNode.x + randomize_x
			thisNode.y = thisNode.y + randomize_y

	thisGlyph.undoManager().endUndoGrouping()



print "Beowulferizing " + str(Font.familyName)
glyphsToProcess = glyphen[:]
Font.disableUpdateInterface()



# Create Glyph Variants:

print 'Creating alternative glyphs for:',
for thisGlyph in glyphen:
	print thisGlyph.name,
	for runde in range( alphabets ):
		newName = thisGlyph.name+".calt"+str(runde)
		targetGlyph = thisGlyph.copy()
		targetGlyph.name = newName
		glyphsToProcess.append( targetGlyph )
		Font.glyphs.append( targetGlyph )

print "\nDeforming glyphs",
for thisGlyph in glyphsToProcess:
	print ".",
	for iteration in range( reiterations ):
		process( thisGlyph )



# Create Classes:

print "\nCreating OT class: @default"
defaultclass = GSClass()
defaultclass.name = "@default"
defaultclass.code = " ".join( listOfNames )
Font.classes.append( defaultclass )

for i in range(alphabets):
	mynewclass = GSClass()
	mynewclass.name = "@calt"+str(i)
	mynewclass.code = " ".join( [glyphName+".calt"+str(i) for glyphName in listOfNames] )
	Font.classes.append( mynewclass )
	print "Creating OT class: " + mynewclass.name



# Create OT Feature:

print "Creating OT feature: calt"
myNewFeature = GSFeature()
myNewFeature.name = "calt"
featuretext = ""
for i in range( (alphabets * ( linelength//alphabets ) + 1), 0, -1 ):
	newline = "  sub @default' " + "@default "*i + "by @calt"+str( (range(alphabets)*((linelength//alphabets)+2))[i] )+";\n"
	featuretext = featuretext + newline
myNewFeature.code = featuretext
Font.features.append(myNewFeature)

Font.enableUpdateInterface()
