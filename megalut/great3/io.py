"""
I/O functions directly related to the GREAT3 files
"""


import numpy as np
import os

from .. import catalog


def readgalcataslist(filepath):
	"""
	I return a list of Galaxy objects.
	"""

	data = np.loadtxt(filepath)
	def makegal(line):
		
		gal = catalog.Galaxy(id=str(int(line[2])))
		gal.fields = {"x":line[0], "y":line[1]}
		
		#try:
		# This only exists if branch is variable_psf
		#	gal.x_tile_index = line[3]
		#	gal.y_tile_index = line[4]
		#	gal.x_tile_true_deg = line[5]
		#	gal.y_tile_true_deg = line[6]
		#	gal.x_field_true_deg = line[7]
		#	gal.y_field_true_deg = line[8]
		#finally:
		#	return gal
		
		return gal
	
	galaxies = [makegal(line) for line in data]
	return galaxies



def readgalcat(branch, subfield):
	"""
	Reads in a GREAT3 galaxy catalog as a MegaLUT catalog
	You give me a branch, instead of a filepath.
	"""
	
	filepath = branch.galcatfilepath(subfield)
	
	galaxies = readgalcataslist(filepath)
	
	return catalog.Catalog(galaxies, meta={"branch":branch, "filepath":filepaths})
	
