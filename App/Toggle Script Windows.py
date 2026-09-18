# MenuTitle: Toggle Script Windows
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Toggles visibility of all windows and panels created by Python scripts.
"""

from mekkablue import macroPanelController

controller = macroPanelController()
if controller is None:
	return None
scriptWindow = controller.window()
scriptWindow.setIsVisible_(not scriptWindow.isVisible())
