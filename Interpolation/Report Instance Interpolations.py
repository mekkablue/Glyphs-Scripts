# MenuTitle: Report Instance Interpolations
__doc__ = """
Outputs master coefficients for each instance in Macro Window. Tells you which masters are involved in interpolating a specific instance, and to which extent.
"""

from GlyphsApp import Glyphs, Message


def reportCoefficients(instance):
	interpolations = instance.instanceInterpolations
	for masterId in interpolations.allKeys():
		master = Glyphs.font.masters[masterId]
		print("   Ⓜ%7.2f%% %s" % (interpolations[masterId] * 100, master.name))


thisFont = Glyphs.font  # frontmost font
if thisFont is None:
	Message(
		title="No Font Open",
		message="The script requires a font. Open a font and run the script again.",
		OKButton=None,
	)
elif not thisFont.instances:
	Message(
		title="No Instances Set",
		message="This font has no instances set up in File > Font Info > %s. Insert instances and run the script again." %
		("Exports" if Glyphs.versionNumber >= 3 else "Instances", ),
		OKButton=None,
	)
else:
	# brings macro window to front and clears its log:
	Glyphs.clearLog()
	Glyphs.showMacroWindow()
	print("Instance Report for %s" % thisFont.familyName)
	fileName = thisFont.filepath.lastPathComponent() if thisFont.filepath else f"{thisFont.familyName} (unsaved)"
	print(f"📄 {fileName}")

	for thisInstance in thisFont.instances:
		if Glyphs.buildNumber > 3198:
			instanceIsExporting = thisInstance.exports
		else:
			instanceIsExporting = thisInstance.active
		print("\n%s %s %s" % (
			"🟢" if instanceIsExporting else "🚫",
			thisInstance.familyName,
			thisInstance.name,
		))
		reportCoefficients(thisInstance)
