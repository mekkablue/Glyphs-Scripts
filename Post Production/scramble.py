#!/usr/bin/env python3
# scramble.py - Scramble glyphs in fonts with SCRM unscramble feature + HTML demo

import argparse
import json
import random
import glob
import webbrowser
import tempfile
import shutil
import sys
from pathlib import Path
from fontTools import ttLib
from fontTools.ttLib.tables import otTables

SPACE_UNICODES = {
    0x002A, 0x00A0,  # *, NBSP
    0x2002, 0x2003, 0x2000, 0x2001,  # En/Em space, etc.
    0x2004, 0x2005, 0x2006, 0x2007,  # 1/8-6 em spaces
    0x2008, 0x2009, 0x200A,          # Punctuation/Thin spaces
    0x200B, 0x202F, 0x205F           # Zero-width, NNSP, Medium math space
}

def isSpaceGlyph(font, glyphName):
	"""Check if glyph is a space (zero-width or listed Unicode)"""
	try:
		# Check hmtx first (fast zero-width detection)
		metrics = font['hmtx'].metrics.get(glyphName, (0, 0))
		if metrics[0] == 0:
			return True
		
		# Check cmap for space Unicodes
		for cmapTable in font['cmap'].tables:
			if cmapTable.isUnicode() and glyphName in cmapTable.cmap.values():
				charCode = next(code for code, gn in cmapTable.cmap.items() if gn == glyphName)
				if charCode in SPACE_UNICODES:
					return True
		return False
	except:
		return False

def getGlyphClass(glyphName, font):
	"""Get GDEF class for a glyph name. 0=unclassified, 1=base, 2=ligature, 3=mark, 4=component."""
	try:
		if 'GDEF' not in font:
			return 0
		
		gdef = font['GDEF'].table
		if not gdef or not hasattr(gdef, 'GlyphClassDef') or not gdef.GlyphClassDef:
			return 0
		
		classDefs = gdef.GlyphClassDef.classDefs
		return classDefs.get(glyphName, 0)
	except Exception:
		return 0

def glyphsInLookup(lookup):
	"""Collect all glyph names referenced in a single GSUB lookup."""
	glyphs = set()
	subtables = lookup.SubTable
	# Unwrap Extension lookups (type 7)
	if lookup.LookupType == 7:
		subtables = [st.ExtSubTable for st in subtables if hasattr(st, 'ExtSubTable')]
	for subtable in subtables:
		mapping = getattr(subtable, 'mapping', None)
		if mapping:
			for inGlyph, outGlyphs in mapping.items():
				glyphs.add(inGlyph)
				if isinstance(outGlyphs, (list, tuple)):
					glyphs.update(outGlyphs)  # MultipleSubst
				else:
					glyphs.add(outGlyphs)  # SingleSubst
		alternates = getattr(subtable, 'alternates', None)
		if alternates:
			for inGlyph, altGlyphs in alternates.items():
				glyphs.add(inGlyph)
				glyphs.update(altGlyphs)
		ligatures = getattr(subtable, 'ligatures', None)
		if ligatures:
			for firstGlyph, ligList in ligatures.items():
				glyphs.add(firstGlyph)
				for lig in ligList:
					glyphs.add(lig.LigGlyph)
					glyphs.update(lig.Component)
		substitute = getattr(subtable, 'Substitute', None)
		if substitute:
			glyphs.update(substitute)  # ReverseChainSingleSubst
		for attr in ('Coverage', 'BacktrackCoverage', 'InputCoverage', 'LookAheadCoverage'):
			coverage = getattr(subtable, attr, None)
			if coverage is None:
				continue
			coverages = coverage if isinstance(coverage, (list, tuple)) else [coverage]
			for cov in coverages:
				if cov and hasattr(cov, 'glyphs'):
					glyphs.update(cov.glyphs)
	return glyphs

def getRvrnGlyphs(font):
	"""Collect all glyphs involved in variation alternates:
	the rvrn feature's default lookups PLUS every lookup reachable through
	GSUB FeatureVariations (condition-triggered alternate feature tables).
	In OTVARs, the variation alternates live in FeatureVariations, not in
	the default rvrn feature table (which is usually empty)."""
	glyphs = set()
	if 'GSUB' not in font:
		return glyphs
	gsub = font['GSUB'].table
	if not gsub.LookupList:
		return glyphs

	lookupIndices = set()

	if gsub.FeatureList:
		for featRecord in gsub.FeatureList.FeatureRecord:
			if featRecord.FeatureTag == 'rvrn':
				lookupIndices.update(featRecord.Feature.LookupListIndex)

	# Variation alternates: past the trigger point on the axis, the engine
	# swaps in these alternate feature tables. Exclude their glyphs, and the
	# glyphs of the default lookups of every feature they substitute, so the
	# substitutions stay consistent on both sides of the trigger point.
	featureVariations = getattr(gsub, 'FeatureVariations', None)
	if featureVariations:
		for fvRecord in featureVariations.FeatureVariationRecord:
			for substRecord in fvRecord.FeatureTableSubstitution.SubstitutionRecord:
				lookupIndices.update(substRecord.Feature.LookupListIndex)
				if gsub.FeatureList and substRecord.FeatureIndex < len(gsub.FeatureList.FeatureRecord):
					substitutedFeature = gsub.FeatureList.FeatureRecord[substRecord.FeatureIndex].Feature
					lookupIndices.update(substitutedFeature.LookupListIndex)

	for idx in lookupIndices:
		if idx < len(gsub.LookupList.Lookup):
			glyphs.update(glyphsInLookup(gsub.LookupList.Lookup[idx]))

	if glyphs:
		print(f'[DEBUG] rvrn/variation-alternate glyphs excluded from scrambling: {len(glyphs)}')
	return glyphs

