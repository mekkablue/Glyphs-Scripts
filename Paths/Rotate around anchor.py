#MenuTitle: Rotate around anchor
# -*- coding: utf-8 -*-
"""Rotate selected glyphs (or selected paths and components) around a 'rotate' anchor."""

import GlyphsApp
import vanilla

def transformNode( myNode, myTransform ):
	myNode.position = myTransform.transformPoint_( NSMakePoint( myNode.x, myNode.y ) )
	
	return myNode

def transformPath( myPath, myTransform ):
	for thisNode in myPath.nodes:
		transformNode( thisNode, myTransform )
	
	return myPath
	
def transformComponent( myComponent, myTransform ):
	compTransform = NSAffineTransform.transform()
	compTransform.setTransformStruct_( myComponent.transform )
	compTransform.appendTransform_( myTransform )
	t = compTransform.transformStruct()
	tNew = ( t.m11, t.m12, t.m21, t.m22, t.tX, t.tY )
	myComponent.transform = tNew
	
	return myComponent
	
def stepAndRepeatPaths( myPath, myTransform, steps ):
	if steps == 0:
		return [myPath]
	else:
		return [myPath] + stepAndRepeatPaths( transformPath( myPath.copy(), myTransform ), myTransform, steps-1 )

def stepAndRepeatComponents( myComponent, myTransform, steps ):
	if steps == 0:
		return [myComponent]
	else:
		return [myComponent] + stepAndRepeatComponents( transformComponent( myComponent.copy(), myTransform ), myTransform, steps-1 )

