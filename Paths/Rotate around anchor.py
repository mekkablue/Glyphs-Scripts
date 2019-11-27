#MenuTitle: Rotate Around Anchor
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Rotate selected glyphs (or selected paths and components) around a 'rotate' anchor.
"""

import vanilla
from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct, NSMakePoint

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
		self.w.rotate_degrees = vanilla.EditText((15+60, 40-3, 35, 15+3), "10", sizeStyle = 'small', callback = self.SavePreferences)
		self.w.rotate_text2 = vanilla.TextBox((15+60+40, 40, 50, 15), "degrees:", sizeStyle = 'small')
		self.w.rotate_ccw = vanilla.Button((-150, 40, -85, 15-3), u"↺ ccw", sizeStyle = 'small', callback = self.rotate )
		self.w.rotate_cw  = vanilla.Button((-80, 40, -15, 15-3), u"↻ cw", sizeStyle = 'small', callback = self.rotate )
		
		self.w.stepAndRepeat_text1 = vanilla.TextBox((15, 65, 55, 15), "Repeat", sizeStyle = 'small')
		self.w.stepAndRepeat_times = vanilla.EditText((15+60, 65-3, 35, 15+3), "5", sizeStyle = 'small', callback = self.SavePreferences)
		self.w.stepAndRepeat_text2 = vanilla.TextBox((15+60+40, 65, 50, 15), "times:", sizeStyle = 'small')
		self.w.stepAndRepeat_ccw = vanilla.Button((-150, 65, -85, 15-3), u"↺+ ccw", sizeStyle = 'small', callback = self.rotate )
		self.w.stepAndRepeat_cw  = vanilla.Button((-80, 65, -15, 15-3), u"↻+ cw", sizeStyle = 'small', callback = self.rotate )
		
		if not self.LoadPreferences():
			self.logToConsole( "Rotate: Could not load prefs, will resort to defaults." )
		self.setDefaultRotateAnchor()
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.rotateAroundAnchor.rotate_degrees"] = self.w.rotate_degrees.get()
			Glyphs.defaults["com.mekkablue.rotateAroundAnchor.stepAndRepeat_times"] = self.w.stepAndRepeat_times.get()
			return True
		except:
			return False
			
	def LoadPreferences( self ):
		try:
			self.w.rotate_degrees.set( Glyphs.defaults["com.mekkablue.rotateAroundAnchor.rotate_degrees"] )
			self.w.stepAndRepeat_times.set( Glyphs.defaults["com.mekkablue.rotateAroundAnchor.stepAndRepeat_times"] )
			return True
		except:
			return False

	def setRotateAnchor(self, sender):
		try:
			selectedLayers = Glyphs.currentDocument.selectedLayers()
			myRotationCenter = NSPoint()
			myRotationCenter.x = int( self.w.anchor_x.get() )
			myRotationCenter.y = int( self.w.anchor_y.get() )
			myRotationAnchor = GSAnchor( "rotate", myRotationCenter )
			for thisLayer in selectedLayers:
				# adds 'rotate' if it doesn't exist, resets it if it exists:
				thisLayer.addAnchor_( myRotationAnchor )
		except Exception as e:
			self.logToConsole( "setRotateAnchor: %s" % e )
	
	def setDefaultRotateAnchor(self):
		try:
			selectedLayer = Glyphs.currentDocument.selectedLayers()[0]
			rotationAnchor = selectedLayer.anchors["rotate"]
			self.w.anchor_x.set( int(rotationAnchor.x) )
			self.w.anchor_y.set( int(rotationAnchor.y) )
		except Exception as e:
			self.logToConsole( "setDefaultRotateAnchor: %s" % e )
			
	def stepAndRepeatListOfPaths( self, thisLayer, listOfPaths, RotationTransform, rotationCount ):
		try:
			for thisPath in listOfPaths:
				newPaths = stepAndRepeatPaths( thisPath.copy(), RotationTransform, rotationCount )[1:]
				for newPath in newPaths:
					thisLayer.paths.append( newPath.copy() )
		except Exception as e:
			self.logToConsole( "stepAndRepeatPaths: %s" % e )
			
	def stepAndRepeatListOfComponents( self, thisLayer, listOfComponents, RotationTransform, rotationCount ):
		try:
			for thisComponent in listOfComponents:
				newComponents = stepAndRepeatComponents( thisComponent.copy(), RotationTransform, rotationCount )[1:]
				for newComponent in newComponents:
					thisLayer.components.append( newComponent.copy() )
		except Exception as e:
			self.logToConsole( "stepAndRepeatComponents: %s" % e )
	
	def rotateListOfPaths( self, thisLayer, listOfPaths, RotationTransform, rotationCount ):
		try:
			for thisPath in listOfPaths:
				thisPath = transformPath( thisPath, RotationTransform )
		except Exception as e:
			self.logToConsole( "rotateListOfPaths: %s" % e )
	
	def rotateListOfComponents( self, thisLayer, listOfComponents, RotationTransform, rotationCount ):
		try:
			for thisComponent in listOfComponents:
				thisComponent = transformComponent( thisComponent, RotationTransform )
		except Exception as e:
			self.logToConsole( "rotateListOfComponents: %s" % e )
			
	def rotationCenterOfLayer( self, thisLayer ):
		try:
			rotationCenter = thisLayer.anchors["rotate"]
			if rotationCenter:
				rotationX = rotationCenter.x
				rotationY = rotationCenter.y
			else:
				rotationX = thisLayer.width * 0.5
				rotationY = 0.0
			return NSPoint( rotationX, rotationY )
		except Exception as e:
			self.logToConsole( "rotationCenter: %s" % e )
	
	def rotationTransform( self, rotationCenter, rotationDegrees, rotationDirection ):
		try:
			rotationX = rotationCenter.x
			rotationY = rotationCenter.y#
			rotation  = rotationDegrees * rotationDirection
			RotationTransform = NSAffineTransform.transform()
			RotationTransform.translateXBy_yBy_( rotationX, rotationY )
			RotationTransform.rotateByDegrees_( rotation )
			RotationTransform.translateXBy_yBy_( -rotationX, -rotationY )
			return RotationTransform
		except Exception as e:
			self.logToConsole( "rotationTransform: %s" % e )

	def logToConsole( self, thisString ):
		print(thisString)
	
	def selectionForLayer(self, thisLayer):
		selection = ()
		try:
			selection = thisLayer.selection() # Glyphs until v2.1
		except:
			selection = thisLayer.selection # Glyphs v2.2+
		return selection
			
	def rotate(self, sender):
		# update settings to the latest user input:
		if not self.SavePreferences( self ):
			print("Note: 'Rotate Around Anchor' could not write preferences.")
		
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
		
		rotationDegrees = float( self.w.rotate_degrees.get() )
		
		if len(selectedLayers) == 1 and self.selectionForLayer(selectedLayers[0]):
			# rotate individually selected nodes and components
			try:
				thisLayer = selectedLayers[0]
				thisGlyph = thisLayer.parent
				selection = self.selectionForLayer(thisLayer)
				thisGlyph.beginUndo()
				
				centerOfThisLayer = self.rotationCenterOfLayer(thisLayer)
				RotationTransform = self.rotationTransform( centerOfThisLayer, rotationDegrees, rotationDirection )
				
				if rotationCount == 0: # simple rotation
					for thisThing in selection:
						if thisThing.__class__ == GSNode:
							thisThing = transformNode( thisThing, RotationTransform )
						elif thisThing.__class__ == GSComponent:
							thisThing = transformComponent( thisThing, RotationTransform )
				else: # step and repeat
					listOfPaths = []
					listOfComponents = []
					
					for thisThing in selection:
						if thisThing.__class__ == GSNode:
							# thisPath = thisThing.parent # DOES NOT WORK
							thisPath = [p for p in thisLayer.paths if thisThing in p.nodes][0]
							listOfPaths.append( thisPath )
						elif thisThing.__class__ == GSComponent:
							listOfComponents.append( thisThing )
					
					listOfPaths = list(set(listOfPaths)) # count every path only once
					self.stepAndRepeatListOfPaths( thisLayer, listOfPaths, RotationTransform, rotationCount )
					self.stepAndRepeatListOfComponents( thisLayer, listOfComponents, RotationTransform, rotationCount )
				
				thisGlyph.endUndo()
			except Exception as e:
				self.logToConsole( "Rotate: %s\ntrying to rotate individually selected nodes and components" % e )
			
		else:
			# rotate whole layers
			for thisLayer in selectedLayers:
				try:
					thisGlyph = thisLayer.parent
					thisGlyph.beginUndo()
					centerOfThisLayer = self.rotationCenterOfLayer(thisLayer)
					RotationTransform = self.rotationTransform( centerOfThisLayer, rotationDegrees, rotationDirection )
					thisLayer.setDisableUpdates()
					if rotationCount == 0: # simple rotation
						self.rotateListOfPaths( thisLayer, thisLayer.paths, RotationTransform, rotationCount )
						self.rotateListOfComponents( thisLayer, thisLayer.components, RotationTransform, rotationCount )
					else: # step and repeat
						self.stepAndRepeatListOfPaths( thisLayer, thisLayer.paths, RotationTransform, rotationCount )
						self.stepAndRepeatListOfComponents( thisLayer, thisLayer.components, RotationTransform, rotationCount )
					thisLayer.setEnableUpdates()
					thisLayer.updatePath()
				except Exception as e:
					self.logToConsole( "Rotate: %s\ntrying to rotate whole layers" % str(e) )
				finally:
					thisGlyph.endUndo()

Rotator()