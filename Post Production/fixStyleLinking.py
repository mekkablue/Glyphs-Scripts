"""
python3 fixStyleLinking.py -h     ... help
python3 fixStyleLinking.py *.ttf  ... apply to all TTFs in current dir
"""

from argparse import ArgumentParser
from fontTools import ttLib

# axis value that is the regular one of the axis, and the value it links to (style linking):
REGULAR_VALUES = {"wght": 400, "ital": 0, "slnt": 0}
LINKED_VALUES = {"wght": 700, "ital": 1}  # slnt: the most negative value of the axis, see linkedValueFor()


def linkedValueFor(axisTag, fvarAxes):
	"""Returns the value the regular value links to, or None if there is none."""
	if axisTag in LINKED_VALUES:
		return LINKED_VALUES[axisTag]
	if axisTag == "slnt":
		fvarAxis = fvarAxes.get("slnt")
		if fvarAxis is not None and fvarAxis.minValue < 0:
			return fvarAxis.minValue
	return None


def fixStyleLinking(font):
	"""
	Turns the STAT Format 1 (or 3) axis value of wght=400 and ital=0 (or, if there is no ital axis, slnt=0)
	into a Format 3 (style linking) entry that is elidable (Flags=2) and links to wght=700, ital=1 or slnt=min.
	Keeps AxisIndex, ValueNameID and Value. Returns True if the font was changed.
	"""
	if "STAT" not in font:
		print("  ⚠️ No STAT table. Skipping.")
		return False

	statTable = font["STAT"].table
	axisValueArray = getattr(statTable, "AxisValueArray", None)
	if not axisValueArray or not axisValueArray.AxisValue:
		print("  ⚠️ STAT table has no axis values. Skipping.")
		return False

	axes = [axis.AxisTag for axis in statTable.DesignAxisRecord.Axis]
	fvarAxes = {axis.axisTag: axis for axis in font["fvar"].axes} if "fvar" in font else {}

	if "wght" in axes:
		targetTags = ["wght"]
	else:
		targetTags = []
	if "ital" in axes:
		targetTags.append("ital")
	elif "slnt" in axes:
		targetTags.append("slnt")
	if not targetTags:
		print("  ⚠️ No wght, ital or slnt axis in STAT. Skipping.")
		return False

	changesMade = False
	handledTags = set()
	newAxisValues = []
	for statIndex, statEntry in enumerate(axisValueArray.AxisValue):
		axisTag = axes[statEntry.AxisIndex] if statEntry.AxisIndex < len(axes) else None
		isTarget = axisTag in targetTags and statEntry.Format in (1, 3) and statEntry.Value == REGULAR_VALUES[axisTag]
		if not isTarget:
			if axisTag in targetTags and statEntry.Format == 2 and statEntry.NominalValue == REGULAR_VALUES[axisTag]:
				print(f"  ⚠️ STAT axis value {statIndex}, {axisTag}={statEntry.NominalValue}: Format 2 (range) cannot be turned into style linking. Left as is.")
			newAxisValues.append(statEntry)
			continue

		if axisTag in handledTags:
			print(f"  ⛔️ Deleting STAT axis value {statIndex}, {axisTag}={statEntry.Value}: duplicate of the style linking entry.")
			changesMade = True
			continue

		linkedValue = linkedValueFor(axisTag, fvarAxes)
		if linkedValue is None:
			print(f"  ⚠️ STAT axis value {statIndex}, {axisTag}={statEntry.Value}: no negative value on the fvar axis to link to. Left as is.")
			newAxisValues.append(statEntry)
			continue

		handledTags.add(axisTag)
		oldFormat = statEntry.Format
		oldFlags = statEntry.Flags
		oldLinkedValue = getattr(statEntry, "LinkedValue", None)
		if oldFormat == 3 and oldFlags == 2 and oldLinkedValue == linkedValue:
			print(f"  🏛️ STAT axis value {statIndex}, {axisTag}={statEntry.Value}: already correct.")
		else:
			print(
				f"  🏛️ STAT axis value {statIndex}, {axisTag}={statEntry.Value}: "
				f"Format {oldFormat} → 3, flags {oldFlags} → 2 (elidable), linked value {oldLinkedValue} → {linkedValue}"
			)
			statEntry.Format = 3
			statEntry.Flags = 2
			statEntry.LinkedValue = linkedValue
			changesMade = True
		newAxisValues.append(statEntry)

	for axisTag in targetTags:
		if axisTag not in handledTags:
			print(f"  🤷🏻‍♀️ No Format 1 or 3 STAT axis value for {axisTag}={REGULAR_VALUES[axisTag]}.")

	if changesMade:
		axisValueArray.AxisValue = newAxisValues
		statTable.AxisValueCount = len(newAxisValues)
		# Format 3 requires STAT version 1.1 or later:
		if statTable.Version < 0x00010001:
			statTable.Version = 0x00010001
	return changesMade


def fixStyleLinkingInFile(fontPath):
	"""Fixes the STAT table of the font file, saves it only if something changed. Returns True if saved."""
	font = ttLib.TTFont(fontPath)
	changesMade = fixStyleLinking(font)
	if changesMade:
		font.save(fontPath, reorderTables=False)
		print(f"💾 Saved {fontPath}")
	else:
		print("🤷🏻‍♀️ No changes made. File left unchanged.")
	return changesMade


def main():
	parser = ArgumentParser(
		description="In STAT, turns the Format 1 axis values of wght=400 and ital=0 (or, if there is no ital axis, slnt=0) into Format 3 (style linking) entries, makes them elidable (Flags=2) and sets the linked values wght=700, ital=1, slnt=most negative value of the axis. Keeps AxisIndex, ValueNameID and Value."
	)
	parser.add_argument(
		"fonts",
		nargs="+",  # one or more font names, e.g. *.ttf
		metavar="font",
		help="Any number of OTF or TTF files.",
	)
	fonts = parser.parse_args().fonts
	changed = 0
	for i, fontPath in enumerate(fonts):
		print(f"\n📄 {i + 1}. Fixing style linking in STAT: {fontPath}")
		if fixStyleLinkingInFile(fontPath):
			changed += 1
	print(f"\n✅ Done. Changed {changed} of {len(fonts)} fonts.\n")


if __name__ == "__main__":
	main()
