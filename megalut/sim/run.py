"""
High-level functions to create a whole set of simulations.

These functions write their results to disk, and therefore **define a directory and
filename structure**, containing the different realizations, catalogs, etc.
This is very different from the lower-level functions such as those in stampgrid,
which do not specify any directory or filename structure.
"""

import os
import sys
import glob
import datetime
import tempfile
import cPickle as pickle
import copy
import multiprocessing

import stampgrid
import inspect

import logging
logger = logging.getLogger(__name__)


def multi(simdir, simparams, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=1, savetrugalimg=False, savepsfimg=False):
	"""
	Uses stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	
	Supports multiprocessing (ncpu), and furthermore **generates additional simulations ** to any
	existing image set previously generated (instead of overwriting).
	To do so, unique filenames are generated (avoiding "race hazard") using ``tempfile``.
	So one could have **multiple processes running this function in parallel**, writing
	simulations using the same simparams in the same directory. Note that a timestamp is included
	in the filenames, but this is just to help human readability, not for uniqueness.

	:param simdir: Path to a directory where the simulations are written to.
		This directory does **not** have to be unique for every call of this function!
		Subdirectories reflecting the name of each simparams are made under the simdir.
		If the simparams directory already exists, simulations will be
		**added** to it, instead of overwriting any existing file.
	:param simparams: A sim.simparams instance that defines the distributions of parameters
	:param drawcatkwargs: Keyword arguments which will be directly passed to stampgrid.drawcat
	:type drawcatkwargs: dict
	:param drawimgkwargs: Idem for stampgrid.drawimg.  However any specified filenames will be
		ignored (the filenames will be automatically generated).  If anything but None
		is specified as path for the simtrugalimgfilepath or the simpsfimgfilepath, the
		files will be saved with the auto-generated filenames (otherwise the true galaxy
		images and the PSF stamp images are not saved).
	:type drawimgkwargs: dict
	:param ncat: The number of catalogs to be generated.
	:type ncat: int
	:param nrea: The number of realizations per catalog to be generated.
	:type nrea: int
	:param ncpu: Maximum number of processes to be used. Default is 1.
		Set to 0 for maximum number of available CPUs.
	:type ncpu: int
	:param savetrugalimg: if True, I will also save the true (unconvolved) galaxy images.
	:param savepsfimg: if True, I will also save the PSF stamps.
	
	
	As an illustration, an example of the directory structure I produce (ncat=2, nrea=2)::
	
		% ls -1 simdir/name_of_simparams/*
		
		simdir/name_of_simparams/20141016T170441_1ZBNwd_cat.pkl
		simdir/name_of_simparams/20141016T170441_BJjhps_cat.pkl

		simdir/name_of_simparams/20141016T170441_log.txt

		simdir/name_of_simparams/20141016T170441_1ZBNwd_img:
		20141016T170441_1ZBNwd_0_galimg.fits
		20141016T170441_1ZBNwd_0_trugalimg.fits
		20141016T170441_1ZBNwd_1_galimg.fits
		20141016T170441_1ZBNwd_1_trugalimg.fits

		simdir/name_of_simparams/20141016T170441_BJjhps_img:
		20141016T170441_BJjhps_0_galimg.fits
		20141016T170441_BJjhps_0_trugalimg.fits
		20141016T170441_BJjhps_1_galimg.fits
		20141016T170441_BJjhps_1_trugalimg.fits

	
	For a single call to this function, the timestamp is the same for all catalogs. This is
	handy if you want to delete all files from a particular call.
	
	Note that the unique filename of a catalog is repeated in the filename of every single
	realization image.  This is intended, so that you can collect things that are based on
	realization image filenames made from a single name_of_simparams into one directory.
	It also makes things safer.
	"""
	
	if ncat < 1 or nrea < 1:
		raise RuntimeError("ncat and nrea must be above 0")
	
	# I suppress the info-or-lower-level logging from the low-level functions:
	stampgridlogger = logging.getLogger("megalut.sim.stampgrid")
	stampgridlogger.setLevel(logging.WARNING)

	
	starttime = datetime.datetime.now()
	workdir = os.path.join(simdir, simparams.name)
	if not os.path.exists(workdir):
		os.makedirs(workdir)
		logger.info("Creating a new set of simulations named '%s'" % (simparams.name))
	else:
		logger.info("Adding new simulations to the existing set '%s'" % (simparams.name))

	logger.info("Drawing %i catalogs, and %i image realizations per catalog" % (ncat, nrea))
	logger.info("All files written into '%s'" % (workdir))
	

	# We create the catalogs, there is probably no need to parallelize this: 
	catalogs = [stampgrid.drawcat(simparams, **drawcatkwargs) for i in range(ncat)]

	# Now we save them using single filenames.
	# This is not done with a timestamp!  The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	prefix = datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
		catalog.meta["catname"] = os.path.basename(str(catfile.name)).replace("_cat.pkl","")
		catalog.meta["simparamsname"] = simparams.name
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog '%s'" % catalog.meta["catname"])
	
	
	# The catalogs are drawn, we save a log file about this
	logger.debug("Now writing logfile...")
	logfilepath = os.path.join(workdir, prefix + "log.txt")
	logfile = open(logfilepath, "w")
	logfile.write("Logfile of megalut.sim.run.multi, written to %s\n\n" % (logfilepath))
	logfile.write(str(simparams) + "\n")
	logfile.write("drawcatkwargs: " + repr(drawcatkwargs) + "\n")
	logfile.write("drawimgkwargs: " + repr(drawimgkwargs) + "\n")
	# I did not manage to save the code of simparams, here is my attempt:
	#logfile.write("\n")
	#logfile.write(str(simparams) + ":\n")
	#logfile.write(inspect.getsourcelines(type(simparams)))
	logfile.close()
	logger.debug("Done with writing logfile")
	
	# Before drawing the images, some warnings
	
	if "simgalimgfilepath" in drawimgkwargs:
		logger.warning("You specified a simgalimgfilepath in your drawimgkwargs, but I will not respect it")
		drawimgkwargs.pop("simgalimgfilepath")
	if "simtrugalimgfilepath" in drawimgkwargs:
		logger.warning("You specified a simtrugalimgfilepath in your drawimgkwargs, but I will not respect it")
		drawimgkwargs.pop("simtrugalimgfilepath")
	if "simpsfimgfilepath" in drawimgkwargs:
		logger.warning("You specified a simpsfimgfilepath in your drawimgkwargs, but I will not respect it")
		drawimgkwargs.pop("simpsfimgfilepath")
		
	# And now we draw the image realizations for those catalogs.
	# This is done with multiprocessing.
	# We make a multiprocessing loop over all combinations of catalogs and realizations,
	# as we want this to be efficient for both (1 cat, 20 rea), and (20 cat, 1 rea)
	# For this, we prepare a flat list of _WorkerSettings objects for all (cat, rea) combinations,
	# and run a pool of _worker functions on this list.
	
	wslist = []
	for catalog in catalogs:	
		for reaindex in range(nrea):
			
			# We have to customize the drawimgkwargs, and so we work on a copy
			thisdrawimgkwargs = copy.deepcopy(drawimgkwargs)
			
			# Preparing the filepaths in which we will write the image(s)
			# Note that we removed all these keys from the the drawimgkwargs before!
			
			catname = catalog.meta["catname"]
			catimgdirpath = os.path.join(workdir, catname + "_img")
				
			thisdrawimgkwargs["simgalimgfilepath"] =\
				os.path.join(catimgdirpath, "%s_%i_galimg.fits" % (catname, reaindex))
		
			# If the user asked for a trugalimg and a psfimg, we also prepare these filepaths.
			if savetrugalimg:
				thisdrawimgkwargs["simtrugalimgfilepath"] = os.path.join(catimgdirpath, "%s_%i_trugalimg.fits" % (catname, reaindex))
			if savepsfimg:
				thisdrawimgkwargs["simpsfimgfilepath"] = os.path.join(catimgdirpath, "%s_%i_psfimg.fits" % (catname, reaindex))
	
			ws = _WorkerSettings(catalog, reaindex, thisdrawimgkwargs, workdir)
			
			wslist.append(ws)
		
		# While in this simple loop over catalogs, we also make the dir that will contain the images.
		# Indeed the worker loop iterates over this same dir for every realization.
		
		os.mkdir(os.path.join(workdir, catalog.meta["catname"] + "_img"))
	
				
	assert len(wslist) == ncat * nrea
	
	# The catalogs could be heavy, but note that we do not put unique copies of the catalogs in this list !
	# Still, it would seem better to just have small thinks like "indexes" in the settings.
	# However it seems that accessing shared memory from a multiprocessing.Pool is not trivial.
	# So until we need something better, we leave it like this.
	# Note for the future: instead of thinking about how to share memory to optimize this, the workers could well
	# read their data from disk, and stay embarassingly parallel. 

	if ncpu == 0:
		try:
			ncpu = multiprocessing.cpu_count()
		except:
			logger.warning("multiprocessing.cpu_count() is not implemented!")
			ncpu = 1
			
	logger.info("Start drawing %i images using %i CPUs" % (len(wslist), ncpu))
	
	# The single-processing version would be:
	#map(_worker, wslist)

	# The simple multiprocessing map is:
	
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()
	
	endtime = datetime.datetime.now()
	nstamps = len(catalogs[0])*nrea
	logger.info("Done, the total time for drawing %i stamps was %s" % (nstamps, str(endtime - starttime)))
	logger.info("That's %.3f ms per stamp (with ncpu = %i)." % (1e3*(endtime - starttime).total_seconds()/nstamps, ncpu))


