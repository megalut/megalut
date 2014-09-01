"""
I/O functions directly related to the GREAT3 files
"""

import logging
import numpy as np
import os

import astropy.table
#from .. import catalog

logger = logging.getLogger(__name__)



def readgalcat(branch, subfield):
	"""
	I read the galaxy catalog for a given branch and subfield.
	:returns: An astropy.table 
	"""
	
	filepath = branch.galcatfilepath(subfield)
	
	# There is probably a direct astropy way to read the data
	#cat = astropy.table.Table.read(filepath, format="ascii")
	#cat.rename_column('col1', 'ID')
	
	# But instead, let's try with numpy to illustrate maximum control:
	data = np.loadtxt(filepath)
	
	assert data.shape[1] == 3
	
	ids = [int(line[2]) for line in data]
	xs = data[:,0]
	ys = data[:,1]
	
	cat = astropy.table.Table([ids, xs, ys],
		names=('ID', 'x', 'y'),
		meta = {"branch":branch, "subfield":subfield, "filepath":filepath}
		)
		
	logger.info("Read %i sources from %s" % (len(cat), filepath))

	return cat



# def readgalcataslist(filepath):
# 	"""
# 	I return a list of Galaxy objects.
# 	"""
# 
# 	data = np.loadtxt(filepath)
# 	def makegal(line):
# 		
# 		gal = catalog.Galaxy(id=str(int(line[2])))
# 		gal.fields = {"x":line[0], "y":line[1]}
# 		
# 		#try:
# 		# This only exists if branch is variable_psf
# 		#	gal.x_tile_index = line[3]
# 		#	gal.y_tile_index = line[4]
# 		#	gal.x_tile_true_deg = line[5]
# 		#	gal.y_tile_true_deg = line[6]
# 		#	gal.x_field_true_deg = line[7]
# 		#	gal.y_field_true_deg = line[8]
# 		#finally:
# 		#	return gal
# 		
# 		return gal
# 	
# 	galaxies = [makegal(line) for line in data]
# 	logger.info("Read %i galaxies from %s" % (len(galaxies), filepath))
# 	return galaxies
# 
# 
# 
# def readgalcat(branch, subfield):
# 	"""
# 	Reads in a GREAT3 galaxy catalog as a MegaLUT catalog
# 	You give me a branch, instead of a filepath.
# 	"""
# 	
# 	filepath = branch.galcatfilepath(subfield)
# 	
# 	galaxies = readgalcataslist(filepath)
# 	
# 	return catalog.Catalog(galaxies, meta={"branch":branch, "subfield":subfield, "filepath":filepath})
# 	
