# MenuTitle: Toggle Script Windows
__doc__ = """
Toggles visibility of all windows and panels created by Python scripts.
"""

from mekkablue import macroPanelController

controller = macroPanelController()
if controller:
	scriptWindow = controller.window()
	scriptWindow.setIsVisible_(not scriptWindow.isVisible())
