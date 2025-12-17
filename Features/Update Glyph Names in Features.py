#MenuTitle: Update Glyph Names in Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Like Glyph > Update Glyph Info, but in Font Info > Features.
"""

import re
from GlyphsApp import Glyphs, GSGlyphsInfo

RESERVED = {
	"feature", "lookup", "languagesystem", "script", "language", "table", "include", "ignore",
	"sub", "substitute", "by", "from", "pos", "position", "enum", "enumerate", "del", "delete",
	"markClass", "anchorDef", "valueRecordDef",
	"useExtension", "parameters", "excludeDFLT",
	"lookupflag", "UseMarkFilteringSet", "MarkAttachmentType", "IgnoreMarks", "IgnoreBaseGlyphs", "RightToLeft",
	'adlm', 'ahom', 'hluw', 'arab', 'armn', 'avst', 'bali', 'bamu', 'bass', 'batk', 'beng', 'bng2', 'berf', 'bhks', 'bopo', 'brah', 'brai', 'bugi', 'buhd', 'byzm', 'cans', 'cari', 'aghb', 'cakm', 'cham', 'cher', 'chrs', 'hani', 'copt', 'cprt', 'cpmn', 'cyrl', 'dsrt', 'deva', 'dev2', 'diak', 'dogr', 'dupl', 'egyp', 'elba', 'elym', 'ethi', 'gara', 'geor', 'glag', 'goth', 'gran', 'grek', 'gujr', 'gjr2', 'gong', 'guru', 'gur2', 'gukh', 'hang', 'jamo', 'hang', 'rohg', 'hano', 'hatr', 'hebr', 'kana', 'armi', 'phli', 'prti', 'java', 'kthi', 'knda', 'knd2', 'kana', 'kawi', 'kali', 'khar', 'kits', 'khmr', 'khoj', 'sind', 'krai', 'lao ', 'latn', 'lepc', 'limb', 'lina', 'linb', 'lisu', 'lyci', 'lydi', 'mahj', 'maka', 'mlym', 'mlm2', 'mand', 'mani', 'marc', 'gonm', 'math', 'medf', 'mtei', 'mend', 'merc', 'mero', 'plrd', 'modi', 'mong', 'mroo', 'mult', 'musc', 'mymr', 'mym2', 'mym2', 'nbat', 'nagm', 'nand', 'newa', 'talu', 'nko ', 'nshu', 'hmnp', 'orya', 'ory2', 'ogam', 'olck', 'onao', 'ital', 'hung', 'narb', 'perm', 'xpeo', 'sogo', 'sarb', 'orkh', 'ougr', 'osge', 'osma', 'hmng', 'palm', 'pauc', 'phag', 'phnx', 'phlp', 'rjng', 'runr', 'samr', 'saur', 'shrd', 'shaw', 'sidd', 'sidt', 'sgnw', 'sinh', 'sogd', 'sora', 'soyo', 'xsux', 'sund', 'sunu', 'sylo', 'syrc', 'tglg', 'tagb', 'tale', 'lana', 'tavt', 'tayo', 'takr', 'taml', 'tml2', 'tnsa', 'tang', 'telu', 'tel2', 'thaa', 'thai', 'tibt', 'tfng', 'tirh', 'todr', 'tols', 'toto', 'tutg', 'ugar', 'vai ', 'vith', 'wcho', 'wara', 'yezi', 'yi  ', 'zanb',
	'AAQ', 'ABA', 'ABK', 'ACH', 'ACR', 'ACY', 'ADY', 'AFK', 'AFR', 'AGW', 'AIO', 'AKA', 'AKB', 'ALS', 'ALT', 'AMH', 'ANG', 'ARA', 'ARG', 'ARI', 'ARK', 'ASM', 'AST', 'ATH', 'ATS', 'AVN', 'AVR', 'AWA', 'AYM', 'AZB', 'AZE', 'BAD', 'BAG', 'BAL', 'BAN', 'BAR', 'BAU', 'BBC', 'BBR', 'BCH', 'BCR', 'BDC', 'BDY', 'BEL', 'BEM', 'BEN', 'BGC', 'BGQ', 'BGR', 'BHI', 'BHO', 'BIK', 'BIL', 'BIS', 'BJJ', 'BKF', 'BLI', 'BLK', 'BLN', 'BLT', 'BMB', 'BML', 'BOS', 'BPY', 'BRE', 'BRH', 'BRI', 'BRM', 'BRX', 'BSH', 'BSK', 'BTD', 'BTI', 'BTK', 'BTM', 'BTS', 'BTX', 'BTZ', 'BUG', 'BYV', 'CAK', 'CAT', 'CAY', 'CBG', 'CBK', 'CEB', 'CGG', 'CHA', 'CHE', 'CHG', 'CHH', 'CHI', 'CHK', 'CHO', 'CHP', 'CHR', 'CHU', 'CHY', 'CJA', 'CJM', 'CMI', 'CMR', 'COO', 'COP', 'COR', 'COS', 'CPP', 'CRE', 'CRR', 'CRT', 'CSB', 'CSL', 'CSY', 'CTG', 'CTO', 'CTT', 'CUK', 'DAG', 'DAN', 'DAR', 'DAX', 'DCR', 'DEU', 'DGO', 'DGR', 'DHG', 'DHV', 'DIQ', 'DIV', 'DJR', 'DNG', 'DNJ', 'DNK', 'DRI', 'DUJ', 'DUN', 'DZN', 'EBI', 'ECR', 'EDO', 'EFI', 'ELL', 'EMK', 'EMP', 'ENG', 'ERZ', 'ESP', 'ESU', 'ETI', 'EUQ', 'EVK', 'EVN', 'EWE', 'FAN', 'FAR', 'FAT', 'FIN', 'FJI', 'FLE', 'FMP', 'FNE', 'FON', 'FOS', 'FRA', 'FRC', 'FRI', 'FRL', 'FRP', 'FTA', 'FUL', 'FUV', 'GAD', 'GAE', 'GAG', 'GAL', 'GAR', 'GAW', 'GEZ', 'GIH', 'GIL', 'GKP', 'GLK', 'GMZ', 'GNN', 'GOG', 'GON', 'GRN', 'GRO', 'GUA', 'GUC', 'GUF', 'GUJ', 'GUZ', 'HAI', 'HAL', 'HAR', 'HAU', 'HAW', 'HAY', 'HAZ', 'HBN', 'HEI', 'HER', 'HIL', 'HIN', 'HMA', 'HMD', 'HMN', 'HMO', 'HMZ', 'HND', 'HRI', 'HRV', 'HUN', 'HUR', 'HYE', 'IBA', 'IBB', 'IBO', 'IDO', 'IJO', 'ILE', 'ILO', 'INA', 'IND', 'ING', 'INU', 'IPK', 'IRI', 'IRT', 'IRU', 'ISL', 'ISM', 'ITA', 'IWR', 'JAM', 'JAN', 'JAV', 'JBO', 'JCT', 'JDT', 'JII', 'JUD', 'JUL', 'KAB', 'KAC', 'KAL', 'KAN', 'KAR', 'KAT', 'KAW', 'KAZ', 'KBC', 'KDE', 'KEA', 'KEB', 'KEK', 'KGE', 'KGF', 'KHA', 'KHK', 'KHM', 'KHS', 'KHT', 'KHV', 'KHW', 'KIK', 'KIR', 'KIS', 'KIU', 'KJD', 'KJJ', 'KJP', 'KJZ', 'KKN', 'KLM', 'KMB', 'KMG', 'KMN', 'KMO', 'KMS', 'KMZ', 'KNR', 'KOD', 'KOH', 'KOK', 'KOM', 'KON', 'KOP', 'KOR', 'KOS', 'KOZ', 'KPL', 'KRI', 'KRK', 'KRL', 'KRM', 'KRN', 'KRT', 'KSH', 'KSI', 'KSM', 'KSU', 'KSW', 'KUA', 'KUI', 'KUL', 'KUM', 'KUR', 'KUU', 'KUY', 'KVQ', 'KWK', 'KYK', 'KYU', 'LAD', 'LAH', 'LAK', 'LAM', 'LAO', 'LAT', 'LAZ', 'LCR', 'LDK', 'LEF', 'LEZ', 'LIJ', 'LIM', 'LIN', 'LIS', 'LIV', 'LJP', 'LKI', 'LMA', 'LMB', 'LMO', 'LMW', 'LOM', 'LPO', 'LRC', 'LSB', 'LSM', 'LTH', 'LTZ', 'LUA', 'LUB', 'LUG', 'LUH', 'LUO', 'LUT', 'LVI', 'MAD', 'MAG', 'MAH', 'MAJ', 'MAK', 'MAL', 'MAM', 'MAN', 'MAP', 'MAR', 'MAW', 'MBN', 'MBO', 'MCH', 'MCR', 'MDE', 'MDR', 'MEN', 'MER', 'MEV', 'MFA', 'MFE', 'MIN', 'MIZ', 'MKD', 'MKR', 'MKW', 'MLE', 'MLG', 'MLN', 'MLR', 'MLY', 'MND', 'MNG', 'MNI', 'MNK', 'MNX', 'MOH', 'MOK', 'MOL', 'MON', 'MOR', 'MOS', 'MRI', 'MTH', 'MTS', 'MUN', 'MUS', 'MWL', 'MWW', 'MYN', 'MZN', 'NAG', 'NAH', 'NAN', 'NAP', 'NAS', 'NAU', 'NAV', 'NCR', 'NDB', 'NDC', 'NDG', 'NDS', 'NEP', 'NEW', 'NGA', 'NGR', 'NHC', 'NIS', 'NIU', 'NKL', 'NKO', 'NLD', 'NOE', 'NOG', 'NOP', 'NOR', 'NOV', 'NSM', 'NSO', 'NTA', 'NTO', 'NUK', 'NYM', 'NYN', 'NZA', 'OCI', 'OCR', 'OJB', 'ONE', 'ONO', 'ORI', 'ORO', 'OSS', 'PAA', 'PAG', 'PAL', 'PAM', 'PAN', 'PAP', 'PAS', 'PAU', 'PCC', 'PCD', 'PDC', 'PGR', 'PHK', 'PIH', 'PIL', 'PLG', 'PLK', 'PMS', 'PNB', 'POH', 'PON', 'PRO', 'PTG', 'PWO', 'QIN', 'QUC', 'QUH', 'QUZ', 'QVI', 'QWH', 'RAJ', 'RAR', 'RBU', 'RCR', 'REJ', 'RIA', 'RHG', 'RIF', 'RIT', 'RKW', 'RMS', 'RMY', 'ROM', 'ROY', 'RSY', 'RTM', 'RUA', 'RUN', 'RUP', 'RUS', 'SAD', 'SAN', 'SAS', 'SAT', 'SAY', 'SCN', 'SCO', 'SCS', 'SEE', 'SEK', 'SEL', 'SFM', 'SGA', 'SGO', 'SGS', 'SHI', 'SHN', 'SIB', 'SID', 'SIG', 'SJA', 'SJE', 'SJU', 'SKS', 'SKY', 'SLA', 'SLV', 'SML', 'SMO', 'SNA', 'SND', 'SNH', 'SNK', 'SOG', 'SOP', 'SOT', 'SQI', 'SRB', 'SRD', 'SRK', 'SRR', 'SSL', 'SSM', 'STR', 'STQ', 'SUK', 'SUN', 'SUR', 'SVA', 'SVE', 'SWA', 'SWK', 'SWZ', 'SXT', 'SXU', 'SYL', 'SYR', 'SZL', 'TAB', 'TAJ', 'TAM', 'TAQ', 'TMH', 'TAT', 'TBV', 'TCR', 'TDC', 'TDD', 'TEL', 'TET', 'TGL', 'TGN', 'TGR', 'TGY', 'THA', 'THT', 'THP', 'THV', 'TMH', 'THZ', 'TMH', 'TIB', 'TIV', 'TJL', 'TKM', 'TLI', 'TMH', 'TAQ', 'THV', 'THZ', 'TTQ', 'TLY', 'TMN', 'TNA', 'TNE', 'TNG', 'TOD', 'TPI', 'TRK', 'TSG', 'TSJ', 'TTQ', 'TMH', 'TUA', 'TUL', 'TUM', 'TUS', 'TUV', 'TVL', 'TWI', 'TYZ', 'TZM', 'TZO', 'UDI', 'UDM', 'UKR', 'UMB', 'URD', 'USB', 'UYG', 'UZB', 'VEC', 'VEN', 'VIT', 'VOL', 'VRO', 'WAG', 'WAR', 'WBL', 'WCI', 'WCR', 'WDT', 'WEL', 'WLF', 'WLN', 'WTM', 'WYN', 'XBD', 'XHS', 'XJB', 'XKF', 'XOG', 'XPE', 'XUB', 'XUJ', 'YAK', 'YAO', 'YAP', 'YBA', 'YCR', 'YGP', 'YIC', 'YIM', 'YNA', 'YUF', 'YWQ', 'ZEA', 'ZGH', 'ZHA', 'ZHH', 'ZHP', 'ZHS', 'ZHT', 'ZND', 'ZUL', 'ZZA',
}

GLYPHNAMEREGEX = re.compile(r'([A-Za-z._][A-Za-z0-9_.-]*)')

font = Glyphs.font
if not font:
	raise Exception("No font open.")

Glyphs.clearLog()
print("Update Glyph Names in Features")
print(f"📄 {font.filepath or font.familyName}")
allGlyphNames = [g.name for g in font.glyphs]


def updateName(name):
	if name in allGlyphNames:
		return name
	newName = font.glyphsInfo().niceGlyphNameForName_(name) or name
	if newName not in allGlyphNames:
		print(f"⚠️ Glyph name not in font: {'/'.join(list(set([name, newName])))}. Left unchanged.")
		return name
	return newName


def updateLine(line):
	def repl(m):
		name = m.group(1)
		if name in RESERVED:
			return name
		newName = updateName(name)
		return newName if newName else name
	return GLYPHNAMEREGEX.sub(repl, line)


def convertCodeToNiceNames(feature):
	if feature.automatic:
		return
	featureCode = feature.code
	codeLines = featureCode.splitlines()
	change = 0
	for i in range(len(codeLines)):
		oldLine, comment = codeLines[i], None
		if "#" in oldLine:
			oldLine, comment = oldLine.split("#", maxsplit=1)
		newLine = updateLine(oldLine)
		if comment:
			newLine += "#" + comment
		if oldLine != newLine:
			codeLines[i] = newLine
			change += 1
	if change != 0:
		print(f"🕹️ {feature.name}: {change} line{'' if change==1 else 's'} updated.")
		feature.code = "\n".join(codeLines)


print("\n⚙️ Updating OT Features...")
for otFeature in font.features:
	convertCodeToNiceNames(otFeature)

print("\n⚙️ Updating OT Prefixes...")
for otPrefix in font.featurePrefixes:
	convertCodeToNiceNames(otPrefix)

print("\n⚙️ Updating OT Classes...")
for otClass in font.classes:
	convertCodeToNiceNames(otClass)

print("\n✅ Done.")
font.parent.windowController().showFontInfoWindowWithTabSelected_(3)