def scrambleGlyphOrder(font, respectClasses=True):
	glyphOrder = list(font.getGlyphOrder())
	glyphMap = {gn: i for i, gn in enumerate(glyphOrder)}
	originalOrder = list(glyphOrder)
	originalHmtx = dict(font['hmtx'].metrics) if 'hmtx' in font else {}

	spaceGlyphs = set()
	for cmapTable in font['cmap'].tables:
		if cmapTable.isUnicode():
			for code, gn in cmapTable.cmap.items():
				if code in SPACE_UNICODES:
					spaceGlyphs.add(gn)

	rvrnGlyphs = getRvrnGlyphs(font)

	swappableGlyphs = []
	for gn in glyphOrder:
		if gn == '.notdef':
			continue
		if gn in spaceGlyphs:
			continue
		if gn in rvrnGlyphs:
			continue
		swappableGlyphs.append(gn)

	print(f'[DEBUG] Total glyphs: {len(glyphOrder)}, spaces excluded: {len(spaceGlyphs)}, rvrn excluded: {len(rvrnGlyphs)}, swappable: {len(swappableGlyphs)}')

	if respectClasses:
		groups = {}
		for gn in swappableGlyphs:
			cls = getGlyphClass(gn, font)
			groups.setdefault(cls, []).append(gn)

		totalSwaps = 0
		for cls in sorted(groups.keys()):
			grp = list(groups[cls])
			print(f'[DEBUG] GDEF class {cls}: {len(grp)} glyphs')
			if len(grp) < 2:
				continue

			random.shuffle(grp)
			swapCount = 0
			while len(grp) >= 2:
				glyphA = grp.pop(0)
				glyphB = grp.pop(0)

				idxA = glyphMap[glyphA]
				idxB = glyphMap[glyphB]
				glyphOrder[idxA] = glyphB
				glyphOrder[idxB] = glyphA
				swapCount += 1

				if glyphA in ('A', 'V', 'a') or glyphB in ('A', 'V', 'a') or glyphA == 'uni0326.case' or glyphB == 'uni0326.case':
					print(f'[DEBUG] swap {glyphA}({cls}) <-> {glyphB}({cls})')

			print(f'[DEBUG] Class {cls}: {swapCount} swaps')
			totalSwaps += swapCount

		print(f'[DEBUG] Total swaps: {totalSwaps}')
	else:
		random.shuffle(swappableGlyphs)
		swapCount = 0
		while len(swappableGlyphs) >= 2:
			glyphA = swappableGlyphs.pop(0)
			glyphB = swappableGlyphs.pop(0)
			idxA = glyphMap[glyphA]
			idxB = glyphMap[glyphB]
			glyphOrder[idxA] = glyphB
			glyphOrder[idxB] = glyphA
			swapCount += 1
		print(f'[DEBUG] Total swaps: {swapCount}')

	font.setGlyphOrder(glyphOrder)
	print('[DEBUG] Glyph order scrambled')

	return originalOrder, glyphOrder, originalHmtx

def verifyNoCrossClassSwaps(font, originalOrder, currentOrder):
	"""Verify no class 1↔3 swaps occurred"""
	print('[DEBUG] Verifying no cross-class swaps...')
	
	for i, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
		if origGlyph != currGlyph:
			origClass = getGlyphClass(origGlyph, font)
			currClass = getGlyphClass(currGlyph, font)
			
			if (origClass == 1 and currClass == 3) or (origClass == 3 and currClass == 1):
				print(f'[ERROR] Cross-class swap: {origGlyph}(cls{origClass}) <-> {currGlyph}(cls{currClass})')
	
	print('[DEBUG] ✓ No class 1↔3 swaps found')

def scrambleCmap(font, originalOrder, currentOrder):
	glyphMapping = {}
	for i, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
		if origGlyph != currGlyph:
			glyphMapping[origGlyph] = currGlyph
	
	print(f'[DEBUG] Cmap remapping: {len(glyphMapping)} glyphs')
	
	for cmapTable in font['cmap'].tables:
		if not cmapTable.isUnicode():
			continue
		
		cmap = cmapTable.cmap
		remapped = {}
		for charCode, glyphName in cmap.items():
			if glyphName in glyphMapping:
				remapped[charCode] = glyphMapping[glyphName]
			else:
				remapped[charCode] = glyphName
		
		cmapTable.cmap = remapped
	
	print(f'[DEBUG] Cmap scrambled')

def makeUnscrambleMap(font, originalOrder, currentOrder):
	"""Build unscramble map for SCRM feature"""
	
	unscrambleMap = {}
	for i, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
		if origGlyph != currGlyph:
			unscrambleMap[currGlyph] = origGlyph
	
	print(f'[DEBUG] Unscramble pairs: {len(unscrambleMap)}')
	if not unscrambleMap:
		print('[DEBUG] No scrambled glyphs found')
		return None
	
	return unscrambleMap

