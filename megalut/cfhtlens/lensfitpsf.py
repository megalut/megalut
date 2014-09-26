"""
Code related to the PSF interpolation performed by lensfit on CFHTLenS and cie. 

"""

import os
import subprocess
import shutil
import glob
import astropy
import numpy as np
import math
import copy

import logging
logger = logging.getLogger(__name__)

from .. import utils as megalututils


def writecat(cat, filepath):
	"""
	Dedicated function to write the plain input catalog required for createPSFcube
	"""
	
	f = open(filepath, "w")
	for row in cat:
		f.write("%.8f %.8f\n" % (row["ALPHA_J2000"], row["DELTA_J2000"]))
	f.close()
	logger.info("Wrote %i entries into %s" % (len(cat), filepath))

	


def makeexppsfs(cat, pointing, workdir="."):
	"""
	
	Runs createPSFcube for every source in cat and on every exposure of that pointing.
	
	createPSFcube only works if its argument is just the basename of the explist (not the full path)
	So we have to copy that file and chdir. This is very ugly, to not immitate if not required !
	
	"""
	
	exps = pointing.explists()
	logger.info("I will work on %i exposures: %s" % (len(exps), ", ".join(exps)))

	
	if not os.path.isdir(workdir):
		os.mkdir(workdir)
	
	# VERY IMPORTANT: we have to go back to the current dir at the end of this function !
	cwd = os.getcwd()
	os.chdir(workdir)
	
	writecat(cat, "cat.txt")
	
	# We prepare the environment...
	env = dict(os.environ)
	env.update({ # Does not modify os.environ.
		"PSF_DIR":pointing.psfdir(),
		"DATA_DIR":pointing.datadir(),
		"HEAD_DIR":pointing.headdir(),
		"SWARP_CONFIG":pointing.swarpconfig(),
		"CATALOGUE":"cat.txt"
	})
	#print env
	#print os.environ
	
	
	for exp in exps:
		
		logger.info("Making PSF stamps for exposure %s..." % (exp))

		chiplistpath = os.path.join(pointing.explistdir(), exp + ".list")
		
		shutil.copy(chiplistpath, ".")
		
		#os.system("createPSFcube %s" % (exp+".list"))
		
		p = subprocess.Popen(["createPSFcube", exp+".list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
		
		# We write the output into a log file...
		logfile = open(exp + ".log", "w")
		logfile.write("======= This is the output of createPSFcube =========\n")
		out, err = p.communicate()
		logfile.write(out)
		logfile.write("======= And this is the stderr =========\n")
		logfile.write(err)
		logfile.close()
		
		# And show errors as log.warnings :
		if err != "":
			logger.warning(err)


	os.chdir(cwd) # It's quite a mess if you don't go back to where you left !
	print os.getcwd()
	

def stackexppsfs(cat, workdir, gridwidth=50):
	"""
	I stack the PSFs from the individual exposures.
	I do my business by looking at what I find in the workdir, autonomously.
	
	
	Should this be split into stacking and making grid ?
	"""
	cubestocoadd = sorted(glob.glob(os.path.join(workdir, "*.list_psfcube.fits")))
	#print cubestocoadd
		
	data = astropy.io.fits.getdata(cubestocoadd[0]) # Careful, we do not do the usual transpose here !
	assert data.shape[0] == len(cat)
	assert data.shape[1] == data.shape[2]
	
	stampsize = data.shape[1]
	
	
	logger.info("Will stack %i psfs from %i exposures..." % (len(cat), len(cubestocoadd)))
	logger.info("Stamp size is %i" % (stampsize))

	stack = np.zeros(data.shape) # this is for the stamps
	counter = np.zeros(data.shape[0]) # this is to keep track of how much stamps we have for each source.


	# We loop over the FITS files:
	for cubetocoadd in cubestocoadd:
		data = astropy.io.fits.getdata(cubetocoadd)
		stack += data
		
		maxofstamps = np.max(np.max(data, axis=1), axis=1)
		hasdata = maxofstamps > 0.0001 # This is boolean
		
		counter += hasdata.astype(int) # We add 1 where we had data
	
	logger.info("Done with stacking, now making grid...")

	# We arrange all the stacked stamps on a grid
	
	gridheight = int(math.ceil(float(len(cat)) / gridwidth))
	
	logger.info("The grid will be %i x %i (%i tiles)" % (gridwidth, gridheight, gridwidth * gridheight))
	
	grid = np.zeros((gridwidth*stampsize, gridheight*stampsize))
	
	outcat = copy.deepcopy(cat)
	outcat.add_columns([
		astropy.table.Column(name="psfgridx", data=np.zeros(len(cat), dtype=float)),
		astropy.table.Column(name="psfgridy", data=np.zeros(len(cat), dtype=float)),
		astropy.table.Column(name="psfgridn", data=np.zeros(len(cat), dtype=int))
	])
	
	for i in range(len(cat)):
		
		(yind, xind) = divmod(i, gridwidth)
		xmin = xind*stampsize
		xmax = xmin + stampsize
		ymin = yind*stampsize
		ymax = ymin + stampsize
		
		grid[xmin:xmax, ymin:ymax] = stack[i].transpose() / float(counter[i])
		
		xpos = xmin + stampsize/2.0 + 0.5
		ypos = ymin + stampsize/2.0 + 0.5
		outcat[i]["psfgridx"] = xpos
		outcat[i]["psfgridy"] = ypos
		outcat[i]["psfgridn"] = counter[i]
		
		
	megalututils.tofits(grid, os.path.join(workdir, "psfgrid.fits"))
	
	return outcat


