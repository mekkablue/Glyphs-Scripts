# MenuTitle: Floating Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Floating window for activating features in the frontmost Edit tab.
"""

import vanilla
import traceback
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class FeatureActivator(mekkaObject):

	def __init__(self):
		numOfFeatures = len(Glyphs.font.features)

		self.w = vanilla.FloatingWindow((150, 10 + numOfFeatures * 18), "", autosaveName=self.domain("mainwindow"))
		i = 0
		selectedFeatures = Glyphs.currentDocument.windowController().activeEditViewController().selectedFeatures()
		for feature in Glyphs.font.features:
			featureTag = feature.name
			featureName = feature.fullName()
			exec(
				"self.w.featureCheckBox_%i = vanilla.CheckBox((8, 4 + 18 * i, -8, 18), featureName, sizeStyle='small', callback=self.toggleFeature, value=(featureTag in selectedFeatures) )"
				% i
			)
			exec("self.w.featureCheckBox_%i.getNSButton().setIdentifier_(featureTag)" % i)
			i += 1
		self.w.open()

	def toggleFeature(self, sender):
		try:
			editTab = Glyphs.currentDocument.windowController().activeEditViewController()
			featureTag = sender.getNSButton().identifier()
			featureActive = bool(sender.get())
			if featureActive:
				# add the feature:
				try:
					editTab.selectedFeatures().append(featureTag)
				except:
					editTab.selectedFeatures().addObject_(featureTag)
			else:
				# remove the feature:
				try:
					while True:
						editTab.selectedFeatures().remove(featureTag)
				except:
					pass

			editTab.graphicView().reflow()
			editTab.graphicView().layoutManager().updateActiveLayer()
			editTab._updateFeaturePopup()
			editTab.updatePreview()
		except Exception as e:
			print(e)
			print(traceback.format_exc())
			return False

		return True


FeatureActivator()
