"""
I/O functions directly related to the GREAT3 files
"""


import numpy as np
import os


def readgalcat(filepath):
	"""
	Reads a GREAT3 galaxy catalog and returns a catalog
	"""
	
	print "Reading %s ..." % (filepath)
	data = np.loadtxt(filepath)
	
	def makegal(line):
		
		gal = megalut.galaxy.Galaxy()
		gal.x = line[0]
		gal.y = line[1]
		gal.ID = int(line[2])
		try:
		# This only exists if branch is variable_psf
			gal.x_tile_index = line[3]
			gal.y_tile_index = line[4]
			gal.x_tile_true_deg = line[5]
			gal.y_tile_true_deg = line[6]
			gal.x_field_true_deg = line[7]
			gal.y_field_true_deg = line[8]
		finally:
			return gal
	
	galaxies = [makegal(line) for line in data]
	
	# We test the IDs for uniqueness...
	IDs = [g.ID for g in galaxies]
	assert len(set(IDs)) == len(IDs)
	
	return galaxies
	