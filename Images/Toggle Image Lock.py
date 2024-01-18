# MenuTitle: Toggle Image Lock
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Floating Window for toggling the locked status of selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs


class ToggleImageLock(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 250
		windowHeight = 60
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Toggle Image Lock",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		currentWidth = self.w.getPosSize()[2]
		# A tuple of form *(left, top, width, height)* representing the window's
		# position and size.

		self.w.lockButton = vanilla.Button((15, 10, currentWidth / 2 - 10, -10), u"🔒 Lock", sizeStyle='regular', callback=self.ToggleImageLockMain)
		self.w.unlockButton = vanilla.Button((currentWidth / 2 + 10, 10, -15, -10), u"🔓 Unlock", sizeStyle='regular', callback=self.ToggleImageLockMain)
		self.w.setDefaultButton(self.w.unlockButton)
		self.w.bind("resize", self.resizeButtons)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def resizeButtons(self, sender):
		currentWidth = self.w.getPosSize()[2]
		print(currentWidth)
		self.w.lockButton.setPosSize((15, 10, currentWidth / 2 - 10, -10))
		self.w.unlockButton.setPosSize((currentWidth / 2 + 10, 10, -15, -10))

	def ToggleImageLockMain(self, sender):
		try:
			lockedStatus = True
			if sender == self.w.unlockButton:
				lockedStatus = False

			thisFont = Glyphs.font  # frontmost font
			listOfSelectedLayers = thisFont.selectedLayers  # active layers of currently selected glyphs
			for thisLayer in listOfSelectedLayers:  # loop through layers
				if thisLayer.backgroundImage:
					thisLayer.backgroundImage.locked = lockedStatus
					if thisLayer.parent:
						status = "Locked" if thisLayer.backgroundImage.locked else "Unlocked"
						print("%s image in %s." % (status, thisLayer.parent.name))
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Toggle Image Lock Error: %s" % e)


ToggleImageLock()
