ABOUT

These are Python scripts for use with the Glyphs font editor <http://glyphsapp.com/>.


INSTALLATION

Put the scripts into your ~/Library/Application Support/Glyphs/Scripts/ folder.
For some scripts, you will also need to install Tal Leming's Vanilla. Here's how. Open Terminal and copy and paste each of the following four lines and hit return. Notes: the second line (svn...) may take a while, the fourth line (sudo...) will prompt you for your password.

cd ~/Library/
svn co http://svn.typesupply.com/packages/vanilla
cd vanilla/trunk/
sudo python setup.py install

And if you are running Glyphs on Lion (10.7) or later, you may want to add:

sudo cp /Library/Python/2.6/site-packages/vanilla* /Library/Python/2.7/site-packages/


ABOUT THE SCRIPTS

Anchors
Anchor Mover 1: GUI for moving anchors vertically in multiple glyphs. Handy for getting all top anchors right after changing your cap height. Needs Vanilla.
Anchor Mover 2: GUI for batch-processing anchors in multiple glyphs. Needs Vanilla.
Move top anchors: Moves top anchors in all selected glyphs to the new_y value specified in the .py file.
Put accents on new anchors in all layers: Moves 'acute', 'grave' and 'hookabovecomb' to the 'top_viet' anchor. Useful for Vietnamese double accents. Assumes that you have top_viet anchors in all layers of circumflex.
Report top anchors: Report the y positions of all top anchors into the Macro Panel.

Arabic
AXt Converter: converts the MacRoman glyph names (used in legacy AXt fonts) into nice names as employed by Glyphs. Attention: the script is still a work in progress. Suggestions are very welcome in the Wiki: https://github.com/mekkablue/Glyphs-Scripts/wiki/AXt-Converter

Components
Replace components: relinks components in selected glyphs to a new source glyph. Needs Vanilla.
Delete all components: Deletes ALL components in selected glyphs. Be careful.

Effects Scripts
Wackelpudding and Beowulferize: Select some or all glyphs in the Font tab, then run the script. It will create alternates of the selected glyphs and create a pseudorandom calt feature. Activate it by selecting Contextual Alternates in e.g. InDesign.
Baseline Wiggle: Creates a pos feature that randomly displaces the glyphs while you type.
Glyph Shaker: Randomly moves each node in selected layers of selected glyphs.
Retract offcurve nodes: Deletes all offcurve points (BCPs). Handy for making sure, your font only consists of straight lines. 
Turn offcurve into oncurve: Does exactly what the name suggests. Makes fonts look really weird.

Glyph Names:
Check glyph names: Checks all available glyph names for illegal characters.
Lowercase: Turns the names of selected glyphs lowercase.

Hinting
Delete Hints: Deletes hints in selected glyphs.

Masters
Copy layer to layer: Copies paths from one Master to another. Needs Vanilla.
Dekink masters: Dekinks your smooth transitions which are not horizontal or vertical. Select one or more angled smooth connections and run this script to move the corresponding nodes in all other masters to the same relative position.
Fill up empty layers: Copies paths from one Master to another. But only if target master is empty. Needs Vanilla.
Find and Replace in Layer Names: Replaces text in all layer names (except Master layers) of selected glyphs. Useful if you use the bracket trick in many glyphs. Needs Vanilla.
Insert instances: GUI for calculating and inserting weight instances. Needs Vanilla.
Show next/previous instance: Jumps to next/previous instance in the preview section of the current Edit tab. Handy for attaching a keyboard shortcut to.
Suggest instances: Calculates an ideal distribution of weight values between your masters. Outputs into the macro window.