class Rotator(object):
	"""GUI for rotating selected glyphs."""

	def __init__(self):
		self.w = vanilla.FloatingWindow((320, 95), "Rotate around anchor")
		
		self.w.anchor_text = vanilla.TextBox((15, 15, 120, 15), "Set 'rotate' anchor to:", sizeStyle = 'small')
		self.w.anchor_x = vanilla.EditText((15+125, 15-3, 40, 15+3), "0", sizeStyle = 'small')
		self.w.anchor_y = vanilla.EditText((15+125+45, 15-3, 40, 15+3), "0", sizeStyle = 'small')
		self.w.anchor_button = vanilla.Button((-80, 15, -15, 15-3), "Set", sizeStyle = 'small', callback = self.setRotateAnchor)
		
		self.w.rotate_text1 = vanilla.TextBox((15, 40, 55, 15), "Rotate by", sizeStyle = 'small')
		self.w.rotate_degrees = vanilla.EditText((15+60, 40-3, 35, 15+3), "10", sizeStyle = 'small')
		self.w.rotate_text2 = vanilla.TextBox((15+60+40, 40, 50, 15), "degrees:", sizeStyle = 'small')
		self.w.rotate_ccw = vanilla.Button((-150, 40, -85, 15-3), u"↺ ccw", sizeStyle = 'small', callback = self.rotate )
		self.w.rotate_cw  = vanilla.Button((-80, 40, -15, 15-3), u"↻ cw", sizeStyle = 'small', callback = self.rotate )
		
		self.w.stepAndRepeat_text1 = vanilla.TextBox((15, 65, 55, 15), "Repeat", sizeStyle = 'small')
		self.w.stepAndRepeat_times = vanilla.EditText((15+60, 65-3, 35, 15+3), "5", sizeStyle = 'small')
		self.w.stepAndRepeat_text2 = vanilla.TextBox((15+60+40, 65, 50, 15), "times:", sizeStyle = 'small')
		self.w.stepAndRepeat_ccw = vanilla.Button((-150, 65, -85, 15-3), u"↺+ ccw", sizeStyle = 'small', callback = self.rotate )
		self.w.stepAndRepeat_cw  = vanilla.Button((-80, 65, -15, 15-3), u"↻+ cw", sizeStyle = 'small', callback = self.rotate )
		
		self.w.open()
		self.setDefaultRotateAnchor()

	def setRotateAnchor(self, sender):
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		
		myRotationCenter = NSPoint()
		myRotationCenter.x = int( self.w.anchor_x.get() )
		myRotationCenter.y = int( self.w.anchor_y.get() )
		myRotationAnchor = GSAnchor( "rotate", myRotationCenter )
				
		for thisLayer in selectedLayers:
			# adds 'rotate' if it doesn't exist, resets it if it exists:
			thisLayer.addAnchor_( myRotationAnchor )
	
	def setDefaultRotateAnchor(self):
		try:
			selectedLayer = Glyphs.currentDocument.selectedLayers()[0]
			rotationAnchor = selectedLayer.anchors["rotate"]
			self.w.anchor_x.set( str( int(rotationAnchor.x) ) )
			self.w.anchor_y.set( str( int(rotationAnchor.y) ) )
		except Exception, e:
			pass
		
	def rotate(self, sender):
		selectedLayers = Glyphs.currentDocument.selectedLayers()
		originatingButton = sender.getTitle()
		
		if "ccw" in originatingButton:
			rotationDirection = 1
		else:
			rotationDirection = -1
			
		rotationCopy = ( "+" in originatingButton )
		if rotationCopy:
			rotationCount = int( self.w.stepAndRepeat_times.get() )
		else:
			rotationCount = 0
			
		if len(selectedLayers) == 1 and selectedLayers[0].selection() != ():
			# rotate individually selected nodes and components
			
			thisLayer = selectedLayers[0]
			thisGlyph = thisLayer.parent
			selection = thisLayer.selection()
			
			rotationCenter = thisLayer.anchors["rotate"]
			rotationX = rotationCenter.x
			rotationY = rotationCenter.y
			rotation  = float( self.w.rotate_degrees.get() ) * rotationDirection
			
			RotationTransform = NSAffineTransform.transform()
			RotationTransform.translateXBy_yBy_( rotationX, rotationY )
			RotationTransform.rotateByDegrees_( rotation )
			RotationTransform.translateXBy_yBy_( -rotationX, -rotationY )
			
			try:
				thisGlyph.beginUndo()
			
				if rotationCount == 0: # simple rotation
					for thisThing in selection:
						if thisThing.__class__ == GSNode:
							thisThing = transformNode( thisThing, RotationTransform )
						elif thisThing.__class__ == GSComponent:
							thisThing = transformComponent( thisThing, RotationTransform )
			
				thisGlyph.endUndo()
			except Exception, e:
				raise e
			
		else:
			# rotate whole layers
			
			for thisLayer in selectedLayers:
				
				thisGlyph = thisLayer.parent
				thisGlyph.beginUndo()
				
				try:
					thisLayer.setDisableUpdates()
				
					rotationCenter = thisLayer.anchors["rotate"]
					rotationX = rotationCenter.x
					rotationY = rotationCenter.y
					rotation  = float( self.w.rotate_degrees.get() ) * rotationDirection
				
					RotationTransform = NSAffineTransform.transform()
					RotationTransform.translateXBy_yBy_( rotationX, rotationY )
					RotationTransform.rotateByDegrees_( rotation )
					RotationTransform.translateXBy_yBy_( -rotationX, -rotationY )
				
					if rotationCount == 0: # simple rotation
						for thisPath in thisLayer.paths:
							thisPath = transformPath( thisPath, RotationTransform )
					
						for thisComponent in thisLayer.components:
							thisComponent = transformComponent( thisComponent, RotationTransform )
					
					else: # step and repeat
						newLayer = GSLayer()
					
						for thisPath in thisLayer.paths:
							newPaths = stepAndRepeatPaths( thisPath.copy(), RotationTransform, rotationCount )[1:]
							for newPath in newPaths:
								newLayer.paths.append( newPath )

						for injectPath in newLayer.paths:
							thisLayer.paths.append( injectPath.copy() )
					
						for thisComponent in thisLayer.components:
							newComponents = stepAndRepeatComponents( thisComponent.copy(), RotationTransform, rotationCount )[1:]
							for newComponent in newComponents:
								newLayer.components.append( newComponent )
							
						for injectComponent in newLayer.components:
							thisLayer.components.append( injectComponent.copy() )
				
					thisLayer.setEnableUpdates()
					thisLayer.updatePath()
				except Exception, e:
					raise e
				
				thisGlyph.endUndo()

Rotator()