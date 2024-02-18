# MenuTitle: Resetter
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Resets Quicklook preview, keyboard shortcuts, and clearing out app prefs, saved app states, autosaves.
"""

import vanilla
from os import system
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


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
		windowWidth = 230
		windowHeight = 205
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Resetter",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Fix problems by resetting prefs:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.quicklook = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reset QuickLook previews in Finder", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.quicklook.getNSButton().setToolTip_("Will reset the QuickLook server, perhaps effective only after logging out and back in again.")
		linePos += lineHeight

		self.w.shortcuts = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reset keyboard shortcuts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.shortcuts.getNSButton().setToolTip_("Warning: will delete all your keyboard shortcuts.")
		linePos += lineHeight

		self.w.autosaves = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete autosave information", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.autosaves.getNSButton().setToolTip_("Removes all Glyphs files from ~/Library/Autosave Information/")
		linePos += lineHeight

		self.w.savedAppState = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete saved application state", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.savedAppState.getNSButton().setToolTip_("Removes all Glyphs files from ~/Library/Saved Application State/")
		linePos += lineHeight

		self.w.preferences = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Delete app preferences", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.preferences.getNSButton().setToolTip_("Warning: also deletes the content of your Macro window tabs.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Reset", callback=self.ResetterMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		isAnyThingSelected = any([self.pref(prefName) for prefName in self.prefDict.keys()])
		self.w.runButton.enable(isAnyThingSelected)

	def terminalCommand(self, input):
		status = system(input)
		if status == "0":
			return "OK"
		return status

	def reset_quicklook(self):
		# reset Finder previews
		print("👩🏻‍💻 Resetting QuickLook Manager")
		return self.terminalCommand("qlmanage -r")

	def reset_shortcuts(self):
		# reset shortcuts
		print("👩🏻‍💻 Resetting keyboard shortcuts")
		Glyphs.defaults["GSCommandKeyEquivalents"] = {}
		Glyphs.defaults["NSUserKeyEquivalents"] = None
		return "OK"

	def reset_autosaves(self):
		print("👩🏻‍💻 Resetting autosaves")
		dir = "~/Library/Autosave Information"  # system() expects backslash-escaped spaces
		return self.terminalCommand('rm -f %s/com.GeorgSeifert*;rm -f %s/*.glyphs;rm -f %s/*.glyphsproject' % (dir, dir, dir))

	def reset_savedAppState(self):
		print("👩🏻‍💻 Resetting saved app states")
		dir = "~/Library/Saved Application State"
		return self.terminalCommand('rm -rf %s/com.GeorgSeifert*' % dir)

	def reset_preferences(self):
		print("👩🏻‍💻 Resetting app preferences")
		dir = "~/Library/Preferences"
		return self.terminalCommand('rm -f %s/com.GeorgSeifert*;rm -f %s/com.schriftgestaltung*' % (dir, dir))

	def ResetterMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()

			# update settings to the latest user input:
			self.SavePreferences()

			for prefName in self.prefs:
				if self.pref(prefName):
					status = getattr(self, "reset_%s" % prefName)()
					if not status:
						status = "no response from system"
					print("💬 Status: %s\n" % status)

			print("Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Resetter Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Resetter()
