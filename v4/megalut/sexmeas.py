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

def writeassoc(galaxies, filename):
	"""
	Function to write an "assoc-list" for sextractor, from a list of galaxy objects.
	It adds the "index" of a galaxy in the galaxies list as a third column.
	"""
	
	# We cannot use the galaxy ID here as it is too long.
	# At some point sextractor will write the ID as an rounded float and thus loose it !
	
	lines = []
	for (gindex, g) in enumerate(galaxies):
		lines.append("%.3f\t%.3f\t%i\n" % (g.x, g.y, gindex))

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
	settings_sex = os.path.join(sexparamsdir, "default.sex")
	settings_param = os.path.join(sexparamsdir, "default.param")
	settings_conv = os.path.join(sexparamsdir, "default.conv")

	cmd = "nice -n 10 sex %s -c %s -PARAMETERS_NAME %s -FILTER_NAME %s -CATALOG_NAME %s -ASSOC_NAME %s" % ( imgfilepath, 
		settings_sex, settings_param, settings_conv, sexcatfilepath, assocfilepath)
	print "Running SExtractor on image %s ..." % imgfilepath
	os.system(cmd)
	
	endtime = datetime.now()
	print "This SExtractor run took %s" % (str(endtime - starttime))

	

def readout(galaxies, sexcatfilepath, **kwargs):
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
	#print sexcat.info()

	# If ordered to, source selection:
	if 'source_selection' in kwargs and kwargs['source_selection']:
		print "Selecting galaxies..."

		sel=sourceselection.SourceSelect(sexcat, id_image=kwargs['id_image'])
		sel.default_removal()
		skiplist, skiplist_id = sel.get_skiplist()

	# End of source selection
	
	print "Identifying galaxies..."
	
	#gindexes = list(sexcat['VECTOR_ASSOC2'].tonumpy()) # Holy shit, it is super slow to search a python list with .index() !
	gindexes = sexcat['VECTOR_ASSOC2'].tonumpy() # Keep it as numpy
	
	notfound = 0
	if 'ds9' in kwargs and kwargs['ds9']: 
		f = open('regions_%03d.reg' % kwargs['id_image'], 'w')
		print >> f, """# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
image"""
	ngal = 0
	for (gindex, g) in enumerate(galaxies):
#		if 'nimg' in kwargs and not g.tru_nimg==kwargs['nimg']: continue
		ngal+=1
		try:
			i = np.where(gindexes == gindex)[0][0]
		except IndexError:
			g.mes_flux = -1.0
			notfound += 1
			#print "Couldn't find galaxy %s !" % (str(g));exit();
			continue
		
		# The much much slower way...
		#try:
		#	i = gindexes.index(gindex)
		#except ValueError:
		#	g.mes_flux = -1.0
		#	notfound += 1
		#	#print "Couldn't find galaxy %s !" % (str(g))
		#	continue
		if 'source_selection' in kwargs and kwargs['source_selection']:
			id_ = np.where(skiplist_id==i)[0]
			if skiplist[i]:
				g.mes_flux = -1.0
				continue

		g.mes_x = sexcat["XWIN_IMAGE"][i]
		g.mes_y = sexcat["YWIN_IMAGE"][i]
		g.mes_a = sexcat["AWIN_IMAGE"][i]
		g.mes_b = sexcat["BWIN_IMAGE"][i]
		g.mes_theta = sexcat["THETAWIN_IMAGE"][i]
		g.mes_fwhm = sexcat["FWHM_IMAGE"][i]
		g.mes_flux = sexcat["FLUX_AUTO"][i]
		g.mes_fluxerr = sexcat["FLUXERR_AUTO"][i]
		g.mes_snr = np.clip(g.mes_flux / g.mes_fluxerr, 0.0, 1.0e10)
		g.mes_rad30 = sexcat["FLUX_RADIUS"][i]
		g.mes_rad40 = sexcat["FLUX_RADIUS1"][i]
		g.mes_rad50 = sexcat["FLUX_RADIUS2"][i]
		g.mes_rad60 = sexcat["FLUX_RADIUS3"][i]
		g.mes_rad70 = sexcat["FLUX_RADIUS4"][i]
		g.mes_rad80 = sexcat["FLUX_RADIUS5"][i]
		g.mes_rad90 = sexcat["FLUX_RADIUS6"][i]
		g.mes_radkron = sexcat["KRON_RADIUS"][i]
	
		if 'ds9' in kwargs and kwargs['ds9']: print >> f,'circle(%2.6f,%2.6f,%2.6f)' % (sexcat["XWIN_IMAGE"][i],sexcat["YWIN_IMAGE"][i], 20)
	endtime = datetime.now()
	print "I could identify %.2f%% of the galaxies (%i out of %i are missing)." % (100.0 * float(ngal-notfound) / float(ngal), notfound, ngal)
	if 'source_selection' in kwargs and kwargs['source_selection']: print "%.2f%% passed the selections criteria (%i out of %i are removed)." % (100.0 * float(ngal-np.sum(skiplist)) / float(len(ngal)), np.sum(skiplist), ngal)
	print "This catalog-readout took %s" % (str(endtime - starttime))
	
	if 'ds9' in kwargs and kwargs['ds9']: 
		f.close()
		os.system('ds9 /obs/EPFL_GREAT3/control/ground/constant/image-%03d-0.fits -regions load regions_%03d.reg' % (kwargs['id_image'],kwargs['id_image']))
#BETTER: os.system('ds9 %s/image-%03d-0.fits -regions load regions_%03d.reg' % (kwargs['imagepath'],kwargs['id_image']))


def readout_noassoc(sexcatfilepath):
	"""
	Simply reads the catalog and returns a new list of galaxies.
	"""
	sexcat = asciidata.open(sexcatfilepath)
	print "We have %i galaxies in the sextractor catalog %s" % (sexcat.nrows, sexcatfilepath)
	
	galaxies = []
	for i in range(sexcat.nrows):
	
		g = galaxy.Galaxy()		
		g.mes_x = sexcat["XWIN_IMAGE"][i]
		g.mes_y = sexcat["YWIN_IMAGE"][i]
		g.mes_a = sexcat["AWIN_IMAGE"][i]
		g.mes_b = sexcat["BWIN_IMAGE"][i]
		g.mes_theta = sexcat["THETAWIN_IMAGE"][i]
		g.mes_fwhm = sexcat["FWHM_IMAGE"][i]
		g.mes_flux = sexcat["FLUX_AUTO"][i]
		g.mes_rad30 = sexcat["FLUX_RADIUS"][i]
		g.mes_rad50 = sexcat["FLUX_RADIUS1"][i]
		g.mes_rad70 = sexcat["FLUX_RADIUS2"][i]
		g.mes_rad90 = sexcat["FLUX_RADIUS3"][i]
		g.mes_radkron = sexcat["KRON_RADIUS"][i]
	
		galaxies.append(g)
	
	return galaxies
