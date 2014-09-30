"""
A demo/test of the CFHTLenS data structure and the Pointing class.
"""

import megalut.cfhtlens

import logging
logging.basicConfig(level=logging.INFO)


pointing = megalut.cfhtlens.utils.Pointing()

for code in pointing.good_codes + pointing.bad_codes:
	
	pointing.setcode(code)
	print pointing
	
	# Check that all files exist as expected (no need to repeatedly do this) :
	pointing.validate()

	# This pointing gives you access to all files. For instance:
	print pointing.catpath()

