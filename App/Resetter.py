# MenuTitle: Resetter
__doc__ = """
Resets Quicklook preview, keyboard shortcuts, and clearing out app prefs, saved app states, autosaves.
"""

import vanilla
from glob import glob
from os import path, remove
from shutil import rmtree
from subprocess import run
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


def removePaths(pattern):
	"""Deletes all files and folders matching the glob pattern. Returns the number of removed items."""
	count = 0
	for itemPath in glob(path.expanduser(pattern)):
		if path.isdir(itemPath):
			rmtree(itemPath)
		else:
			remove(itemPath)
		count += 1
	return count


class Resetter(mekkaObject):
	prefDict = {
		"quicklook": False,
		"shortcuts": False,
		"autosaves": False,
		"savedAppState": False,
		"preferences": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Resetter",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Fix problems by resetting prefs:", sizeStyle="small", selectable=True)

		self.w.quicklook = vanilla.CheckBox("auto", "Reset QuickLook previews in Finder", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.quicklook.setToolTip("Will reset the QuickLook server, perhaps effective only after logging out and back in again.")

		self.w.shortcuts = vanilla.CheckBox("auto", "Reset keyboard shortcuts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.shortcuts.setToolTip("Warning: will delete all your keyboard shortcuts.")

		self.w.autosaves = vanilla.CheckBox("auto", "Delete autosave information", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.autosaves.setToolTip("Removes all Glyphs files from ~/Library/Autosave Information/")

		self.w.savedAppState = vanilla.CheckBox("auto", "Delete saved application state", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.savedAppState.setToolTip("Removes all Glyphs files from ~/Library/Saved Application State/")

		self.w.preferences = vanilla.CheckBox("auto", "Delete app preferences", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.preferences.setToolTip("Warning: also deletes the content of your Macro window tabs.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Reset", callback=self.ResetterMain)
		self.w.runButton.setToolTip("Performs the checked resets.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; let every control hug so the window fits the content:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[quicklook]-(>=inset)-|",
				"H:|-inset-[shortcuts]-(>=inset)-|",
				"H:|-inset-[autosaves]-(>=inset)-|",
				"H:|-inset-[savedAppState]-(>=inset)-|",
				"H:|-inset-[preferences]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[quicklook]-checkRow-[shortcuts]-checkRow-[autosaves]-checkRow-[savedAppState]-checkRow-[preferences]-inset-[runButton]-inset-|",
			],
			metrics={"inset": inset, "gap": 12, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		isAnyThingSelected = any(self.prefBool(prefName) for prefName in self.prefDict.keys())
		self.w.runButton.enable(isAnyThingSelected)

	def resetQuicklook(self):
		print("👩🏻‍💻 Resetting QuickLook Manager")
		return run(["qlmanage", "-r"]).returncode == 0

	def resetShortcuts(self):
		print("👩🏻‍💻 Resetting keyboard shortcuts")
		Glyphs.defaults["GSCommandKeyEquivalents"] = {}
		Glyphs.defaults["NSUserKeyEquivalents"] = None
		return True

	def resetAutosaves(self):
		print("👩🏻‍💻 Resetting autosaves")
		folder = "~/Library/Autosave Information"
		count = removePaths(f"{folder}/com.GeorgSeifert*")
		count += removePaths(f"{folder}/*.glyphs")
		count += removePaths(f"{folder}/*.glyphsproject")
		print(f"\tremoved {count} item{'' if count == 1 else 's'}")
		return True

	def resetSavedAppState(self):
		print("👩🏻‍💻 Resetting saved app states")
		count = removePaths("~/Library/Saved Application State/com.GeorgSeifert*")
		print(f"\tremoved {count} item{'' if count == 1 else 's'}")
		return True

	def resetPreferences(self):
		print("👩🏻‍💻 Resetting app preferences")
		folder = "~/Library/Preferences"
		count = removePaths(f"{folder}/com.GeorgSeifert*")
		count += removePaths(f"{folder}/com.schriftgestaltung*")
		print(f"\tremoved {count} item{'' if count == 1 else 's'}")
		return True

	def ResetterMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()

			# update settings to the latest user input:
			self.SavePreferences()

			print("Report for Resetter\n")
			for prefName in self.prefDict.keys():
				if self.prefBool(prefName):
					resetMethod = getattr(self, f"reset{prefName[0].upper()}{prefName[1:]}")
					if resetMethod():
						print("\t✅ OK\n")
					else:
						print("\t❌ Failed\n")

			print("Done.")
			Glyphs.showNotification("Resetter", "Done! Details in Macro Window.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Resetter Error: {e}")
			import traceback
			print(traceback.format_exc())


Resetter()
