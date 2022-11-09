#MenuTitle: Update git Repositories in Scripts Folder
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Executes a 'git pull' command on all subfolders in the Glyphs Scripts folder. Will not work for the Glyphs 3 Repositories folder, which you need to take care of with the Plugin Manager.
"""

from os import system, chdir, path

if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	Message(
		title="Friendly Reminder",
		message=
		"In Glyphs 3 and later, we strongly recommend to manage your scripts with the Plugin Manager (Window → Plugin Manager). Do not manage the script repositories yourself. This script only works on the Scripts folder, not the Repositories folder.",
		OKButton=None,
		)

Glyphs.clearLog()
if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	scriptsFolderPath = "~/Library/Application Support/Glyphs 3/Scripts/"
else:
	# GLYPHS 2
	scriptsFolderPath = "~/Library/Application Support/Glyphs/Scripts/"

expandedScriptsFolderPath = path.expanduser(scriptsFolderPath)
print("Executing 'git pull' for all subfolders in:\n%s" % expandedScriptsFolderPath)

chdir(expandedScriptsFolderPath)
exitStatus = system('find . -mindepth 1 -maxdepth 1 -type d -print -exec git -C {} pull -f \; -exec echo \;')
system('open "%s"' % scriptsFolderPath)

if exitStatus != 0:
	print("ERROR: Exit Status %i" % exitStatus)
	Glyphs.showMacroWindow()
else:
	print("Done.")
	Glyphs.showNotification(
		"Completed git pull",
		scriptsFolderPath,
		)
