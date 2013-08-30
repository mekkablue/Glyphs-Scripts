#MenuTitle: Replace components
"""Replaces components in selected glyphs (GUI)."""

import vanilla

class Componentreplacer(object):

	def __init__(self):
		self.w = vanilla.FloatingWindow((340, 40), "Replace Components in Selection")

		self.w.text_Component = vanilla.TextBox((15, 12+2, 65, 14), "Replace", sizeStyle='small')
		self.w.Component_name = vanilla.PopUpButton((65, 12, 80, 17), self.GetComponentNames(), sizeStyle='small')
		
		self.w.text_value = vanilla.TextBox((150, 12+2, 55, 14), "by", sizeStyle='small')
		self.w.Component_newname = vanilla.EditText((175, 12, 65, 19), "glyph.alt", sizeStyle='small')

		self.w.replacebutton = vanilla.Button((-80, 12+1, -15, 17), "Replace", sizeStyle='small', callback=self.buttonCallback)
		self.w.setDefaultButton( self.w.replacebutton )

		self.w.open()
			

	def buttonCallback(self, sender):
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		
		old_Component_name  = str( self.w.Component_name.getItems()[self.w.Component_name.get()] )
		new_Component_name  = self.w.Component_newname.get()
		
		for thisLayer in selectedLayers:
			try:
				thisComponent = thisLayer.components[old_Component_name]
				thisComponent.componentName = new_Component_name
			except:
				print "Failed to replace Component in %s." % thisLayer.parent.name
	
	def GetComponentNames(self):
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		myComponentList = set()
		
		for thisLayer in selectedLayers:
			l = thisLayer.components
			for thisComponent in thisLayer.components:
				myComponentList.add(thisComponent.componentName)
		
		return sorted(list(myComponentList))

Componentreplacer()
