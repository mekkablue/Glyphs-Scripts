# -*- coding: utf-8 -*-
"""
python3 fixpsname.py -h     ... help
python3 fixpsname.py *.ttf  ... apply to all TTFs in current dir
"""
import fontTools
from fontTools import ttLib
from argparse import ArgumentParser

parser = ArgumentParser(
    description = "Fix Italic PS Names in fvar when they have a double ‘Italic’ signifier. Will rework the corresponding name table entries."
)

parser.add_argument(
    "fonts",
    nargs="+", # one or more font names, e.g. *.otf
    metavar="font",
    help="Any number of OTF or TTF files.",
)

def fixPSnames(otFont):
	anythingChanged = False
	nameTable = otFont["name"]
	for nameTableEntry in nameTable.names:
		nameID = nameTableEntry.nameID
		# print("CHECK3 nameID", nameID) # DEBUG
		nameValue = nameTableEntry.toStr()
		oldName = nameValue
		# print("CHECK4 nameID", nameID, nameValue) # DEBUG
		if nameID in (4, 6, 17):
			for oldParticle in ("Regular Italic", "RegularItalic"):
				if oldParticle in nameValue:
					nameValue = nameValue.replace(oldParticle, "Italic")
		if nameID in (3, 6) or nameID > 255:
			oldName = nameValue
			if "Italic-" in nameValue and nameValue.count("Italic")>1:
				particles = nameValue.split("-")
				for i in range(1, len(particles)):
					particles[i] = particles[i].replace("Italic", "").strip()
					if len(particles[i]) == 0:
						particles[i] = "Regular"
				nameValue = "-".join(particles)
		if nameValue != oldName:
			nameTableEntry.string = nameValue
			anythingChanged = True
			print(f"✅ Changed ID {nameID}: {oldName} → {nameValue}")
	return anythingChanged

arguments = parser.parse_args()
fonts = arguments.fonts
changed = 0
for i, fontpath in enumerate(fonts):
	print(f"\n📄 {i+1}. {fontpath}")
	font = ttLib.TTFont(fontpath)
	changesMade = fixPSnames(font)
	if changesMade:
		changed += 1
		font.save(fontpath, reorderTables=False)
		print(f"💾 Saved {fontpath}")
	else:
		print(f"🤷🏻‍♀️ No changes made. File left unchanged.")

print(f"\n✅ Done. Changed {changed} of {i+1} fonts.\n")
