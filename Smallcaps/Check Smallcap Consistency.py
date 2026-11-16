# MenuTitle: Check Smallcap Consistency
__doc__ = """
Performs a few tests on your SC set and reports into the Macro window, especially kerning groups and glyph set.
"""

from mekkablue import setMacroDivider
from GlyphsApp import Glyphs, GSSmallcaps, GSUppercase, GSLowercase, Message

thisFont = Glyphs.font  # frontmost font
if not thisFont:
	Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()


	def removeSuffix(name, suffixes=("sc", "smcp", "c2sc")):
		particles = name.split(".")
		for suffix in suffixes:
			while suffix in particles:
				particles.remove(suffix)
		return ".".join(particles)

	def uppercased(name):
		particles = name.split(".")
		info = Glyphs.glyphInfoForName(particles[0])
		if info is not None and info.unicharString():
			particles[0] = Glyphs.niceGlyphName(info.unicharString().upper()) or particles[0]
		return ".".join(particles)

	def lowercased(name):
		particles = name.split(".")
		info = Glyphs.glyphInfoForName(particles[0])
		if info is not None and info.unicharString():
			particles[0] = Glyphs.niceGlyphName(info.unicharString().lower()) or particles[0]
		return ".".join(particles)

	setMacroDivider(0.2)

	smallcaps = [g.name for g in thisFont.glyphs if g.case == GSSmallcaps and g.export]
	lowercase = [g.name for g in thisFont.glyphs if g.case == GSLowercase and g.export]
	uppercase = [g.name for g in thisFont.glyphs if g.case == GSUppercase and g.export]

	print(f"Smallcap Consistency for {thisFont.familyName}:")
	print(f"🌈 {len(smallcaps)} exporting smallcap glyphs in font")
	print(f"🔡 {len(lowercase)} exporting lowercase glyphs in font")
	print(f"🔠 {len(uppercase)} exporting uppercase glyphs in font")
	print()

	lowercaseMissing = [n for n in lowercase if f"{n}.sc" not in smallcaps and f"{n}.smcp" not in smallcaps]
	if not lowercaseMissing:
		print("✅🔡 All lowercase glyphs have a smallcap counterpart.")
	else:
		print(f"⚠️🔡 Lowercase glyphs without a smallcap counterpart (.sc or .smcp):\n{', '.join(lowercaseMissing)}")
	print()

	uppercaseMissing = [n for n in uppercase if f"{n}.sc" not in smallcaps and f"{n}.c2sc" not in smallcaps]
	if not uppercaseMissing:
		print("✅🔡 All uppercase glyphs have a smallcap counterpart.")
	else:
		print(f"⚠️🔡 Uppercase glyphs without a smallcap counterpart (.sc or .c2sc):\n{', '.join(uppercaseMissing)}")
	print()

	orphanedSmallcaps = []
	allCased = lowercase + uppercase
	for name in smallcaps:
		unsuffixedName = removeSuffix(name)
		if unsuffixedName in allCased:
			continue
		elif uppercased(unsuffixedName) in allCased:
			continue
		elif lowercased(unsuffixedName) in allCased:
			continue
		orphanedSmallcaps.append(name)
	if not orphanedSmallcaps:
		print("✅🌈 No smallcap glyph without UC or LC counterpart.")
	else:
		print(f"⚠️🌈 Orphaned smallcap glyphs:\n{', '.join(orphanedSmallcaps)}")
	print()
