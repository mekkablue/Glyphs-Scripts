#MenuTitle: Wrap and Extend Features
# -*- coding: utf-8 -*-
__doc__="""
Enclose all features with lookups and divide them into sub groups of 3000 lines max. It will also add the useExtension parameter allowing you to have a 32 bits limit insead of the 16 bits.
"""

import GlyphsApp
import string
import re

# Global variables
lookUpCount  = 0
featureCount = 0
featureOpen  = False
currFeature  = ""
originalCode = ""
newCode      = ""
# Maximum number of lines in feature
maxSub = 3000; # 3000 for Glyphs

Font = Glyphs.font

def resetGlobals():
    global lookUpCount
    global featureCount
    global featureOpen
    global currFeature
    global originalCode
    global newCode

    lookUpCount = 0;
    featureCount = 0;
    featureOpen = False;
    currFeature = "";
    originalCode = "";
    newCode = "";

def addCode(codeString):
    global newCode
    newCode += codeString

def cleanFeatureName(line):
    return ''.join([i for i in line if not i.isdigit()]).replace("lookup ","",1).replace("useExtension","",1).replace(" ","").replace("{","").strip('\n')

def openLookup():
    global lookUpCount
    global featureCount
    global featureOpen
    global currFeature
    lookUpCount = 0
    featureCount += 1
    addCode("lookup " + currFeature + str(featureCount) + " useExtension {\n")
    featureOpen = True

def process(line):
    global lookUpCount
    global featureCount
    global featureOpen
    global currFeature
    global maxSub
    if 'lookup ' in line:
        currFeature = cleanFeatureName(line)
        openLookup()
    elif currFeature in line:
        # Close the curent feature
        addCode("} " + currFeature + str(featureCount) + ";\n")
        featureOpen = False
    elif 'sub ' in line:
        if 'ignore ' in line:
            if featureOpen == True:
                # Close the curent feature
                addCode("} " + currFeature + str(featureCount) + ";\n")
                openLookup()
        if featureOpen == False:
            openLookup()
        lookUpCount += 1
        if lookUpCount > maxSub:
            # Close the curent feature
            addCode("} " + currFeature + str(featureCount) + ";\n")
            # And create a new one
            openLookup()
        addCode(line)
    else:
        if featureOpen == True:
            addCode("} " + currFeature + str(featureCount) + ";\n")
            featureOpen = False
        addCode(line)

for thisFeature in Font.features:
    resetGlobals()
    
    #set globals
    currFeature = thisFeature.name
    originalCode = thisFeature.code.splitlines(True)
    
    for line in originalCode:
        process(line)

    thisFeature.code = newCode
    
    print "Feature %s updated." % thisFeature.name

print "Done."
