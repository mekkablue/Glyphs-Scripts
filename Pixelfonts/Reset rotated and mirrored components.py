#MenuTitle: Reset rotated and mirrored components

Doc = Glyphs.currentDocument
selectedLayers = Doc.selectedLayers()

for l in selectedLayers:
	glyphName = l.parent.name
	
	toBeDeleted = []
	toBeAdded = []
	
	for compIndex in range(len(l.components)):
		comp = l.components[ compIndex ]
		if comp.transform[0] != 1.0 or comp.transform[3] != 1.0:
			# print comp.transform, comp.bounds.origin, comp.componentName #DEBUG
			toBeDeleted.append( compIndex )
			toBeAdded.append( [ comp.componentName, comp.bounds.origin.x, comp.bounds.origin.y ] )
				
	numOfComponents = len(toBeAdded)
	print "Fixing %i components in %s" % ( numOfComponents, glyphName )

	for delIndex in sorted(toBeDeleted)[::-1]:
		del l.components[ delIndex ]

	for addMe in toBeAdded:
		# print "   Adding %s at %i, %i" % ( addMe[0], addMe[1], addMe[2] ) #DEBUG
		
		newC = GSComponent( str( addMe[0] ) )
		newC.x = addMe[1]
		newC.y = addMe[2]
		
		l.components.append( newC )
			
