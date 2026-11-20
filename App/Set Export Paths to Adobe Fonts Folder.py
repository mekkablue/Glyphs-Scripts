# MenuTitle: Set Export Paths to Adobe Fonts Folder
# -*- coding: utf-8 -*-
__doc__ = """
Sets the OpenType font and Variable Font export paths to the Adobe Fonts Folder.
"""

import os
from GlyphsApp import Glyphs, Message

Glyphs.clearLog()


adobeFontsFolder = "/Library/Application Support/Adobe/Fonts"
# TODO: check if general Library is accessible (W privileges), if not, use ~/Library

# Make sure the folder actually exists:
try:
	if not os.path.isdir(adobeFontsFolder):
		print("Creating directory: %s" % adobeFontsFolder)
		os.makedirs(adobeFontsFolder)
except OSError as e:
	print("Could not create directory %s: %s" % (adobeFontsFolder, e))
	Glyphs.showMacroWindow()

# Changing the export paths for Glyphs:
settings = ("GXExportPath", "OTFExportPath")

# Floating notification:
Message(
	title="Export Paths Reset Successfully",
	message="Static and variable fonts now export to Adobe Fonts Folder. More details in Macro Window.",
	OKButton="🥂 Hurrah",
)

for setting in settings:
	print("Setting %s to %s:" % (setting, adobeFontsFolder), end=' ')
	try:
		Glyphs.defaults[setting] = adobeFontsFolder
		print("OK.")
	except Exception as e:
		print("\nTRACEBACK:")
		import traceback
		print(traceback.format_exc())
		print("\nEXCEPTION:")
		print(e)
