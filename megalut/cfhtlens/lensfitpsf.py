"""
Code related to the PSF interpolation performed by lensfit on CFHTLenS and cie. 

"""

import os
import subprocess
import shutil

import logging
logger = logging.getLogger(__name__)



def writecat(cat, filepath):
	"""
	Dedicated function to write the plain input catalog required for createPSFcube
	"""
	
	f = open(filepath, "w")
	for row in cat:
		f.write("%.8f %.8f\n" % (row["ALPHA_J2000"], row["DELTA_J2000"]))
	f.close()
	logger.info("Wrote %i entries into %s" % (len(cat), filepath))

	


def makepsfs(cat, pointing, workdir="."):
	"""
	
	Runs createPSFcube for every source in cat and on every exposure of that pointing.
	
	createPSFcube only works if its argument is just the basename of the explist (not the full path)
	(what the hell ???)
	So we have to copy that file and chdir.
	
	"""
	
	exps = pointing.explists()
	logger.info("I will work on %i exposures: %s" % (len(exps), ", ".join(exps)))

	
	if not os.path.isdir(workdir):
		os.mkdir(workdir)
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


def coaddpsfs(workdir):
	"""
	
	
	"""
	pass
	




