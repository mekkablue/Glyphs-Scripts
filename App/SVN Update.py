#MenuTitle: SVN Update
# -*- coding: utf-8 -*-
__doc__="""
Issues an SVN Update command on specified folders and reports to the Macro Window.
"""

import vanilla, subprocess

class SVNUpdate( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
		windowHeight = 300
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 300 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"SVN Update", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SVNUpdate.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.descriptionText = vanilla.TextBox( (15-1, 12+2, -14, 14), "SVN Update these paths (1 path per line):", sizeStyle='small' )
		self.w.svnPaths = vanilla.TextEditor( (15, 12+20, -15, -40), 
			text="~/Library/Application Support/Glyphs/Scripts/",
		)
		self.w.svnPaths.getNSTextView().setFont_( NSFont.fontWithName_size_("Menlo",12.0) )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-95, -20-15, -15, -15), "Update", sizeStyle='regular', callback=self.SVNUpdateMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'SVN Update' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SVNUpdate.svnPaths"] = self.w.svnPaths.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.SVNUpdate.svnPaths": "~/Library/Application Support/Glyphs/Scripts/"
				}
			)
			self.w.svnPaths.set( Glyphs.defaults["com.mekkablue.SVNUpdate.svnPaths"] )
		except:
			return False
			
		return True

	def SVNUpdateMain( self, sender ):
		try:
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()
			
			paths = self.w.svnPaths.get().splitlines()
			for thisPath in paths:
				thisPath = thisPath.strip()
				if thisPath:
					import subprocess
					terminalCommandResult = subprocess.Popen( ["svn","up",thisPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
					output, error = terminalCommandResult.communicate()
					lineLength = len(thisPath)
					print "\n%s\n%s\n%s\nRESULT of svn update (0=OK): %s" % ( "-"*lineLength, thisPath, "-"*lineLength, terminalCommandResult.returncode )
					if output:
						print "\nOUTPUT:\n%s" % output
					if error:
						print "\nERROR:\n%s" % error
			
			if not self.SavePreferences( self ):
				print "Note: 'SVN Update' could not write preferences."
			
			self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "SVN Update Error: %s" % e

SVNUpdate()