"""
Shape measurement with SExtractor
"""

import numpy as np
import math
import random
import utils
import os
import asciidata
from datetime import datetime
import galaxy
import sourceselection
import math

def writeassoc(stars, filename, nimg=None):
	"""
	Function to write an "assoc-list" for sextractor, from a list of stars objects.
	It adds the "index" of a star in the stars list as a third column.
	"""
	
	# We cannot use the galaxy ID here as it is too long.
	# At some point sextractor will write the ID as an rounded float and thus loose it !
	
	lines = []
	for (sindex, s) in enumerate(stars):
		if not nimg == None and not s.tru_nimg==nimg: continue
		lines.append("%.3f\t%.3f\t%i\n" % (s.x, s.y, sindex))

	lines = "".join(lines)
	f = open(filename, "w")
	f.writelines(lines)
	f.close()
	print "Wrote %s" % filename


def run(imgfilepath, sexcatfilepath, assocfilepath):
	"""
	Runs sextractor on the image
	"""

	starttime = datetime.now()	

	sexparamsdir = os.path.join(os.path.dirname(__file__), "sexparams")
	settings_sex = os.path.join(sexparamsdir, "stars.sex")
	settings_param = os.path.join(sexparamsdir, "stars.param")
	settings_conv = os.path.join(sexparamsdir, "default.conv")

	cmd = "nice -n 19 sex %s -c %s -PARAMETERS_NAME %s -FILTER_NAME %s -CATALOG_NAME %s -ASSOC_NAME %s" % ( imgfilepath, 
		settings_sex, settings_param, settings_conv, sexcatfilepath, assocfilepath)
	print "Running SExtractor on image %s ..." % imgfilepath
	os.system(cmd)
	
	endtime = datetime.now()
	print "This SExtractor run took %s" % (str(endtime - starttime))

	

def readout(stars, sexcatfilepath):
	"""
	Reads in shape measurements from a sextractor catalog.
	Uses the ASSOC mecanism to identify galaxies.
	
	galaxies = a list of galaxy objects
	sexcatfilepath = path to sex catoalog
	
	I find each galaxy in the catalog, and get its measured shape.
	For this I use the "third col" assoc data of the sex catalog, which gives the ID of the galaxy.
	"""


	print "Reading catalog..."
	starttime = datetime.now()	

	sexcat = asciidata.open(sexcatfilepath)
	print "We have %i galaxies in the sextractor catalog %s" % (sexcat.nrows, sexcatfilepath)

	print "Identifying stars..."
	
	sindexes = sexcat['VECTOR_ASSOC2'].tonumpy() # Keep it as numpy
	
	notfound = 0
	nstars = 0
	for (sindex, s) in enumerate(stars):
		try:
			i = np.where(sindexes == sindex)[0][0]
		except IndexError:
			notfound += 1
			#print "Couldn't find galaxy %s !" % (str(g));exit();
			continue

		s.mes_x = sexcat["XWIN_IMAGE"][i]
		s.mes_y = sexcat["YWIN_IMAGE"][i]
		s.mes_a = sexcat["AWIN_IMAGE"][i]
		s.mes_b = sexcat["BWIN_IMAGE"][i]
		s.mes_theta = sexcat["THETAWIN_IMAGE"][i]
		s.mes_fwhm = sexcat["FWHM_IMAGE"][i]
		s.mes_flux = sexcat["FLUX_AUTO"][i]
		s.mes_fluxerr = sexcat["FLUXERR_AUTO"][i]
		s.mes_flux_max = sexcat["FLUX_MAX"][i]
		s.mes_fwhm = sexcat["FWHM_IMAGE"][i]
		s.mes_equivrad = math.sqrt(s.mes_flux/math.pi/s.mes_flux_max)
		print s.mes_x, s.mes_y, s.mes_equivrad,s.mes_fwhm

		nstars+=1

	print '-----------------'
	
	endtime = datetime.now()
	print "I could identify %.2f%% of the stars (%i out of %i are missing)." % (100.0 * float(nstars-notfound) / float(nstars), notfound, nstars)
	print "This catalog-readout took %s" % (str(endtime - starttime))	


