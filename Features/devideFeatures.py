#!/usr/bin/python

# A quick and rough script to divide features into sub groups of 3000 lines
# It would be good to implement this into Glyphs so we can set feature name automatically if not present
import re

# Maximum number of lines in feature
maxSub = 3000; # 3000 for Glyphs

# Global lookup count
lookUpCount  = 0
featureCount = 0
featureOpen  = False
currFeature  = "NameOfFeature"

def cleanFeatureName(line):
	return ''.join([i for i in line if not i.isdigit()]).replace("lookup ","",1).replace(" {","",1).strip('\n')

def process(line):
    global lookUpCount
    global featureCount
    global featureOpen
    global currFeature
    if 'lookup ' in line.lower():
        currFeature = cleanFeatureName(line)
        lookUpCount = 0
        featureCount += 1
        fo.write("lookup " + currFeature + str(featureCount) + " {\n")
        featureOpen = True
    elif currFeature in line:
        # Close the curent feature
        fo.write("} " + currFeature + str(featureCount) + ";\n")
        featureOpen = False
    elif 'sub ' in line:
        if not featureOpen:
            lookUpCount = 0
            featureCount += 1
            fo.write("lookup " + currFeature + str(featureCount) + " {\n")
            featureOpen = True
        lookUpCount += 1
        if lookUpCount < maxSub:
            fo.write(line)
        else:
            # Close the curent feature
            fo.write("} " + currFeature + str(featureCount) + ";\n")
            # And create a new one
            lookUpCount = 0
            featureCount += 1
            fo.write("lookup " + currFeature + str(featureCount) + " {\n")
            fo.write(line)
    else:
        if featureOpen:
            fo.write("} " + currFeature + str(featureCount) + ";\n")
            featureOpen = False
        fo.write(line)

#Create a new ile to write
fo = open('./featuresOutput.txt', 'w');

with open("./pastedFeatures.txt", "r") as fi:
    for line in fi:
        process(line)
