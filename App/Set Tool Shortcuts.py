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
	"AnnotationTool": u"a",
	"DrawTool": u"p",
	"HandTool": u"h",
	"MeasurementTool": u"l",
	"OtherPathsTool": u"e",
	"PenTool": u"b",
	"PrimitivesTool": u"f",
	"SelectTool": u"v",
	"SelectAllLayersTool": u"v",
	"TextTool": u"t",
	"RotateTool": u"r",
	"ScaleTool": u"s",
	"TrueTypeTool": u"i",
	"ZoomTool": u"z",
}


class SetToolShortcuts(mekkaObject):

	def __init__(self):
		position = 14
		lineheight = 23

		# Window 'self.w':
		windowWidth = 200
		windowHeight = lineheight * len(shortcuts) + 40
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			u"Set Tool Shortcuts",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		for tool in sorted(shortcuts.keys()):
			shortcut = Glyphs.defaults["%s.Hotkey" % tool]
			if not shortcut:
				shortcut = shortcuts[tool]
			exec("self.w.text_%s = vanilla.TextBox( (15, %i, 115, 14), u'%s', sizeStyle='small' )" % (tool, position + 2, tool))
			exec(
				"self.w.edit_%s = vanilla.EditText( (15+115+15, %i, -15, 20), u'%s', sizeStyle = 'small', callback=self.changeShortcut )" % (
					tool,
					position - 1,
					shortcut.upper() if shortcut != "ß" else shortcut,  # do not capitalize ß because SF font is buggy
				)
			)
			exec("self.w.edit_%s.setPlaceholder('%s')" % (tool, tool))
			position += lineheight

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def changeShortcut(self, sender):
		try:
			tool = sender.getPlaceholder()
			newShortcut = sender.get()
			print(u"%s: '%s'" % (tool, sender.get()))
			if len(newShortcut) > 0:
				if newShortcut:
					sender.set(newShortcut[-1].upper())
					newShortcut = newShortcut[-1].lower()
					Glyphs.defaults[u"%s.Hotkey" % tool] = newShortcut
					print(u"New Shortcut for %s: %s" % (tool, newShortcut))
					sender.selectAll()
			else:
				print(u"Resetting Shortcut for %s: %s" % (tool, newShortcut))
				del Glyphs.defaults["%s.Hotkey" % tool]
				sender.set(shortcuts[tool].upper())

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(u"Set Tool Shortcuts Error: %s" % e)
			import traceback
			print(traceback.format_exc())


SetToolShortcuts()