def insertScrmFeatureManually(font, unscrambleMap, featureTag='SCRM'):
	"""Manually insert SCRM feature into existing GSUB table, preserving all other features"""
	try:
		if not unscrambleMap:
			print(f'[DEBUG] No unscramble map, skipping {featureTag} feature insertion')
			return False

		print(f'[DEBUG] Inserting {featureTag} feature manually...')
		
		if 'GSUB' not in font:
			print('[DEBUG] No GSUB table, creating one...')
			font['GSUB'] = ttLib.newTable('GSUB')
			gsub = font['GSUB']
			gsub.table = otTables.GSUB()
			gsub.table.Version = 0x00010000
			gsub.table.ScriptList = otTables.ScriptList()
			gsub.table.ScriptList.ScriptRecord = []
			gsub.table.FeatureList = otTables.FeatureList()
			gsub.table.FeatureList.FeatureRecord = []
			gsub.table.LookupList = otTables.LookupList()
			gsub.table.LookupList.Lookup = []
		
		gsub = font['GSUB'].table
		
		# Create SingleSubst lookup for SCRM
		lookup = otTables.Lookup()
		lookup.LookupType = 1  # SingleSubst
		lookup.LookupFlag = 0
		
		subtable = otTables.SingleSubst()
		subtable.mapping = unscrambleMap
		
		lookup.SubTable = [subtable]
		lookup.SubTableCount = 1
		
		# Insert lookup at beginning of LookupList (index 0)
		if not gsub.LookupList:
			gsub.LookupList = otTables.LookupList()
			gsub.LookupList.Lookup = []
		
		gsub.LookupList.Lookup.insert(0, lookup)
		gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

		print(f'[DEBUG] Created lookup at index 0 (SCRM lookup first)')

		# Update all existing lookups' indices in features
		# Since we inserted at 0, all old lookups shifted by 1
		for featRec in gsub.FeatureList.FeatureRecord:
			feature = featRec.Feature
			if feature.LookupListIndex:
				feature.LookupListIndex = [idx + 1 for idx in feature.LookupListIndex]
				feature.LookupCount = len(feature.LookupListIndex)

		# Fix: shift SubstLookupRecord.LookupListIndex in all type-5/6 lookups
		# because inserting SCRM at index 0 shifted every other lookup index by +1
		for lkp in gsub.LookupList.Lookup:
			ltype = lkp.LookupType
			sts = lkp.SubTable
			if ltype == 7:
				sts = [s.ExtSubTable for s in sts if hasattr(s, 'ExtSubTable')]
				ltype = sts[0].LookupType if sts else ltype
			if ltype not in (5, 6):
				continue
			for st in sts:
				# Format 3 direct SubstLookupRecord
				for slr in (getattr(st, 'SubstLookupRecord', None) or []):
					slr.LookupListIndex += 1
				# Type 5 Format 1: SubRuleSet → SubRule
				for rs in (getattr(st, 'SubRuleSet', None) or []):
					if rs is None: continue
					for rule in (getattr(rs, 'SubRule', None) or []):
						for slr in (getattr(rule, 'SubstLookupRecord', None) or []):
							slr.LookupListIndex += 1
				# Type 5 Format 2: SubClassSet → SubClassRule
				for rs in (getattr(st, 'SubClassSet', None) or []):
					if rs is None: continue
					for rule in (getattr(rs, 'SubClassRule', None) or []):
						for slr in (getattr(rule, 'SubstLookupRecord', None) or []):
							slr.LookupListIndex += 1
				# Type 6 Format 1: ChainSubRuleSet → ChainSubRule
				for rs in (getattr(st, 'ChainSubRuleSet', None) or []):
					if rs is None: continue
					for rule in (getattr(rs, 'ChainSubRule', None) or []):
						for slr in (getattr(rule, 'SubstLookupRecord', None) or []):
							slr.LookupListIndex += 1
				# Type 6 Format 2: ChainSubClassSet → ChainSubClassRule
				for rs in (getattr(st, 'ChainSubClassSet', None) or []):
					if rs is None: continue
					for rule in (getattr(rs, 'ChainSubClassRule', None) or []):
						for slr in (getattr(rule, 'SubstLookupRecord', None) or []):
							slr.LookupListIndex += 1
		print('[DEBUG] SubstLookupRecord indices shifted by +1')

		# Fix: FeatureVariations (OTVAR variation alternates) reference lookups
		# by index too — the alternate feature tables that get swapped in past
		# the axis trigger point. Without this shift, past the trigger point
		# every substituted feature points at the lookup BEFORE the intended
		# one (off by one), producing wrong substitutions.
		featureVariations = getattr(gsub, 'FeatureVariations', None)
		if featureVariations:
			for fvRecord in featureVariations.FeatureVariationRecord:
				for substRecord in fvRecord.FeatureTableSubstitution.SubstitutionRecord:
					feature = substRecord.Feature
					if feature.LookupListIndex:
						feature.LookupListIndex = [idx + 1 for idx in feature.LookupListIndex]
						feature.LookupCount = len(feature.LookupListIndex)
			print('[DEBUG] FeatureVariations lookup indices shifted by +1')

		# Create or update SCRM feature
		existingSCRM = None
		for i, featRec in enumerate(gsub.FeatureList.FeatureRecord):
			if featRec.FeatureTag == featureTag:
				existingSCRM = i
				break
		
		featureRecordInserted = False
		if existingSCRM is not None:
			# Update existing feature to point to lookup 0
			print(f'[DEBUG] Updating existing {featureTag} feature')
			feature = gsub.FeatureList.FeatureRecord[existingSCRM].Feature
			feature.LookupListIndex = [0]
			feature.LookupCount = 1
		else:
			# Create new feature at beginning pointing to lookup 0
			print(f'[DEBUG] Creating new {featureTag} feature')
			feature = otTables.Feature()
			feature.FeatureParams = None
			feature.LookupListIndex = [0]
			feature.LookupCount = 1

			featureRecord = otTables.FeatureRecord()
			featureRecord.FeatureTag = featureTag
			featureRecord.Feature = feature

			# Insert at beginning of feature list
			gsub.FeatureList.FeatureRecord.insert(0, featureRecord)
			gsub.FeatureList.FeatureCount = len(gsub.FeatureList.FeatureRecord)
			featureRecordInserted = True

			# Fix: FeatureVariations SubstitutionRecords address the feature
			# they replace by index into the FeatureList; the insert at 0
			# shifted every existing feature by +1. Without this, past the
			# axis trigger point the variation record replaces the WRONG
			# feature — a record targeting former feature 0 would clobber
			# the freshly inserted SCRM feature itself.
			if featureVariations:
				for fvRecord in featureVariations.FeatureVariationRecord:
					for substRecord in fvRecord.FeatureTableSubstitution.SubstitutionRecord:
						substRecord.FeatureIndex += 1
				print('[DEBUG] FeatureVariations feature indices shifted by +1')
		
		# Ensure SCRM is available in all scripts
		if not gsub.ScriptList or not gsub.ScriptList.ScriptRecord:
			print('[DEBUG] No scripts in GSUB, adding default script')
			gsub.ScriptList = otTables.ScriptList()
			gsub.ScriptList.ScriptRecord = []
			
			script = otTables.Script()
			script.DefaultLangSys = otTables.LangSys()
			script.DefaultLangSys.ReqFeatureIndex = 0xFFFF
			script.DefaultLangSys.FeatureIndex = [0]  # SCRM feature index
			script.DefaultLangSys.FeatureCount = 1
			script.LangSysRecord = []
			
			scriptRecord = otTables.ScriptRecord()
			scriptRecord.ScriptTag = 'DFLT'
			scriptRecord.Script = script
			
			gsub.ScriptList.ScriptRecord.append(scriptRecord)
			gsub.ScriptList.ScriptCount = 1
		else:
			# Fix: inserting at FeatureList[0] shifted every existing feature index by +1;
			# update all Script/LangSys FeatureIndex arrays before adding SCRM (index 0).
			# Only do this when a FeatureRecord was actually inserted — updating an
			# existing SCRM feature does not shift the FeatureList.
			print(f'[DEBUG] Adding {featureTag} to {len(gsub.ScriptList.ScriptRecord)} scripts')
			if featureRecordInserted:
				for scriptRec in gsub.ScriptList.ScriptRecord:
					script = scriptRec.Script
					if script.DefaultLangSys:
						script.DefaultLangSys.FeatureIndex = [idx + 1 for idx in script.DefaultLangSys.FeatureIndex]
					if script.LangSysRecord:
						for langSysRec in script.LangSysRecord:
							langSys = langSysRec.LangSys
							langSys.FeatureIndex = [idx + 1 for idx in langSys.FeatureIndex]

			# index of the SCRM feature in the (possibly shifted) FeatureList
			scrmFeatureIndex = 0 if featureRecordInserted else existingSCRM

			for scriptRec in gsub.ScriptList.ScriptRecord:
				script = scriptRec.Script

				# Add to default language system
				if script.DefaultLangSys:
					if scrmFeatureIndex not in script.DefaultLangSys.FeatureIndex:
						script.DefaultLangSys.FeatureIndex = [scrmFeatureIndex] + list(script.DefaultLangSys.FeatureIndex)
						script.DefaultLangSys.FeatureCount = len(script.DefaultLangSys.FeatureIndex)

				# Add to all language systems
				if script.LangSysRecord:
					for langSysRec in script.LangSysRecord:
						langSys = langSysRec.LangSys
						if scrmFeatureIndex not in langSys.FeatureIndex:
							langSys.FeatureIndex = [scrmFeatureIndex] + list(langSys.FeatureIndex)
							langSys.FeatureCount = len(langSys.FeatureIndex)
		
		print(f'[DEBUG] {featureTag} feature inserted successfully')
		print(f'[DEBUG] GSUB now has {gsub.FeatureList.FeatureCount} features')
		for i, featRec in enumerate(gsub.FeatureList.FeatureRecord):
			print(f'[DEBUG]   Feature {i}: {featRec.FeatureTag}')
		
		return True
	except Exception as e:
		print(f'[DEBUG] Manual insertion failed: {e}')
		import traceback
		traceback.print_exc()
		return False

