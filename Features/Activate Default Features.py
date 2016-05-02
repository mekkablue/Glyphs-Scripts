#MenuTitle: Activate Default Features
# -*- coding: utf-8 -*-
__doc__="""
Activates all features that should be on by default.
"""

defaultFeatures = """
ccmp
liga
calt
"""

thisFont = Glyphs.font # frontmost font
defaultFeatures = defaultFeatures.strip().splitlines()
availableDefaultFeatures = [f.name for f in thisFont.features if f.name in defaultFeatures]

editTab = Glyphs.currentDocument.windowController().activeEditViewController()
for featureName in availableDefaultFeatures:
	if not featureName in editTab.selectedFeatures():
		editTab.selectedFeatures().append(featureName)

editTab.graphicView().reflow()
editTab._updateFeaturePopup()
