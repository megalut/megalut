"""
High-level functions to create a whole set of simulations.

These functions write their results to disk, and therefore **define a directory and
filename structure**, containing the different realizations, catalogs, etc.
This is very different from the lower-level functions such as those in stampgrid,
which do not relate to any directory and filename structure.
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

import logging
logger = logging.getLogger(__name__)


def multi(simdir, simparams, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=1):
	"""
	I use stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	
	I support multiprocessing (ncpu), and furthermore I **add** my simulations to any
	existing set generated previously (instead of overwriting).
	To do so,  I take care of generating unique filenames (avoiding "race hazard") using ``tempfile``.
	So you could perfectly have **multiple processes running this function in parallel**, writing
	simulations using the same simparams in the same directory. Note that I also put a timestamp
	in my filenames, but this is just to help humans. I don't rely on it for uniqueness.
	
	:param simdir: Path to a directory where I should write the simulations.
		This directory has **not** to be unique for every call of this function!
		I will make subdirectories reflecting the name of your simparams inside.
		If this directory already exists, even for the same simparams,
		I will **add** my simulations to it, instead of overwriting anything.
	:param simparams: a sim.simparams instance that defines the distributions of parameters
	:param drawcatkwargs: Keyword arguments which I will directly pass to stampgrid.drawcat
	:type drawcatkwargs: dict
	:param drawimgkwargs: Idem for stampgrid.drawimg. However I will not respect filenames that
		you set, as I will use my own ones. If you specify anything but None as path for the
		simtrugalimgfilepath or the simpsfimgfilepath, I will save these, using my own filenames.
		Otherwise the true galaxy images and the PSF stamp images are not saved.
	:type drawimgkwargs: dict
	:param ncat: The number of catalogs I should draw
	:type ncat: int
	:param nrea: The number of realizations per catalog I should draw.
	:type nrea: int
	:param ncpu: Maximum number of processes I should use. Default is 1.
		Set to 0 if I should count them myself.
	:type ncpu: int
	
	
	As an illustration, an example of the directory structure I produce (ncat=2, nrea=2)::
	
		% ls -1 simdir/name_of_simparams/*
		
		simdir/name_of_simparams/20141016T170441_1ZBNwd_cat.pkl
		simdir/name_of_simparams/20141016T170441_BJjhps_cat.pkl

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
	realization image. This is intended, so that you can collect things that are based on
	realization image filenames made from a single name_of_simparams into one directory.
	And also it just makes things safer.
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
		logger.info("I'm adding new simulations to the existing set '%s'" % (simparams.name))

	logger.info("I will draw %i catalogs, and %i image realizations per catalog" % (ncat, nrea))

	# We create the catalogs, there is probably no need to parallelize this: 
	catalogs = [stampgrid.drawcat(simparams, **drawcatkwargs) for i in range(ncat)]

	# Now we save them usign single filenames.
	# This is not done with a timestamp ! The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	prefix = datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
		catalog.meta["catname"] = os.path.basename(str(catfile.name))[:-8] # Removing the suffix "_cat.pkl"
		catalog.meta["simparamsname"] = simparams.name
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog '%s'" % catalog.meta["catname"])
		
		# While in this simple loop over catalogs, we also make the dir that will contain the images.
		# Indeed the worker loop iterates over this same dir for every realization.
		
		os.mkdir(os.path.join(workdir, catalog.meta["catname"] + "_img"))
	
	
	print "Write all settings to a log file !"
	
	# And now we draw the image realizations for those catalogs.
	# This is done with multiprocessing.
	# We make a multiprocessing loop over all combinations of catalogs and realizations,
	# as we want this to be efficient for both (1 cat, 20 rea), and (20 cat, 1 rea)
	# For this, we prepare a flat list of _WorkerSettings objects for all (cat, rea) combinations,
	# and run a pool of _worker functions on this list.
	
	catindexes = range(ncat)
	reaindexes = range(nrea)
	wslist = [_WorkerSettings(catalogs[catindex], reaindex, drawimgkwargs, workdir) for catindex in catindexes for reaindex in reaindexes]
	assert len(wslist) == ncat * nrea
	
	
	# The catalogs could be heavy, but note that we do not put unique copies of the catalogs in this list !
	# Still, it would seem better to just have the catindex in this tuple.
	# However it seems that accessing shared memory from a multiprocessing.Pool is not trivial.
	# So until we need something better, we leave it like this.

	if ncpu == 0:
		try:
			ncpu = multiprocessing.cpu_count()
		except:
			logger.warning("multiprocessing.cpu_count() is not implemented !")
			ncpu = 1
			
	logger.info("I now start drawing %i images using %i CPUs" % (len(wslist), ncpu))
	
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
		the catalog's catname, reaindex, and workdir define the filepaths in which the image(s)
		drawn with the drawimgkwargs will be written.
		"""
		
		self.catalog = catalog # No copy needed, we won't change it!
		self.reaindex = reaindex
		self.drawimgkwargs = copy.deepcopy(drawimgkwargs) # A copy, as we will change this.
		self.workdir = workdir # Stays the same for all workers !
	
		# And some setup work:
		self.catname = self.catalog.meta["catname"]
		self.catimgdirpath = os.path.join(workdir, self.catname + "_img") # Where I write my images
		assert os.path.exists(self.catimgdirpath) == True # Indeed this should always be the case.
		
		# And we prepare the filepaths in which we will write the image(s)
		# For this we simply overwrite any specified image filepath in the drawimgkwargs:
		self.drawimgkwargs["simgalimgfilepath"] =\
			os.path.join(self.catimgdirpath, "%s_%i_galimg.fits" % (self.catname, self.reaindex))
		
		# If the user asked for a trugalimg and a psfimg, we also overwrite these filepaths:
		if self.drawimgkwargs.get("simtrugalimgfilepath", None) is not None:
			self.drawimgkwargs["simtrugalimgfilepath"] = os.path.join(self.catimgdirpath, "%s_%i_trugalimg.fits" % (self.catname, self.reaindex))
		if self.drawimgkwargs.get("simpsfimgfilepath", None) is not None:
			self.drawimgkwargs["simpsfimgfilepath"] = os.path.join(self.catimgdirpath, "%s_%i_psfimg.fits" % (self.catname, self.reaindex))
	
	
	def __str__(self):
		"""
		A short string describing these settings
		"""
		return "[catalog '%s', realization %i]" % (self.catname, self.reaindex)
	
	
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
