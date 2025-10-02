#MenuTitle: Reset Plugin Manager Repo
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Deletes the selected Plugin Manager repository. Fixes the dreaded ‘Failed to get HEAD (unborn)’ error in Plugin Manager.
"""

import vanilla, sys
from mekkablue import *
from os import listdir, path
from shutil import rmtree
from subprocess import run


def listSubfolders(folder):
	folder = path.expanduser(folder)
	return sorted([name for name in listdir(folder) if path.isdir(path.join(folder, name))])


def removeFolder(baseFolder, folderName):
	baseFolder = path.expanduser(baseFolder)
	folderPath = path.join(baseFolder, folderName)
	if path.isdir(folderPath):
		rmtree(folderPath)
		return True
	else:
		return False


def openFolder(folderPath):
	folderPath = path.expanduser(folderPath)
	if path.isdir(folderPath):
		run(['open', folderPath])
		return True
	else:
		return False


class ResetPluginManagerRepo(mekkaObject):
	repoFolder = "~/Library/Application Support/Glyphs 3/Repositories/"
	
	prefID = "com.mekkablue.ResetPluginManagerRepo"
	prefDict = {
		# "prefName": defaultValue,
		"repositoryIndex": 0,
	}
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 120
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Reset Plugin Manager Repo", # window title
			minSize = (windowWidth, windowHeight), # minimum size (for resizing)
			maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Delete a repository, then try again in Plugin Manager:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.repositoryIndex = vanilla.PopUpButton((inset, linePos, -inset-20, 17), listSubfolders(self.repoFolder), sizeStyle="small", callback=self.SavePreferences)
		self.w.repositoryIndex.getNSPopUpButton().setToolTip_("Select the repository that gave you the error in Plugin Manager and delete it with the Zap button. Then reopen Plugin Manager and try installing it again.")

		self.w.repositoryUpdate = UpdateButton((-inset-16, linePos-2, -inset, 18), callback=self.updateUI)
		self.w.repositoryUpdate.setToolTip("Click to reload the contents of the Repositories folder. Useful if you made manual changes and the contents of the pop-up menu do not yet reflect the state of the Repositories folder.")
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Zap", sizeStyle="regular", callback=self.ResetPluginManagerRepoMain)
		self.w.setDefaultButton(self.w.runButton)
		
		# Load Settings:
		if not self.LoadPreferences():
			print("⚠️ ‘Reset Plugin Manager Repo’ could not load preferences. Will resort to defaults.")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def updateUI(self, sender=None):
		repositories = listSubfolders(self.repoFolder)
		currentIndex = self.w.repositoryIndex.get()
		if currentIndex >= len(repositories) + 1:
			currentIndex = 0
		self.w.repositoryIndex.setItems(repositories)
		self.w.repositoryIndex.set(currentIndex)
		self.w.makeKey()


	def ResetPluginManagerRepoMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			repos = self.w.repositoryIndex.getItems()
			index = self.pref("repositoryIndex")
			repoName = repos[index]
			print(f"Removing repository ‘{repoName}’...")
			
			success = removeFolder(self.repoFolder, repoName)
			if success:
				print(f"✅ Successfully removed ‘{repoName}’")
			else:
				print(f"❌ Error: could not delete ‘{repoName}’.")
				Message(
					title="Could not remove folder",
					message=f"Something went wrong, and apparently ‘{repoName}’ was not deleted. Open the repo folder and inspect yourself.",
					OKButton="Open Repositories",
					)
				openFolder(self.repoFolder)

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("⚠️ ‘Reset Plugin Manager Repo’ could not write preferences.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Reset Plugin Manager Repo Error: {e}")
			import traceback
			print(traceback.format_exc())


ResetPluginManagerRepo()