#MenuTitle: Add Adobe Symbol Glyphs
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Will add Adobe’s interpolations for a number of symbol glyphs if they are missing from the font: Omega, Delta, Ohm, increment, asciicircum, greaterequal, infinity, partialdiff, lessequal, notequal, product, approxequal, plus, lozenge, integral, summation, radical, daggerdbl, perthousand, logicalnot, plusminus, asciitilde, divide, minus, multiply, dagger, less, equal, greater, literSign, .notdef.

Requires makeotf (AFDKO) to be installed.
"""

from Foundation import NSString
from os import system, path, mkdir
from time import sleep
import subprocess

glyphNames = """
Omega
Delta
Ohm
increment
asciicircum
greaterequal
infinity
partialdiff
lessequal
notequal
product
approxequal
plus
lozenge
integral
summation
radical
daggerdbl
perthousand
logicalnot
plusminus
asciitilde
divide
minus
multiply
dagger
less
equal
greater
literSign
.notdef
"""

def addSansOrSerif(fontName):
	sansTriggers = ("Sans", "Grotesk", "Grotesque", "Linear", "Mono")
	for trigger in sansTriggers:
		if trigger in fontName:
			return " -sans"
			
	serifTriggers = ("Serif", "Text", "Slab")
	for trigger in serifTriggers:
		if trigger in fontName:
			return " -serif"
	
	return ""

# brings macro window to front and clears its log:
Glyphs.clearLog()
Glyphs.showMacroWindow()

font = Glyphs.font
appSupportFolder = GSGlyphsInfo.applicationSupportPath()
exportFolder = appSupportFolder.stringByAppendingPathComponent_("Temp/Symbols")
# "~/Library/Application Support/Glyphs 3/Temp/Symbols"
if not path.isdir(path.expanduser(exportFolder)):
	mkdir(path.expanduser(exportFolder))
fileName = "deleteme"
fileNameSymbols = f"{fileName}-symbols"
filePath = f"{exportFolder}/{fileName}.otf"
filePathSymbols = f"{exportFolder}/{fileNameSymbols}.otf"
absoluteFilePath =  path.expanduser(filePath)
absoluteFilePathSymbols =  path.expanduser(filePathSymbols)
symbolGlyphNames = [n.strip() for n in glyphNames.strip().splitlines() if n.strip()]
emptyCommand = f"rm -f '{exportFolder}/*.otf'"
# /usr/local/bin/
command = f"PATH='/usr/local/bin'; makeotf -f '{absoluteFilePath}' -o '{absoluteFilePathSymbols}' -nS -addn -adds"
command += addSansOrSerif(font.familyName)

print(command)

generatedGlyphNames = []
for master in font.masters:
	print(f"\nⓂ️ Processing {master.name} ({OTF} {fileNameSymbols})...")
	system(emptyCommand) # empty out target folder
	instance = GSInstance()
	instance.font = font
	instance.name = f"TEMP {master.name}"
	instance.axes = master.axes
	instance.manualInterpolation = True
	instance.instanceInterpolations = {master.id: 1.0}
	instance.customParameters["fileName"] = fileName
	instance.customParameters["Remove Glyphs"] = symbolGlyphNames
	success = instance.generate(
		Format=OTF, #format
		FontPath=exportFolder, # fontPath
		AutoHint=False, # autoHint
		RemoveOverlap=True, #removeOverlap
		UseSubroutines=False, #useSubroutines
		UseProductionNames=True, #useProductionNames
		Containers=[PLAIN], #containers
		)
	
	print("🍻 Exported master as font:", success)
	if success!=True:
		print("☹️ Aborted.")
		continue
	
#	sleep(3)
#	result = system(command)
#	result = subprocess.check_output(command, shell=True, text=True)
	result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, text=True)
#	print(result.communicate())
	
	symbolFont = Glyphs.open(absoluteFilePathSymbols, showInterface=False)
	if symbolFont:
		print(f"🥂 Reopened OTF: {symbolFont.familyName} {symbolFont.instances[0].name}")
		font.disableUpdateInterface()
		for g in symbolFont.glyphs:
			niceName = Glyphs.niceGlyphName(g.name).replace("Omega","Ohm").replace("Delta","increment")
			if niceName in symbolGlyphNames:
				targetGlyph = font.glyphs[niceName]
				if not targetGlyph:
					print(f"🌟 Creating {niceName}...")
					targetGlyph = GSGlyph()
					targetGlyph.name = niceName
					font.glyphs.append(targetGlyph)
				targetLayer = targetGlyph.layers[master.id]
				if targetLayer and not targetLayer.shapes:
					print(f"🔤 Adding shapes: {niceName}, layer {targetLayer.name}")
					symbolLayer = g.layers[0]
					targetLayer.shapes = symbolLayer.shapes
					targetLayer.width = symbolLayer.width
		symbolFont.close(ignoreChanges=True)
		font.enableUpdateInterface()

print("\n✅ Done.")