Metrics
Center glyphs: centers all selected glyphs inside their width, so that LSB=RSB.
Copy sidebearings: steals the sidebearing values from a 2nd font. Needs Vanilla.
Export Kerning CSV: exports a CSV containing all kerning pairs ("mastername;left;right;kerningvalue").
Export Metrics CSV: exports a CSV containing all LSB, RSB and width values ("glyphname;mastername;LSB;RSB;width").
Extract kern strings 1st char: asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 1st letter. Needs Vanilla.
Extract kern strings 2nd char: asks you for a group of characters, then prompts you for one or more text files; it will then output all kerning pairs (containing these chars, found in the text files) to a new Edit tab, alphabetically sorted. Finds all pairs where the entered chars are the 2nd letter. Needs Vanilla.

OpenType
Floating Features: Floating palettes for activating and deactivating OT features. Same functionality as the pop-up menu. Needs Vanilla.
Make OT Class from selected glyphs: GUI for creating a new OT class with the selected glyphs. Needs Vanilla.

Paths
All "Align" scripts look for a path in the currently active layer and align it to whatever the script title says. Useful if you need to do one of these alignment operations very often. Hint: you can set a keyboard shortcut in System Preferences.
All "Bump" scripts move the selection towards the next available metric to the left, right, top or bottom. The Bump Left/Right scripts also include the halfwidth of the glyph. These are intended for setting a shortcut in System Preferences > Keyboard > Keyboard Shortcuts > Application Shortcuts (I recommend ctrl-opt-cmd-arrows).
All "Distribute" scripts distribute all selected nodes horizontally or vertically, whatever is closer or what the script title says.
All "Move" scripts move the selected glyph(s) up/down by the specified distance, similar to what (shift-)ctrl-cmd-left/rightarrow does. As shortcut, I recommend (shift-)ctrl-cmd-up/downarrow.
Close all paths: Closes all open paths in the visible layers of all selected glyphs.
Rotate around anchor: GUI for rotating glyphs or selections of nodes and components around a 'rotate' anchor. Allows to step and repeat. Requires Vanilla.

Pixelfonts
Align anchors to pixelgrid: Moves diacritic anchors onto the grid. Assumes a grid step of 50.
Delete components out of bounds: If a component is placed far outside the usual coordinates (happens when you cmd-arrow components with a high grid step), this script will delete them.
Delete duplicate components: Looks for duplicate components (same name and position) and keeps only one.
Flashify Pixels: Creates small bridges in order to prevent self-intersection of paths so counters stay white. This is especially a problem for the Flash font renderer, hence the name of the script.
Re-Compose Pixels: Tries to rebuild accidentally decomposed pixelglyphs with 'pixel' components.
Reset rotated and mirrored components: Looks for scaled, mirrored and rotated components and turns them back into their default scale and orientation, but keeps their position. Useful for fixing mirrored pixels.

Smallcaps
Copy kerning classes from smcp to c2sc: If you already have c2sc and smcp glyphs, it will copy kerning group attributes from smcp to c2sc glyphs, e.g. d.smcp has leftgroup=h.smcp and rightgroup=o.smcp, then leftgroup=h.smcp and rightgroup=o.smcp will be copied to D.c2sc. 
Make c2sc from smcp: Creates .c2sc copies of your .smcp glyphs, with the .smcp glyphs inserted as components in the .c2sc copies. For example, if you have a.smcp, the script will create A.c2sc and insert a.smcp as component. It will not do anything in case A.c2sc already exists.
Make smcp from c2sc: Creates .smcp copies of your .c2sc glyphs, with the .c2sc glyphs inserted as components in the .smcp copies. For example, if you have A.c2sc, the script will create a.smcp and insert A.c2sc as component. It will not do anything in case a.smcp already exists.

Stylistic Sets 
Synchronize ssXX glyphs: Creates missing ssXX glyphs so that you have synchronous groups of ssXX glyphs. E.g. you have a.ss01 b.ss01 c.ss01 a.ss02 c.ss02 --> the script creates b.ss02
Create ssXX from layer: Takes the current layer and copies it to the primary layer of a new .ssXX glyph.
Create pseudorandom calt feature: Creates pseudorandom calt (contextual alternatives) feature based on number of existing ssXX glyphs in the font. Update: now includes the default class in the rotation algorithm.
