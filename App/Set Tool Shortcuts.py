# MenuTitle: Set Tool Shortcuts
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Set Shortcuts for tools in toolbar.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject

shortcuts = {
	"AnnotationTool": "a",
	"DrawTool": "p",
	"HandTool": "h",
	"MeasurementTool": "l",
	"OtherPathsTool": "e",
	"PenTool": "b",
	"PrimitivesTool": "f",
	"SelectTool": "v",
	"SelectAllLayersTool": "v",
	"TextTool": "t",
	"RotateTool": "r",
	"ScaleTool": "s",
	"TrueTypeTool": "i",
	"ZoomTool": "z",
}


class SetToolShortcuts(mekkaObject):

	def __init__(self):
		position = 14
		lineheight = 23

		# Window 'self.w':
		windowWidth = 200
		windowHeight = lineheight * len(shortcuts) + 20
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Set Tool Shortcuts",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		for tool in sorted(shortcuts.keys()):
			shortcut = Glyphs.defaults["%s.Hotkey" % tool]
			if not shortcut:
				shortcut = shortcuts[tool]
			setattr(self.w, "text_%s" % tool, vanilla.TextBox((15, position + 2, 115, 14), tool, sizeStyle='small'))
			shortcut = shortcut.upper() if shortcut != "ß" else shortcut  # do not capitalize ß because SF font is buggy
			setattr(self.w, "edit_%s" % tool, vanilla.EditText((15 + 115 + 15, position - 1, -15, 20), shortcut, sizeStyle='small', callback=self.changeShortcut))
			exec("self.w.edit_%s.setPlaceholder('%s')" % (tool, tool))
			position += lineheight

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def changeShortcut(self, sender):
		try:
			tool = sender.getPlaceholder()
			newShortcut = sender.get()
			print("%s: '%s'" % (tool, sender.get()))
			if len(newShortcut) > 0:
				if newShortcut:
					sender.set(newShortcut[-1].upper())
					newShortcut = newShortcut[-1].lower()
					Glyphs.defaults["%s.Hotkey" % tool] = newShortcut
					print("New Shortcut for %s: %s" % (tool, newShortcut))
					sender.selectAll()
			else:
				print("Resetting Shortcut for %s: %s" % (tool, newShortcut))
				del Glyphs.defaults["%s.Hotkey" % tool]
				sender.set(shortcuts[tool].upper())

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Tool Shortcuts Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SetToolShortcuts()