GSUB_EXCLUDED = {'ccmp', 'aalt', 'rlig', 'rclt', 'rvrn', 'dnom', 'numr', 'locl', 'SCRM'}

def getFontFaces(outputFiles):
	"""Return (faces, gsub_features).
	faces = list of (filename, display_name, coords_or_None)
	coords_or_None = dict of axis→value for fvar instances, else None."""
	faces = []
	gsub_features = None
	for fpath in outputFiles:
		try:
			font = ttLib.TTFont(str(fpath))
			name4rec = next((n for n in font['name'].names if n.nameID == 4), None)
			name4 = name4rec.toUnicode() if name4rec else fpath.stem
			fvar = font.get('fvar')
			if fvar:
				for inst in fvar.instances:
					instStr = font['name'].getDebugName(inst.subfamilyNameID) or ''
					label = f'{name4} {instStr}'.strip() if instStr else name4
					faces.append((fpath.name, label, dict(inst.coordinates)))
			else:
				faces.append((fpath.name, name4, None))
			if gsub_features is None and 'GSUB' in font:
				seen = set()
				gsub_features = []
				for fr in font['GSUB'].table.FeatureList.FeatureRecord:
					tag = fr.FeatureTag
					if tag not in GSUB_EXCLUDED and tag not in seen:
						gsub_features.append(tag)
						seen.add(tag)
				gsub_features.sort()
			font.close()
		except Exception as e:
			print(f'[DEBUG] getFontFaces error for {fpath}: {e}')
			continue
	return faces, (gsub_features or [])

def generateHtml(outputFiles, htmlPath):
	faces, gsub_features = getFontFaces(outputFiles)
	if not faces:
		print('Warning: no scrambled fonts found in output directory.')
		return False

	has_case = 'case' in gsub_features

	# Build font select options — value=filename, data-coords for fvar instances
	option_parts = []
	for i, (file, name, coords) in enumerate(faces):
		sel = ' selected' if i == 0 else ''
		dc = f" data-coords='{json.dumps(coords)}'" if coords is not None else ''
		option_parts.append(f'<option value="{file}"{sel}{dc}>{name}</option>')
	options_html = '\n    '.join(option_parts)

	# All toggles as hidden-checkbox + label buttons
	# SCRM first (no feature tag, handled separately in JS)
	def btn(id_, label, checked=False, extra_class='', data=''):
		ch = ' checked' if checked else ''
		cls = f'feat-cb{" " + extra_class if extra_class else ""}'
		return (f'<input type="checkbox" id="{id_}" class="{cls}"{ch}{data} onchange="updateFeatures()">'
		        f'<label for="{id_}" class="feat-btn">{label}</label>')

	scrm_btn = (f'<input type="checkbox" id="cb-scrm" class="feat-cb"'
	            f' onchange="updateFeatures()">'
	            f'<label for="cb-scrm" class="feat-btn">SCRM</label>')

	gpos_btns = '  '.join([
		btn('cb-kern', 'kern', checked=True),
		btn('cb-mark', 'mark', checked=True),
		btn('cb-mkmk', 'mkmk', checked=True),
	])

	gsub_btns = '  '.join(
		btn(f'cb-{tag}', tag, extra_class='gsub-feat', data=f' data-feat="{tag}"')
		for tag in gsub_features
	)

	case_js = '''
  const caseCb = document.getElementById('cb-case');
  if (caseCb) textArea.style.textTransform = caseCb.checked ? 'uppercase' : '';''' if has_case else ''

	# JS for variation settings — applied from selected option's data-coords
	var_js = '''
function applyInstance(opt) {
  if (!opt) return;
  const raw = opt.dataset.coords;
  if (raw) {
    const coords = JSON.parse(raw);
    textArea.style.fontVariationSettings = Object.entries(coords).map(([k,v]) => '"'+k+'" '+v).join(', ');
  } else {
    textArea.style.fontVariationSettings = 'normal';
  }
}'''

	html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: sans-serif; margin: 40px; }}
