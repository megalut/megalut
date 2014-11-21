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
import numpy as np
import copy
import shutil
import multiprocessing

import stampgrid
import inspect

import logging
logger = logging.getLogger(__name__)


def multi(simdir, simparams, drawcatkwargs, drawimgkwargs=None,
	psfcat=None, psfimgpath=None, psfstampsize=None, psfxname="psfx", psfyname="psfy", psfselect="random",
	ncat=2, nrea=2, ncpu=1, savetrugalimg=False, savepsfimg=False):
	"""
	Uses stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	
	Supports multiprocessing (ncpu), and furthermore **generates additional simulations ** to any
	existing image set previously generated (instead of overwriting).
	To do so, unique filenames are generated (avoiding "race hazard") using ``tempfile``.
	So one could have **multiple processes running this function in parallel**, writing
	simulations using the same simparams in the same directory. Note that a timestamp is included
	in the filenames, but this is just to help human readability, not for uniqueness.
	
	About specifying the PSFs: this function takes a single psfimg and a corresponding psfcat. This psfcat does **not**
	need to have exactly "n x n" rows (one for each galaxy in each catalog).
	Instead, for each of the n x n galaxy stamps in the ncat catalogs, a PSF from this psfcat will be assigned
	either randomly (psfchoice = "random") or in sequence (psfchoice = "sequential").
	In any case, the information about which PSF is used will be stored in the output catalog.
	This function also makes a FITS copy of psfimg into its "simdir", to be sure that this information is kept
	in a consistent way.
	

	:param simdir: Path to a directory where the simulations are written to.
		This directory does **not** have to be unique for every call of this function!
		Subdirectories reflecting the name of each simparams are made under the simdir.
		If the simparams directory already exists, simulations will be
		**added** to it, instead of overwriting any existing file.
	:param simparams: A sim.simparams instance that defines the distributions of parameters
	:param drawcatkwargs: Keyword arguments which will be directly passed to stampgrid.drawcat
	:type drawcatkwargs: dict
	:param drawimgkwargs: Idem, for stampgrid.drawimg. However note that currently **any entries
		to this dict will be ignored**, as they have to be set internaly by the present function!
		The filepaths simgalimgfilepath, simtrugalimgfilepath simpsfimgfilepath will be saved
		with auto-generated filenames, if asked for.
	:type drawimgkwargs: dict
	:param psfcat: astropy table (or path to a pkl) with pixel coordinates of PSFs to use.
		If None, no PSF information will be passed to stampgrid.drawimg, and you won't have
		to specify any of the other psf-related arguments.
	:param psfimgpath: path to a FITS image with the PSFs.
	:param psfstampsize: size of PSF stamps to extract (in pixels)
	:type psfstampsize: int
	:param psfxname: column name of psfcat containing the x position of the PSF to use
	:param psfyname: idem for y
	:param psfselect: either "random" or "sequential"
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
		
		simdir/name_of_simparams/20141016T170441_kj34jj_psfimg.fits   <-- PSF image is copied!
		
		simdir/name_of_simparams/20141016T170441_1ZBNwd_cat.pkl  <-- the catalogs
		simdir/name_of_simparams/20141016T170441_BJjhps_cat.pkl  <-- (ncat different ones)

		simdir/name_of_simparams/20141016T170441_1ZBNwd_img:     <-- for each cat...
		20141016T170441_1ZBNwd_0_galimg.fits                     <-- ... the images 
		20141016T170441_1ZBNwd_0_trugalimg.fits
		20141016T170441_1ZBNwd_1_galimg.fits                     <-- (nrea different ones)
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
	starttime = datetime.datetime.now()
	prefix = starttime.strftime("%Y%m%dT%H%M%S_")
	
	# First, some general checks:
	if ncat < 1 or nrea < 1:
		raise RuntimeError("ncat and nrea must be above 0")
	if drawimgkwargs is None:
		drawimgkwargs = {}
	
	# Preparing a workdir
	workdir = os.path.join(simdir, simparams.name)
	if not os.path.exists(workdir):
		os.makedirs(workdir)
		logger.info("Creating a new set of simulations named '%s'" % (simparams.name))
	else:
		logger.info("Adding new simulations to the existing set '%s'" % (simparams.name))

	logger.info("Drawing %i catalogs, and %i image realizations per catalog" % (ncat, nrea))
	logger.info("All files will be written into '%s', with prefix '%s'" % (workdir, prefix))

	# We check that the PSF stuff looks fine:
	if psfcat is not None:
		if type(psfcat) is str:
			psfcat = megalut.tools.io.readpickle(psfcat)
			logger.debug("Your psfcat was a path, I loaded it" % (psfcat))
		if psfxname not in psfcat.colnames or psfyname not in psfcat.colnames:
			raise RuntimeError("PSF coordinates (%s, %s) are not available in the psfcat" % (psfxname, psfyname))
		if psfimgpath is None:
			raise RuntimeError("You gave me a psfcat but no psfimgpath")
		if psfstampsize is None:
			raise RuntimeError("Please specify the psfstampsize argument")
		if type(psfimgpath) is not str:
			raise RuntimeError("The psfimgpath should be a filepath (string)")
	
	# We create the catalogs, this is fast and there is no need to parallelize this: 
	logger.info("Drawing galaxy catalogs...")
	catalogs = [stampgrid.drawcat(simparams, **drawcatkwargs) for i in range(ncat)]
	
	# We now attribute PSFs to each source in these catalogs
	
	if psfcat is not None:

		logger.info("Attributing PSFs using psfselect='%s'" % (psfselect))
	
		for catalog in catalogs:
			if psfselect == "random":
				# We repeat the random drawing for each catalog:
				matched_psfcat = psfcat[np.random.randint(low=0, high=len(psfcat)-1, size=len(catalog))]
				# This creates a copy, which is important !
				
			elif psfselect == "sequential":
				raise RuntimeError("Not yet implemented")
				
			else:
				raise RuntimeError("Unknown psfselect")	

			# And we copy the columns
			catalog["psfx"] = matched_psfcat[psfxname]
			catalog["psfy"] = matched_psfcat[psfyname]
		
		# We copy the PSF image into the workdir.
		# We want this to be perfectly collision-free -- just using the timestamp prefix is *not* enough,
		# as several instances of this multi() could be launched at the same time.
		# So we use tempfile to build a filename for this PSF image.
	
		drawpsfimgfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_psfimg.fits", dir=workdir, delete=False)
		drawpsfimgfilename = drawpsfimgfile.name # Will be written in the meta of each catalog
		drawpsfimgfile.close()	
		logger.info("Copying PSF image into the simdir, with filename '%s'..." % (drawpsfimgfilename))
		shutil.copy(psfimgpath, os.path.join(workdir, drawpsfimgfilename))

	
	# Now we save the catalogs, using unique filenames.
	# This is not done with the timestamp!  The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
		catalog.meta["catname"] = os.path.basename(str(catfile.name)).replace("_cat.pkl","")
		catalog.meta["simparamsname"] = simparams.name	
		if psfcat is not None:
			catalog.meta["drawpsfimgfilename"] = drawpsfimgfilename
			catalog.meta["psfstampsize"] = psfstampsize
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog '%s'" % catalog.meta["catname"])
			
	# Before drawing the images, some warnings about kwargs:
	forbiddendrawimgkwargs = ["simgalimgfilepath", "simtrugalimgfilepath", "simpsfimgfilepath", "psfimg", "psfxname", "psfyname"]
	for kwarg in forbiddendrawimgkwargs:
		if kwarg in drawimgkwargs:
			raise RuntimeError("I can't respect your drawimgkwarg '%s', do not specify it." % (kwarg))
			# Better *not* modify the drawimgkwargs as was done below (side effect !)
			#logger.warning("I will not respect your drawimgkwarg '%s'" % (kwarg))
			#drawimgkwargs.pop(kwarg)
	
	# And now we draw the image realizations for those catalogs.
	# This is done with multiprocessing.
	# We make a multiprocessing pool map over all combinations of catalogs and realizations,
	# as we want this to be efficient for both (1 cat, 20 rea), and (20 cat, 1 rea)
	# For this, we prepare a flat list of _WorkerSettings objects for all (cat, rea) combinations,
	# and run a pool of _worker functions on this list.
	
	wslist = []
	for catalog in catalogs:	
		for reaindex in range(nrea):
			
			# We have to customize the drawimgkwargs, and so we work on a copy
			thisdrawimgkwargs = copy.deepcopy(drawimgkwargs)
			
			# Pointing to the PSF image:
			if psfcat is not None:
				thisdrawimgkwargs["psfimg"] = os.path.join(workdir, drawpsfimgfilename) 
			
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

	# I suppress the info-or-lower-level logging from the low-level functions:
	stampgridlogger = logging.getLogger("megalut.sim.stampgrid")
	stampgridlogger.setLevel(logging.WARNING)
	
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
	# The current logfile is not that useful. Rethink it if needed.
	"""
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
	"""


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
		self.drawimgkwargs = drawimgkwargs # This is already a changed deep copy from the original argument to multi().
		self.workdir = workdir # Stays the same for all workers !
	
		
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
	stampgrid.drawimg(ws.catalog, **ws.drawimgkwargs)
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))
