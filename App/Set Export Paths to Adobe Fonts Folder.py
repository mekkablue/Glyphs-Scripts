#MenuTitle: Set Export Paths to Adobe Fonts Folder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Sets the OpenType font and Variable Font export paths to the Adobe Fonts Folder.
"""

import subprocess

def executeCommand( command, commandArgs ):
	commandExecution = subprocess.Popen( command.split(" ")+commandArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	output, error = commandExecution.communicate()
	returncode = commandExecution.returncode
	return returncode, output, error

adobeFontsFolder = "/Library/Application Support/Adobe/Fonts"

# Make sure the folder actually exists:
pathSegments = adobeFontsFolder.split("/")[1:]
path = ""
for pathPart in pathSegments:
	path += "/%s" % pathPart
	returncode, output, error = executeCommand( "cd", [path] )
	if returncode != 0 and "No such file or directory" in error:
		print("Creating directory: %s" % path)
		returncode, output, error = executeCommand( "mkdir", [path] )
		if returncode != 0:
			print("   Returncode: %s\n   Output: %s\n   Error: %s" % ( returncode, output, error ))

# Changing the export paths for Glyphs:
settings = ( "GXExportPath", "OTFExportPath" )

# Floating notification:
Glyphs.showNotification( 
	u"Export Paths Reset Successfully",
	u"Static and variable fonts now export to Adobe Fonts Folder. More details in Macro Window.",
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
