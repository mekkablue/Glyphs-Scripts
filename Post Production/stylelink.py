"""
stylelink.py

Usage:
  python3 stylelink.py [options] fontfile1 [fontfile2 ...]

Options:
  -b, --bold       Set bold style bits
  -i, --italic     Set italic style bits
  --auto           Derive bold/italic bits automatically from nameID 2 subfamily string
  fontfile(s)      One or more .ttf or .otf font files, supports wildcards e.g. *.ttf

Description:
  Sets or clears the 'bold' and 'italic' bits in the 'head' and 'OS/2' tables of TrueType or OpenType fonts.
  When --auto is specified, style bits are inferred from the font's nameID 2 subfamily string, which must be one of:
  "Regular", "Bold", "Italic", or "Bold Italic".

Examples:
  python3 stylelink.py -b -i myfont-bolditalic.ttf
  python3 stylelink.py --auto font1.ttf font2.otf
  python3 stylelink.py --auto *.ttf

"""

import argparse
import glob
from fontTools.ttLib import TTFont

BOLD_MASK = 1 << 0		 # head.macStyle bit 0
ITALIC_MASK = 1 << 1	   # head.macStyle bit 1
OS2_BOLD_MASK = 1 << 5	 # OS/2.fsSelection bit 5
OS2_ITALIC_MASK = 1 << 0   # OS/2.fsSelection bit 0
OS2_REGULAR_MASK = 1 << 6  # OS/2.fsSelection bit 6

def derive_styles_from_name(font):
	# Try nameID 2, prefer Windows English first
	for record in font['name'].names:
		if record.nameID == 2 and ((record.platformID == 3 and record.langID == 0x409) or record.platformID == 1):
			style = record.toUnicode().strip().lower()
			break
	else:
		# Fallback to first nameID 2 record
		style = font['name'].getDebugName(2).strip().lower()
	if style == "bold":
		return True, False
	elif style == "italic":
		return False, True
	elif style == "bold italic":
		return True, True
	else:  # Regular
		return False, False

def set_style_bits(font, bold=False, italic=False):
	# Update head.macStyle
	macStyle = 0
	if bold:
		macStyle |= BOLD_MASK
	if italic:
		macStyle |= ITALIC_MASK
	font['head'].macStyle = macStyle

	# Update OS/2.fsSelection bits
	fsSelection = font['OS/2'].fsSelection

	if bold:
		fsSelection |= OS2_BOLD_MASK
	else:
		fsSelection &= ~OS2_BOLD_MASK

	if italic:
		fsSelection |= OS2_ITALIC_MASK
	else:
		fsSelection &= ~OS2_ITALIC_MASK

	# Regular bit
	if not bold and not italic:
		fsSelection |= OS2_REGULAR_MASK
	else:
		fsSelection &= ~OS2_REGULAR_MASK

	font['OS/2'].fsSelection = fsSelection


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Set Bold/Italic/Regular style bits in font files.")
	parser.add_argument("-b", "--bold", action="store_true", help="Set bold bits")
	parser.add_argument("-i", "--italic", action="store_true", help="Set italic bits")
	parser.add_argument("--auto", action="store_true", help="Derive bold/italic from nameID 2")
	parser.add_argument("fontfiles", nargs='+', help="Input .ttf/.otf font files (supports wildcards)")
	args = parser.parse_args()

	# Expand any globs in file arguments
	files_to_process = []
	for pattern in args.fontfiles:
		files_to_process.extend(glob.glob(pattern))

	for fontfile in files_to_process:
		font = TTFont(fontfile)
		if args.auto:
			bold, italic = derive_styles_from_name(font)
		else:
			bold, italic = args.bold, args.italic

		set_style_bits(font, bold=bold, italic=italic)
		font.save(fontfile)
		print(f"Processed {fontfile}")