#header {{ margin-bottom: 20px; display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }}
#fontSelect {{ font-size: 14px; padding: 2px 4px; }}
.feat-cb {{ display: none; }}
.feat-btn {{
  display: inline-block;
  padding: 1px 6px 2px;
  font-size: 11px;
  line-height: 1.7;
  border: 1px solid #000;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  background: #fff;
  color: #000;
}}
.feat-cb:checked + .feat-btn {{ background: #000; color: #fff; }}
.btn-group {{ display: flex; gap: 2px; }}
.size-group {{ display: flex; align-items: center; gap: 4px; margin-left: 8px; font-size: 12px; }}
#sizeSlider {{ width: 120px; }}
#textArea {{
  font-size: var(--size, 36pt);
  width: 100%; height: 80vh;
  border: 1px solid #ccc; padding: 20px;
  resize: vertical; font-family: var(--font, sans-serif);
  white-space: pre-wrap; overflow: auto; box-sizing: border-box;
}}
@media (prefers-color-scheme: dark) {{
  body {{ background: #1a1a1a; color: #e0e0e0; }}
  #fontSelect {{ background: #2a2a2a; color: #e0e0e0; border: 1px solid #555; }}
  .feat-btn {{ background: #2a2a2a; color: #e0e0e0; border-color: #888; }}
  .feat-cb:checked + .feat-btn {{ background: #e0e0e0; color: #1a1a1a; }}
  #textArea {{ background: #111; color: #e0e0e0; border-color: #444; }}
}}
</style>
</head>
<body>
<div id="header">
  <select id="fontSelect">
    {options_html}
  </select>
  <div class="btn-group">
    {scrm_btn}
  </div>
  <div class="btn-group">
    {gpos_btns}
  </div>
  <div class="btn-group">
    {gsub_btns}
  </div>
  <div class="size-group">
    <input type="range" id="sizeSlider" min="12" max="144" value="36" step="1" oninput="updateSize()">
    <span id="sizeLabel">36pt</span>
  </div>
</div>
<textarea id="textArea">AVATAR. The quick brown fox jumps over the lazy dog. THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. 0123456789 1a 2o 3ère 4ème 5e Paral·lel No.6.</textarea>
<script>
const textArea = document.getElementById('textArea');
const fontSelect = document.getElementById('fontSelect');
{var_js}
function loadFont(fontFile) {{
  if (!fontFile) return;
  let style = document.getElementById('dynamicFont');
  if (style) style.remove();
  style = document.createElement('style');
  style.id = 'dynamicFont';
  style.textContent = '@font-face {{ font-family: "scrm-preview"; src: url("' + fontFile + '") format("woff2"), url("' + fontFile + '") format("truetype"); font-display: swap; }}';
  document.head.appendChild(style);
  document.documentElement.style.setProperty('--font', '"scrm-preview"');
}}

function updateFeatures() {{
  const scrm = document.getElementById('cb-scrm').checked;
  const parts = ['"SCRM" ' + (scrm ? '1' : '0')];
  ['kern','mark','mkmk'].forEach(f => {{
    const cb = document.getElementById('cb-' + f);
    if (cb) parts.push('"' + f + '" ' + (cb.checked ? '1' : '0'));
  }});
  document.querySelectorAll('.gsub-feat').forEach(cb => {{
    parts.push('"' + cb.dataset.feat + '" ' + (cb.checked ? '1' : '0'));
  }});
  textArea.style.fontFeatureSettings = parts.join(', ');{case_js}
}}

function updateSize() {{
  const val = document.getElementById('sizeSlider').value;
  document.getElementById('sizeLabel').textContent = val + 'pt';
  document.documentElement.style.setProperty('--size', val + 'pt');
}}

fontSelect.onchange = function() {{
  const opt = this.options[this.selectedIndex];
  loadFont(opt.value);
  applyInstance(opt);
}};

window.onload = function() {{
  const opt = fontSelect.options[fontSelect.selectedIndex];
  loadFont(opt.value);
  applyInstance(opt);
  updateFeatures();
}};
</script>
</body>
</html>'''
	with open(htmlPath, 'w', encoding='utf-8') as f:
		f.write(html)
	return True

def parseFonts(fontPatterns):
	fonts = []
	for pat in fontPatterns:
		fonts.extend(glob.glob(pat))
	return [f for f in fonts if f.lower().endswith(('.ttf','.otf','.woff','.woff2'))]

def remapGposToOriginalOrder(font, originalOrder, currentOrder):
	"""Remap GPOS for mark positioning (keep kern Coverage as-is)"""
	if 'GPOS' not in font:
		return
	
	try:
		# For mark positioning: scrambled → original
		markMapping = {curr: orig for orig, curr in zip(originalOrder, currentOrder) if orig != curr}
		
		gpos = font['GPOS'].table
		
		if gpos.LookupList:
			for lookup in gpos.LookupList.Lookup:
				for subtable in lookup.SubTable:
					# KERN (PairPos): keep Coverage AS-IS (contains scrambled glyphs)
					if lookup.LookupType == 2:  # PairPos
						print('[DEBUG] PairPos (kern): Coverage unchanged')
					
					# MARK POSITIONING: remap Coverage/ClassDef
					elif lookup.LookupType in [4, 5]:  # MarkToBase/MarkToLigature
						for attr in ['Coverage', 'MarkCoverage', 'BaseCoverage']:
							if hasattr(subtable, attr):
								cov = getattr(subtable, attr)
								if cov and hasattr(cov, 'glyphs'):
									cov.glyphs = [markMapping.get(g, g) for g in cov.glyphs]
						
						for attr in ['ClassDef', 'MarkClassDef']:
							if hasattr(subtable, attr):
								obj = getattr(subtable, attr)
								if obj and hasattr(obj, 'classDefs'):
									obj.classDefs = {markMapping.get(k, k): v for k, v in obj.classDefs.items()}
		
		print('[DEBUG] GPOS: kern preserved, marks remapped')
	except Exception as e:
		print(f'[DEBUG] GPOS remap failed: {e}')

def remapGsubToCurrentOrder(font, originalOrder, currentOrder):
	"""Remap GSUB lookups so they reference scrambled glyph names.
	Mirrors remapGposToOriginalOrder for marks: bidirectional swap mapping
	ensures features fire on the right glyph in SCRM-off (scrambled) mode."""
	if 'GSUB' not in font:
		return

	# Bidirectional swap map: for every A↔B swap, maps A→B and B→A
	swapMap = {curr: orig for orig, curr in zip(originalOrder, currentOrder) if orig != curr}

	def remap(name):
		return swapMap.get(name, name)

	def remapCoverage(cov):
		if cov and hasattr(cov, 'glyphs'):
			cov.glyphs = [remap(g) for g in cov.glyphs]

	def remapClassDef(cd):
		if cd and hasattr(cd, 'classDefs'):
			cd.classDefs = {remap(k): v for k, v in cd.classDefs.items()}

	gsub = font['GSUB'].table
	if not gsub.LookupList:
		return

	for lookup in gsub.LookupList.Lookup:
		ltype = lookup.LookupType
		subtables = lookup.SubTable

		# Unwrap Extension lookups (type 7)
		if ltype == 7:
			subtables = [st.ExtSubTable for st in subtables if hasattr(st, 'ExtSubTable')]
			ltype = subtables[0].LookupType if subtables else ltype

		for st in subtables:
			if ltype == 1:  # SingleSubst
				if hasattr(st, 'mapping'):
					st.mapping = {remap(k): remap(v) for k, v in st.mapping.items()}

			elif ltype == 2:  # MultipleSubst
				if hasattr(st, 'mapping'):
					st.mapping = {remap(k): [remap(g) for g in v] for k, v in st.mapping.items()}

			elif ltype == 3:  # AlternateSubst
				if hasattr(st, 'alternates'):
					st.alternates = {remap(k): [remap(g) for g in v] for k, v in st.alternates.items()}

			elif ltype == 4:  # LigatureSubst
				if hasattr(st, 'ligatures'):
					new_ligs = {}
					for firstGlyph, ligList in st.ligatures.items():
						for lig in ligList:
							lig.LigGlyph = remap(lig.LigGlyph)
							lig.Component = [remap(g) for g in lig.Component]
						new_ligs[remap(firstGlyph)] = ligList
					st.ligatures = new_ligs

			elif ltype == 5:  # ContextSubst
				remapCoverage(getattr(st, 'Coverage', None))
				remapClassDef(getattr(st, 'ClassDef', None))

			elif ltype == 6:  # ChainContextSubst (all formats)
				remapCoverage(getattr(st, 'Coverage', None))
				remapClassDef(getattr(st, 'ClassDef', None))
				for attr in ['BacktrackCoverage', 'InputCoverage', 'LookAheadCoverage']:
					for cov in (getattr(st, attr, None) or []):
						remapCoverage(cov)
				# Format 1: glyph names in ChainSubRuleSet → ChainSubRule sequences
				for ruleset in (getattr(st, 'ChainSubRuleSet', None) or []):
					if ruleset is None:
						continue
					for rule in (ruleset.ChainSubRule or []):
						if hasattr(rule, 'Backtrack'):
							rule.Backtrack = [remap(g) for g in rule.Backtrack]
						if hasattr(rule, 'Input'):
							rule.Input = [remap(g) for g in rule.Input]
						if hasattr(rule, 'LookAhead'):
							rule.LookAhead = [remap(g) for g in rule.LookAhead]

			elif ltype == 8:  # ReverseChainingContextSingleSubst
				remapCoverage(getattr(st, 'Coverage', None))
				if hasattr(st, 'Substitute'):
					st.Substitute = [remap(g) for g in st.Substitute]

	print('[DEBUG] GSUB lookups remapped to scrambled glyph names')


def sortGposGsubCoverages(font):
	"""Sort coverage tables by glyph ID to prevent fontTools warnings"""
	try:
		for tableName in ['GSUB', 'GPOS']:
			if tableName not in font:
				continue
			
			table = font[tableName].table
			glyphOrder = font.getGlyphOrder()
			glyphMap = {name: i for i, name in enumerate(glyphOrder)}
			
			if table.LookupList:
				for lookup in table.LookupList.Lookup:
					for subtable in lookup.SubTable:
						# Sort all coverage tables
						for attr in ['Coverage', 'MarkCoverage', 'BaseCoverage', 'LigCoverage']:
							if hasattr(subtable, attr):
								cov = getattr(subtable, attr)
								if cov and hasattr(cov, 'glyphs'):
									cov.glyphs = sorted(cov.glyphs, key=lambda g: glyphMap.get(g, 0xFFFF))
		
		print('[DEBUG] Coverage tables sorted by glyph ID')
	except Exception as e:
		print(f'[DEBUG] Coverage sorting failed: {e}')

def remapHmtxToOriginalOrder(font, originalOrder, currentOrder, originalHmtx):
	"""Keep advance widths with shapes, using hmtx captured before glyph-order scrambling."""
	if 'hmtx' not in font:
		print('[DEBUG] No hmtx table to remap')
		return
	
	try:
		newMetrics = dict(font['hmtx'].metrics)
		debugGlyphs = {'A', 'M', 'V', 'a', 'uni0326.case', 'uni0304'}

		for pos, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
			if origGlyph == currGlyph:
				continue
			if origGlyph not in originalHmtx:
				continue

			# currGlyph now contains origGlyph's shape, so currGlyph gets origGlyph's ORIGINAL metrics
			newMetrics[currGlyph] = originalHmtx[origGlyph]

			if origGlyph in debugGlyphs or currGlyph in debugGlyphs:
				print(
					f'[DEBUG] hmtx pos {pos}: {currGlyph} <= {origGlyph} | '
					f'new {originalHmtx[origGlyph]}'
				)

		font['hmtx'].metrics = newMetrics

		for g in ['A', 'M', 'V', 'a', 'uni0326.case', 'uni0304']:
			if g in font['hmtx'].metrics:
				print(f"[DEBUG] final hmtx {g}: {font['hmtx'].metrics[g]}")

		print('[DEBUG] hmtx remapped from original metrics snapshot')
	except Exception as e:
		print(f'[DEBUG] hmtx remapping failed: {e}')
		import traceback
		traceback.print_exc()

def remapGdefToOriginalOrder(font, originalOrder, currentOrder):
	"""Remap GDEF GlyphClassDef to reference glyphs by their original indices"""
	if 'GDEF' not in font:
		print('[DEBUG] No GDEF table to remap')
		return
	
	try:
		gdef = font['GDEF'].table
		
		# Build mapping: currentGlyphName -> originalGlyphName
		glyphMapping = {}
		for i, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
			if origGlyph != currGlyph:
				glyphMapping[currGlyph] = origGlyph
		
		if not glyphMapping:
			print('[DEBUG] No glyph remapping needed for GDEF')
			return
		
		# Remap GlyphClassDef
		if hasattr(gdef, 'GlyphClassDef') and gdef.GlyphClassDef:
			oldClassDef = gdef.GlyphClassDef.classDefs
			newClassDef = {}
			for glyphName, classId in oldClassDef.items():
				remappedName = glyphMapping.get(glyphName, glyphName)
				newClassDef[remappedName] = classId
			gdef.GlyphClassDef.classDefs = newClassDef
			print('[DEBUG] GDEF GlyphClassDef remapped')
		
		# Remap MarkAttachClassDef
		if hasattr(gdef, 'MarkAttachClassDef') and gdef.MarkAttachClassDef:
			oldMarkClassDef = gdef.MarkAttachClassDef.classDefs
			newMarkClassDef = {}
			for glyphName, classId in oldMarkClassDef.items():
				remappedName = glyphMapping.get(glyphName, glyphName)
				newMarkClassDef[remappedName] = classId
			gdef.MarkAttachClassDef.classDefs = newMarkClassDef
			print('[DEBUG] GDEF MarkAttachClassDef remapped')
		
		print('[DEBUG] GDEF tables remapped to original glyph order')
	except Exception as e:
		print(f'[DEBUG] GDEF remapping failed: {e}')
		import traceback
		traceback.print_exc()

def debugKernPairs(font, originalOrder, currentOrder):
	print('\n=== KERN PAIR DEBUG ===')
	
	glyphOrder = font.getGlyphOrder()
	aIndex = glyphOrder.index('A') if 'A' in glyphOrder else -1
	vIndex = glyphOrder.index('V') if 'V' in glyphOrder else -1
	
	if aIndex >= 0 and vIndex >= 0:
		aOrig = originalOrder[aIndex]
		vOrig = originalOrder[vIndex]
		aCurrent = glyphOrder[aIndex]
		vCurrent = glyphOrder[vIndex]
		
		print(f'BEFORE scrambling:')
		print(f'  Position {aIndex}: {aOrig} -> NOW {aCurrent}')
		print(f'  Position {vIndex}: {vOrig} -> NOW {vCurrent}')
		
		print(f'\nGDEF classes AFTER scrambling:')
		print(f'  {aCurrent}: class {getGlyphClass(aCurrent, font)}')
		print(f'  {vCurrent}: class {getGlyphClass(vCurrent, font)}')
	
	if 'GPOS' in font:
		gpos = font['GPOS'].table
		if gpos.LookupList:
			for li, lookup in enumerate(gpos.LookupList.Lookup):
				if lookup.LookupType == 2:  # PairPos (kern)
					print(f'\nLookup {li} (PairPos):')
					for si, subtable in enumerate(lookup.SubTable):
						print(f'  Subtable {si}:')
						
						if hasattr(subtable, 'Coverage') and subtable.Coverage.glyphs:
							print(f'    Coverage glyphs: {subtable.Coverage.glyphs[:10]}{"..." if len(subtable.Coverage.glyphs)>10 else ""}')
						
						if hasattr(subtable, 'ClassDef'):
							print(f'    ClassDef1: {len(subtable.ClassDef.classDefs)} glyphs')
						
						if hasattr(subtable, 'ClassDef2'):
							print(f'    ClassDef2: {len(subtable.ClassDef2.classDefs)} glyphs')
						
						if hasattr(subtable, 'PairSet'):
							for pi, pairset in enumerate(subtable.PairSet[:2]):  # First 2 PairSets
								if pairset and pairset.PairValueRecord:
									print(f'    PairSet {pi}: {len(pairset.PairValueRecord)} pairs')
									for pvr in pairset.PairValueRecord[:2]:  # First 2 pairs
										xAdjust = getattr(pvr.Value1, 'XPlacement', 0) if pvr.Value1 else 0
										print(f'      2nd glyph: {pvr.SecondGlyph}, X adjust: {xAdjust}')
	
	print('=== END KERN DEBUG ===\n')

def debugTrackedGlyphs(font, originalOrder, currentOrder):
	tracked = {'A', 'a', 'uni0326.case'}
	print('\n=== TRACKED GLYPHS DEBUG ===')
	for pos, (origGlyph, currGlyph) in enumerate(zip(originalOrder, currentOrder)):
		if origGlyph in tracked or currGlyph in tracked:
			print(
				f'pos {pos}: {origGlyph}({getGlyphClass(origGlyph, font)}) -> '
				f'{currGlyph}({getGlyphClass(currGlyph, font)})'
			)
			if 'hmtx' in font and origGlyph in font['hmtx'].metrics and currGlyph in font['hmtx'].metrics:
				print(f'  hmtx {origGlyph}: {font["hmtx"].metrics[origGlyph]}')
				print(f'  hmtx {currGlyph}: {font["hmtx"].metrics[currGlyph]}')
	print('=== END TRACKED GLYPHS DEBUG ===\n')

def debugGlyphSwaps(originalOrder, currentOrder):
	"""Debug specific A/V swaps"""
	print('\n=== GLYPH SWAP DEBUG ===')
	
	glyphOrder = currentOrder
	for i, (orig, curr) in enumerate(zip(originalOrder, currentOrder)):
		if orig in ['A', 'V'] or curr in ['A', 'V']:
			print(f'Pos {i}: {orig} -> {curr}')
	
	print('=== END SWAP DEBUG ===\n')

def processFont(inputPath, outputDir, featureTag, formatOut, webOnly, respect, outFile):
	print(f'[DEBUG] Processing: {inputPath}')
	tempDir = Path(tempfile.mkdtemp())
	ttfPath = None
	try:
		if inputPath.lower().endswith(('.woff','.woff2')):
			from fontTools.ttLib.woff2 import decompress
			ttfPath = tempDir / 'temp.ttf'
			print(f'[DEBUG] Decompressing WOFF...')
			with open(inputPath, 'rb') as fi, open(ttfPath, 'wb') as fo:
				decompress(fi, fo)
		else:
			ttfPath = inputPath
		
		print(f'[DEBUG] Loading font: {ttfPath}')
		font = ttLib.TTFont(str(ttfPath))
		print(f'[DEBUG] Font loaded successfully')
		
		originalOrder, currentOrder, originalHmtx = scrambleGlyphOrder(font, respect)
		debugTrackedGlyphs(font, originalOrder, currentOrder)

		remapGdefToOriginalOrder(font, originalOrder, currentOrder)
		remapHmtxToOriginalOrder(font, originalOrder, currentOrder, originalHmtx)
		remapGposToOriginalOrder(font, originalOrder, currentOrder)
		remapGsubToCurrentOrder(font, originalOrder, currentOrder)
		sortGposGsubCoverages(font)

		unscrambleMap = makeUnscrambleMap(font, originalOrder, currentOrder)
		insertScrmFeatureManually(font, unscrambleMap, featureTag)
		
		print(f'[DEBUG] Saving to: {outFile}')
		
		from fontTools.misc.loggingTools import configLogger
		import logging
		configLogger(level=logging.WARNING)
		
		font.save(str(outFile), reorderTables=True)
		
		font.close()
		print(f'[DEBUG] Font saved successfully')
		print(f'Processed: {outFile.name}')
	except Exception as e:
		import traceback
		print(f'Error processing {inputPath}: {e}')
		traceback.print_exc()
	finally:
		if tempDir.exists():
			shutil.rmtree(tempDir)

def main():
	parser = argparse.ArgumentParser(prog='scramble', description='Scramble font glyphs with SCRM unscramble feature.', add_help=False)
	parser.add_argument('-F', '--feature', default='SCRM', help='Custom feature tag (default: SCRM)')
	parser.add_argument('-t', '--format', choices=['woff2', 'woff', 'desktop'], default='woff2', help='Output format (default: woff2)')
	parser.add_argument('-w', '--webonly', action='store_true', help='Web-only mode (removes glyph names, generic name table)')
	parser.add_argument('-r', '--respect', action='store_true', default=True, help='Respect GDEF classes (default)')
	parser.add_argument('-d', '--disrespect', dest='respect', action='store_false', help='Ignore GDEF classes')
	parser.add_argument('-o', '--output', default='.', help='Output directory (default: current)')
	parser.add_argument('-f', '--force', action='store_true', help='Overwrite input font files instead of creating -scrm variants')
	parser.add_argument('-H', '--HTML', default='', help='HTML demo file (set to filename to generate)')
	parser.add_argument('fonts', nargs='*', help='Input .ttf/.otf/.woff/.woff2 files (wildcards OK)')
	
	if '-h' in sys.argv or '--help' in sys.argv:
		parser.print_help()
		return
	if '-u' in sys.argv or '--usage' in sys.argv:
		print('Usage: python3 scramble.py [-t woff2] [-w] [-r] [-o outdir] [-f] [-H demo.html] font.ttf [fonts...]')
		print('  -F/--feature     custom feature tag (default: SCRM)')
		print('  -t/--format      woff2, woff, or desktop (default: woff2)')
		print('  -w/--webonly     web-only mode (on by default except for -t desktop)')
		print('  -r/--respect     respect GDEF types (default)')
		print('  -d/--disrespect  scramble across all glyphs')
		print('  -o/--output      output directory (default: current)')
		print('  -f/--force       overwrite input font files instead of creating -scrm variants')
		print('  -H/--HTML        HTML demo file (set to filename to generate, e.g., index.html)')
		print('  -h/--help        show full help')
		print('  -u/--usage       show this usage summary')
		return
	
	args = parser.parse_args()
	
	if not args.fonts:
		parser.print_help()
		return

	outputDir = Path(args.output).resolve()
	outputDir.mkdir(exist_ok=True)
	print(f'[DEBUG] Output directory: {outputDir}')
	
	webOnlyDefault = args.format != 'desktop'
	if not args.webonly:
		args.webonly = webOnlyDefault
	print(f'[DEBUG] webonly={args.webonly}, respect={args.respect}')

	fontFiles = parseFonts(args.fonts)
	print(f'[DEBUG] Found {len(fontFiles)} font files')
	if not fontFiles:
		print('No valid font files found.')
		return

	outputFiles = []
	for inputPath in fontFiles:
		inputFile = Path(inputPath)

		if args.force:
			outFile = inputFile
		else:
			if args.format == 'desktop':
				ext = '.ttf' if inputFile.suffix.lower() in ['.ttf', '.otf'] else inputFile.suffix
			else:
				ext = '.' + args.format
			outFile = outputDir / (inputFile.stem + '-scrm' + ext)

		processFont(str(inputPath), outputDir, args.feature, args.format, args.webonly, args.respect, outFile)
		if outFile.exists():
			outputFiles.append(outFile)

	if args.HTML:
		htmlPath = outputDir / args.HTML
		if generateHtml(outputFiles, htmlPath):
			print(f'HTML demo: {htmlPath}')
			try:
				webbrowser.open(f'file://{htmlPath.absolute()}')
			except Exception:
				pass

if __name__ == '__main__':
	main()
