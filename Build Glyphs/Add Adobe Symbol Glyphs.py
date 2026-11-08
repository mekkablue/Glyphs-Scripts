# MenuTitle: Add Adobe Symbol Glyphs
__doc__ = """
Will add Adobe’s interpolations for a number of symbol glyphs if they are missing from the font: Omega, Delta, Ohm, increment, asciicircum, greaterequal, infinity, partialdiff, lessequal, notequal, product, approxequal, plus, lozenge, integral, summation, radical, daggerdbl, perthousand, logicalnot, plusminus, asciitilde, divide, minus, multiply, dagger, less, equal, greater, literSign, .notdef.

Requires makeotf (AFDKO) to be installed.
"""

from os import system, path, makedirs
import subprocess
from GlyphsApp import Glyphs, GSGlyphsInfo, GSGlyph, GSInstance, PLAIN

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
if font is None:
	print("⚠️ Add Adobe Symbol Glyphs: No font open.")
else:
	appSupportFolder = GSGlyphsInfo.applicationSupportPath()
	exportFolder = appSupportFolder.stringByAppendingPathComponent_("Temp/Symbols")
	# e.g. "~/Library/Application Support/Glyphs 4/Temp/Symbols"
	makedirs(path.expanduser(exportFolder), exist_ok=True)
	fileName = "deleteme"
	fileNameSymbols = f"{fileName}-symbols"
	filePath = f"{exportFolder}/{fileName}.otf"
	filePathSymbols = f"{exportFolder}/{fileNameSymbols}.otf"
	absoluteFilePath = path.expanduser(filePath)
	absoluteFilePathSymbols = path.expanduser(filePathSymbols)
	symbolGlyphNames = [n.strip() for n in glyphNames.strip().splitlines() if n.strip()]
	emptyCommand = f"rm -f '{exportFolder}'/*.otf"
	command = f"PATH='/usr/local/bin'; makeotf -f '{absoluteFilePath}' -o '{absoluteFilePathSymbols}' -nS -addn -adds"
	command += addSansOrSerif(font.familyName)

	print(command)

	for master in font.masters:
		print(f"\nⓂ️ Processing {master.name} (OTF {fileNameSymbols})...")
		system(emptyCommand)  # empty out target folder
		instance = GSInstance()
		instance.font = font
		instance.name = f"TEMP {master.name}"
		instance.axes = master.axes
		instance.manualInterpolation = True
		instance.instanceInterpolations = {
			master.id: 1.0
		}
		instance.customParameters["fileName"] = fileName
		instance.customParameters["Remove Glyphs"] = symbolGlyphNames
		# keyword names as in GSInstance.generate() in the Glyphs 4 API documentation (docu.glyphsapp.com):
		result = instance.generate(
			format="CFF",  # outlines: CFF or TT
			fontPath=exportFolder,
			autoHint=False,
			removeOverlap=True,
			useSubroutines=False,
			useProductionNames=True,
			containers=[PLAIN],
		)

		# The documentation promises True on success and an error message otherwise, but Glyphs 4
		# returns None on success. So trust the file on disk, and report real error messages:
		if result and result is not True:
			print(f"☹️ Export failed: {result}")
			continue
		if not path.exists(absoluteFilePath):
			print(f"☹️ Export did not create {absoluteFilePath}. Aborted.")
			continue
		print("🍻 Exported master as font:", absoluteFilePath)

		# wait for makeotf to finish before opening its output:
		result = subprocess.run(command, capture_output=True, text=True, shell=True)
		if result.returncode != 0:
			print(f"☹️ makeotf failed ({result.returncode}): {result.stderr or result.stdout}")
			continue

		symbolFont = Glyphs.open(absoluteFilePathSymbols, showInterface=False)
		if symbolFont:
			print(f"🥂 Reopened OTF: {symbolFont.familyName} {symbolFont.instances[0].name}")
			font.disableUpdateInterface()
			for g in symbolFont.glyphs:
				niceName = Glyphs.niceGlyphName(g.name).replace("Omega", "Ohm").replace("Delta", "increment")
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
