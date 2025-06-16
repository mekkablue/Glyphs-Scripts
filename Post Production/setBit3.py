#!/usr/bin/env python3
import argparse
from fontTools.ttLib import TTFont

def modify_head_flags(font_path, bit_value, output_path):
	with TTFont(font_path) as font:
		head = font['head']
		
		if bit_value == 1:
			head.flags |= 1 << 3  # Set bit 3 (value 8)
		else:
			head.flags &= ~(1 << 3)  # Clear bit 3
		
		font.save(output_path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='Modify head.flags bit 3 in OpenType fonts',
		)
	parser.add_argument(
		'fonts',
		nargs='+',
		help='input font files',
		)
	parser.add_argument(
		'-b',
		'--bit',
		type=int,
		choices=[0,1],
		default=1,
		help='set bit value (0 or 1, default=1)',
		)
	parser.add_argument(
		'-o',
		'--output',
		help='output file (if not specified, will overwrite input file)',
		)
	
	args = parser.parse_args()
	
	for font_path in args.fonts:
		output = args.output or font_path
		modify_head_flags(font_path, args.bit, output)
		if font_path != output:
			print(f"✅ Updated bit 3 to value {args.bit} in {font_path} -> {output}")
		else:
			print(f"✅ Updated bit 3 to value {args.bit} in {font_path}")
	print()