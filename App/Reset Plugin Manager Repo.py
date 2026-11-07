# MenuTitle: Reset Plugin Manager Repo
__doc__ = """
Deletes the selected Plugin Manager repository. Fixes the dreaded ‘Failed to get HEAD (unborn)’ error in Plugin Manager.
"""

import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
	NSLineBreakByTruncatingTail,
	NSColor,
)
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, UpdateButton
from os import listdir, path
from shutil import rmtree
from subprocess import run


def listSubfolders(folder):
	folder = path.expanduser(folder)
	if not path.isdir(folder):
		return []
	return sorted(name for name in listdir(folder) if path.isdir(path.join(folder, name)))


def removeFolder(baseFolder, folderName):
	baseFolder = path.expanduser(baseFolder)
	folderPath = path.join(baseFolder, folderName)
	if not path.isdir(folderPath):
		return False
	try:
		rmtree(folderPath)
	except OSError as e:
		print(f"❌ {e}")
		return False
	return True


def openFolder(folderPath):
	folderPath = path.expanduser(folderPath)
	if path.isdir(folderPath):
		run(["open", folderPath])
		return True
	else:
		return False


class ResetPluginManagerRepo(mekkaObject):
	repoFolder = "~/Library/Application Support/Glyphs 3/Repositories/"

	prefDict = {
		"repositoryIndex": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Reset Plugin Manager Repo",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Delete a repository, then try again in Plugin Manager:", sizeStyle="small", selectable=True)

		repositories = listSubfolders(self.repoFolder)
		self.w.repositoryIndex = vanilla.PopUpButton("auto", repositories, sizeStyle="regular", callback=self.SavePreferences)
		self.w.repositoryIndex.setToolTip("Select the repository that gave you the error in Plugin Manager and delete it with the Zap button. Then reopen Plugin Manager and try installing it again.")
		# long repository names truncate instead of widening the window:
		self.w.repositoryIndex.getNSPopUpButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.repositoryUpdate = UpdateButton("auto", callback=self.reloadRepositories)
		self.w.repositoryUpdate.setToolTip("Click to reload the contents of the Repositories folder. Useful if you made manual changes and the contents of the pop-up menu do not yet reflect the state of the Repositories folder.")

		# Status line, on the height of the Run button:
		self.w.statusText = vanilla.TextBox("auto", "", sizeStyle="small")
		nsStatus = self.w.statusText.getNSTextField()
		nsStatus.setTextColor_(NSColor.tertiaryLabelColor())
		nsStatus.setLineBreakMode_(NSLineBreakByTruncatingTail)
		# a long message truncates instead of widening the window:
		nsStatus.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Zap", callback=self.ResetPluginManagerRepoMain)
		self.w.runButton.setToolTip("Deletes the selected repository folder.")
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[repositoryIndex]-gap-[repositoryUpdate(24)]-inset-|",
				"H:|-inset-[statusText]-gap-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[repositoryIndex]-inset-[runButton]-inset-|",
				{"view1": self.w.repositoryUpdate, "attribute1": "centerY", "view2": self.w.repositoryIndex, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# the folder content may have changed since the index was saved:
		if not 0 <= self.pref("repositoryIndex") < len(repositories):
			self.setPref("repositoryIndex", 0)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.runButton.enable(bool(self.w.repositoryIndex.getItems()))

	def setStatus(self, message):
		self.w.statusText.set(message)
		self.w.statusText.setToolTip(message)

	def reloadRepositories(self, sender=None):
		repositories = listSubfolders(self.repoFolder)
		currentIndex = self.w.repositoryIndex.get()
		if currentIndex >= len(repositories):
			currentIndex = 0
		self.w.repositoryIndex.setItems(repositories)
		if repositories:
			self.w.repositoryIndex.set(currentIndex)
		self.SavePreferences()
		self.w.makeKey()

	def ResetPluginManagerRepoMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			print("Report for Reset Plugin Manager Repo\n")

			repos = self.w.repositoryIndex.getItems()
			if not repos:
				print(f"⚠️ No repositories found in {self.repoFolder}")
				self.setStatus("⚠️ No repositories found")
				return
			repoName = repos[self.w.repositoryIndex.get()]
			print(f"Removing repository ‘{repoName}’...")

			success = removeFolder(self.repoFolder, repoName)
			if success:
				print(f"\t✅ Successfully removed ‘{repoName}’")
				self.setStatus(f"✅ Removed ‘{repoName}’")
				Glyphs.showNotification("Reset Plugin Manager Repo", f"Removed ‘{repoName}’. Reopen Plugin Manager and try again.")
			else:
				print(f"\t❌ Error: could not delete ‘{repoName}’.")
				self.setStatus(f"❌ Could not delete ‘{repoName}’")
				Message(
					title="Could not remove folder",
					message=f"Something went wrong, and apparently ‘{repoName}’ was not deleted. Open the repo folder and inspect yourself.",
					OKButton="Open Repositories",
				)
				openFolder(self.repoFolder)

			# the removed repository must not stay in the pop-up menu:
			self.reloadRepositories()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Reset Plugin Manager Repo Error: {e}")
			import traceback
			print(traceback.format_exc())


ResetPluginManagerRepo()
