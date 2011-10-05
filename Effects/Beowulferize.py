#MenuTitle: Beowulferize
"""Turns selected glyphs into a pseudorandom Beowulf-lookalike."""

#Bitte den eigenen Beduerfnissen anpassen:
alphabets = 5    # wie viele Varianten angelegt werden sollen
shatter = 12     # wie weit sich jeder einzelne Punkt verschieben darf
reiterations = 2 # wie oft verschoben werden darf
linelength = 70  # Laenge der Zeile, in der das Feature wirkt

import random
import GlyphsApp
#import EasyDialogs

Font        = Glyphs.orderedDocuments()[0].font
Doc         = Glyphs.currentDocument
glyphen     = [ x.parent for x in Doc.selectedLayers() ]
listofnames = [ dieseglyphe.name for dieseglyphe in glyphen ]
random.seed()

def zufall( min, max ):
	return random.randint( min, max )

def glyphcopy( source, target ):
	sourceglyph = glyphen[ source ]
	targetglyph = sourceglyph.copy()
	glyphen.append( targetglyph )
	Font.glyphs.append(targetglyph)

def process( thisglyph ):
	FontMaster = Doc.selectedFontMaster()
	thisglyph.undoManager().disableUndoRegistration()
	thislayer = thisglyph.layers[FontMaster.id]
	for thisPath in thislayer.paths:
		for thisNode in thisPath.nodes:
			zufall_x = zufall( -shatter, shatter )
			zufall_y = zufall( -shatter, shatter )
			thisNode.x = thisNode.x + zufall_x
			thisNode.y = thisNode.y + zufall_y

	thisglyph.undoManager().enableUndoRegistration()

#beometer    = EasyDialogs.ProgressBar("Beowulferizing " + str(Font.familyName), maxval = len( glyphen ) * alphabets * 2 + alphabets + 1, label='Erstelle Variationen')
print "Beowulferizing " + str(Font.familyName)

glyphsToProcess = glyphen[:]
Font.willChangeValueForKey_("glyphs")
#beometer.label( 'Erstelle Glyphen' )
print 'Creating alternative glyphs for:',
for thisGlyph in glyphen:
	print thisGlyph.name,
	for runde in range( alphabets ):
		newname = thisGlyph.name+".calt"+str(runde)
		targetglyph = thisGlyph.copy()
		targetglyph.name = newname
		glyphsToProcess.append( targetglyph )
		Font.glyphs.append(targetglyph)
		#beometer.inc()

Font.didChangeValueForKey_("glyphs")

#beometer.label("Verforme Glyphen")
print "\nDeforming glyphs",
for thisGlyph in glyphsToProcess:
	#for runde in range( alphabets ):
		print ".",
		for iteration in range( reiterations ):
			process( thisGlyph )
			#beometer.inc()

# Klassen
#beometer.label("Erstelle OT-Klasse: @default")
print "\nCreating OT class: @default"
defaultclass = GSClass()
defaultclass.name = "@default"
defaultclass.code = " ".join(listofnames)
Font.classes.append(defaultclass)

for i in range(alphabets):
	mynewclass = GSClass()
	mynewclass.name = "@calt"+str(i)
	mynewclass.code = " ".join([glyphname+".calt"+str(i) for glyphname in listofnames])
	Font.classes.append(mynewclass)
	#beometer.label("Erstelle OT-Klasse: " + mynewclass.name)
	#beometer.inc()
	print "Creating OT class: " + mynewclass.name


# Feature
#beometer.label( "Erstelle OT-Feature: calt" )
#beometer.inc()
print "Creating OT feature: calt"
myNewFeature = GSFeature()
myNewFeature.name = "calt"
featuretext = ""
for i in range( (alphabets * ( linelength//alphabets ) + 1), 0, -1 ):
	newline = "  sub @default' " + "@default "*i + "by @calt"+str((range(alphabets)*((linelength//alphabets)+2))[i])+";\n"
	featuretext = featuretext + newline
myNewFeature.code = featuretext
Font.features.append(myNewFeature)

#del beometer
