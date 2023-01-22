#MenuTitle: Fill up Empty Masters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Looks for empty layers and copies contents of another layer into it.
"""

import vanilla

class MasterFiller(object):

	def __init__(self):
		self.w = vanilla.FloatingWindow((300, 60), "Fill up Masters")

		self.w.text_1 = vanilla.TextBox((15, 12 + 2, 120, 14), "Copy paths from", sizeStyle='small')
		self.w.master_from = vanilla.PopUpButton((120, 12, 80, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)

		self.w.text_2 = vanilla.TextBox((15, 32 + 2, 120, 14), "into selection of", sizeStyle='small')
		self.w.master_into = vanilla.PopUpButton((120, 32, 80, 17), self.GetMasterNames(), sizeStyle='small', callback=self.MasterChangeCallback)

		self.w.copybutton = vanilla.Button((-80, 32, -15, 17), "Copy", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton(self.w.copybutton)

		self.w.open()
		self.w.master_into.set(1)

	def GetMasterNames(self):
		myMasterList = []

		for i, master in enumerate(Glyphs.font.masters):
			myMasterList.append('%i: %s' % (i, master.name))

		return myMasterList

	def MasterChangeCallback(self, sender):
		if self.w.master_from.get() == self.w.master_into.get():
			self.w.copybutton.enable(False)
		else:
			self.w.copybutton.enable(True)

	def buttonCallback(self, sender):
		selectedGlyphs = [x.parent for x in Glyphs.font.selectedLayers]

		index_from = self.w.master_from.get()
		index_into = self.w.master_into.get()

		for thisGlyph in selectedGlyphs:
			sourceLayer = thisGlyph.layers[index_from]
			targetLayer = thisGlyph.layers[index_into]

			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				targetLayerIsEmpty = len(targetLayer.shapes) == 0
			else:
				# GLYPHS 2
				targetLayerIsEmpty = all(
					len(targetLayer.paths) == 0,
					len(targetLayer.components) == 0,
					)

			if targetLayerIsEmpty:

				if len(targetLayer.anchors) == 0:
					for originalAnchor in sourceLayer.anchors:
						newAnchor = originalAnchor.copy()
						targetLayer.anchors.append(newAnchor)

				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					targetLayer.shapes = sourceLayer.shapes.copy()
				else:
					# GLYPHS 2
					for originalPath in sourceLayer.paths:
						newPath = GSPath()
						for originalNode in originalPath.nodes:
							newNode = originalNode.copy()
							newPath.nodes.append(newNode)
						newPath.closed = originalPath.closed
						targetLayer.paths.append(newPath)

					for originalComponent in sourceLayer.components:
						print(originalComponent)
						newComponent = originalComponent.copy()
						targetLayer.components.append(newComponent)

				targetLayer.width = sourceLayer.width

		self.w.close()

MasterFiller()
