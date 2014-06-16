

"""
I/O stuff directly related directly to GREAT3
"""


import numpy as np
import os
import megalut


def readcat(filepath):
	"""
	Reads a GREAT3 galaxy catalog and returns a list of galaxies
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
	
	
	#astropy.io.ascii.read(filepath, guess=False, Reader=astropy.io.ascii.sextractor.SExtractor)

def readstarcat(filepath):
	"""
	Reads a GREAT3 galaxy catalog and returns a list of galaxies
	"""
	
	print "Reading %s ..." % (filepath)
	data = np.loadtxt(filepath)
	
	def makestar(line):
		
		star = megalut.stars.Star()
		star.x = line[0]
		star.y = line[1]
		try:
			star.x_tile_index = line[2]
			star.y_tile_index = line[3]
			star.x_tile_true_deg = line[4]
			star.y_tile_true_deg = line[5]
			star.x_field_true_deg = line[6]
			star.y_field_true_deg = line[7]
		finally:
			return star
	
	stars = [makestar(line) for line in data]

	return stars
	

def writeshearcat(galaxies, filepath, weight=None, fact=None, radpsf=None, gmax=None, ignoreflag=False):
	"""
	weight is an attribute name you want me to write in the output file.
	"""
	
	if os.path.exists(filepath):
		os.remove(filepath)
	
	if fact != None:
		print "! WARNING, using fact = %f" % (fact)
	else:
		fact = 1.0
	
	if gmax != None:
		print "Using gmax of %.3f" % (gmax)
	
	if ignoreflag:
		print "! WARNING, I ignore the flag !"
	
	
	cat = open(filepath, "w")

	nbad = 0
	for ig,g in enumerate(galaxies):

		if g.mes_gs_flux <= 0.0 :
			g.pre_g1 = 20.0
			g.pre_g2 = 20.0
		
		if not ignoreflag:
			if hasattr(g, "flag"):
				if g.flag > 0:
					g.pre_g1 = 20.0
					g.pre_g2 = 20.0
		
		
		if g.pre_g1 > 19.0 or g.pre_g2 > 19.0:
			nbad += 1
			
		# Ugly, this should be done at the prediction stage !:
		if g.pre_g1 < 19.0 and g.pre_g2 < 19.0 and gmax != None:
			(g.pre_g1, g.pre_g2) = megalut.utils.clipg(g.pre_g1, g.pre_g2, gmax=gmax)
			
		if not weight:
			cat.write("%10i\t%+.6f\t%+.6f\n" % (int(g.ID), fact*g.pre_g1, fact*g.pre_g2))
		else:
			cat.write("%10i\t%+.6f\t%+.6f\t%+.6f\n" % (int(g.ID), fact*g.pre_g1, fact*g.pre_g2, g.weight))

	cat.close()
	ntot = len(galaxies)
	print "%i / %i galaxies are not good (%.3f %%)" % (nbad, ntot, float(nbad)/float(ntot)*100.0) 
	
	print "Wrote %s" % (filepath)
	
	
	
	