class _WorkerSettings():
	"""
	A class to hold together all the settings for processing a catalog-realization combination.
	If one day we have different drawimg() functions, we'll just pass this function here as well.
	"""
	
	def __init__(self, catalog, reaindex, drawimgkwargs, workdir):
		"""
		The catalog's catname, reaindex, and workdir define the filepaths in which the image(s)
		drawn with the drawimgkwargs will be written.
		"""
		
		self.catalog = catalog # No copy needed, we won't change it!
		self.reaindex = reaindex
		self.drawimgkwargs = copy.deepcopy(drawimgkwargs) # A copy, as we will change this.
		self.workdir = workdir # Stays the same for all workers !
	
		# And some setup work:
		#self.catname = self.catalog.meta["catname"]
		#self.catimgdirpath = os.path.join(workdir, self.catname + "_img") # Where I write my images
		#assert os.path.exists(self.catimgdirpath) == True # Indeed this should always be the case.
		
	def __str__(self):
		"""
		A short string describing these settings
		"""
		return "[catalog '%s', realization %i]" % (self.catalog.meta["catname"], self.reaindex)
	
	
def _worker(ws):
	"""
	Worker function that processes one _WorkerSettings object.
	"""		
	starttime = datetime.datetime.now()
	p = multiprocessing.current_process()
	logger.info("%s is starting to draw %s with PID %s" % (p.name, str(ws), p.pid))
	
	# It's just a single call:
	stampgrid.drawimg(galcat = ws.catalog, **ws.drawimgkwargs)
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))
