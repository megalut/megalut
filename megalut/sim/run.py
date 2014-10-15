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


def multi(params, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=1, simdir="sim"):
	"""
	
	I use stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	
	I support multiprocessing (ncpu), and furthermore I add my simulations to any
	existing set generated previously.
	To do so,  I take care of generating unique filenames (avoiding "race hazard") using ``tempfile``.
	So you could perfectly have multiple processes running this function in parallel, writing
	simulations using the same params in the same directory. Note that I also put a timestamp
	in my filenames, but this is just to help humans. I don't rely on it for uniqueness.
	

	:param params: a sim.Params instance that defines the distributions of parameters
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
	:param simdir: Path to a directory where I should write the simulations.
		This directory has **not** to be unique for every call of this function!
		I will make subdirectories reflecting the name of your params inside.
		If this directory already exists, even for the same params,
		I will **add** my simulations to it, instead of overwriting anything.
	
	As an illustration, an example of the directory structure I produce (ncat=2, nrea = 2)::
	
		% ls -1 simdir/name_of_params/*
				
		simdir/name_of_params/20141015T144705_QBHeS2_cat.pkl
		simdir/name_of_params/20141015T144705_Yppgi__cat.pkl
		
		simdir/name_of_params/20141015T144705_QBHeS2_img:
		0_galimg.fits
		0_trugalimg.fits
		1_galimg.fits
		1_trugalimg.fits
		
		simdir/name_of_params/20141015T144705_Yppgi__img:
		0_galimg.fits
		0_trugalimg.fits
		1_galimg.fits
		1_trugalimg.fits

	
	
	"""
	
	# I suppress the info logging from the lower level functions:
	stampgridlogger = logging.getLogger("megalut.sim.stampgrid")
	stampgridlogger.setLevel(logging.WARNING)

	
	starttime = datetime.datetime.now()
	workdir = os.path.join(simdir, params.name)
	if not os.path.exists(workdir):
		os.makedirs(workdir)
		logger.info("Creating a new set of simulations named '%s'" % (params.name))
	else:
		logger.info("I'm adding new simulations to the existing set '%s'" % (params.name))

	logger.info("I will draw %i catalogs, and %i image realizations per catalog" % (ncat, nrea))

	# We create the catalogs, there is probably no need to parallelize this: 
	catalogs = [stampgrid.drawcat(params, **drawcatkwargs) for i in range(ncat)]

	# Now we save them usign single filenames.
	# This is not done with a timestamp ! The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	prefix = datetime.datetime.now().strftime("%Y%m%dT%H%M%S_")
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix="_cat.pkl", dir=workdir, delete=False)
		catalog.meta["catfilename"] = str(catfile.name)
		catalog.meta["imgdirname"] = str(catfile.name)[:-8] + "_img"
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog into '%s'" % catalog.meta["catfilename"])
		os.mkdir(os.path.join(workdir, catalog.meta["imgdirname"]))
		
	
	# And now we draw the image realizations for those catalogs.
	# This is done with multiprocessing.
	# We have to make a multiprocessing loop over both catalogs and realizations,
	# as we want this to be efficient for both (1 cat, 20 rea), and (20 cat, 1 rea)
	
	catindexes = range(ncat)
	reaindexes = range(nrea)
	catreatuples = [(catalogs[catindex], reaindex, drawimgkwargs) for catindex in catindexes for reaindex in reaindexes]
	# This is not that great, as the catalogs could be heavy.
	# It would be better to just have the catindex in this tuple.

	assert len(catreatuples) == ncat * nrea
	
	if ncpu == 0:
		try:
			ncpu = multiprocessing.cpu_count()
		except:
			logger.warning("multiprocessing.cpu_count() is not implemented !")
			ncpu = 1
			
	logger.info("I now start drawing %i images using %i CPUs" % (len(catreatuples), ncpu))
	
	# The single-processing version would be:
	#map(drawcatrea, catreatuples)

	# The simple multiprocessing map is:
	
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_drawcatrea, catreatuples)
	pool.close()
	pool.join()
	
	endtime = datetime.datetime.now()
	logger.info("Done in %s" % (str(endtime - starttime)))

	
	
def _drawcatrea(catreatuple):
	"""
	Worker function that the processes will execute.
	"""		
	cat = catreatuple[0]#catalogs[catreatuple[0]]
	reaindex = catreatuple[1]
	drawimgkwargs = catreatuple[2]
	
	# We simply overwrite any conflicting settings in drawimgkwargs:
	drawimgkwargs["simgalimgfilepath"] =\
		os.path.join(cat.meta["imgdirname"], "%i_galimg.fits" % (reaindex))	
	if drawimgkwargs.get("simtrugalimgfilepath", None) is not None:
		drawimgkwargs["simtrugalimgfilepath"] = os.path.join(cat.meta["imgdirname"], "%i_trugalimg.fits" % (reaindex))
	if drawimgkwargs.get("simpsfimgfilepath", None) is not None:
		drawimgkwargs["simpsfimgfilepath"] = os.path.join(cat.meta["imgdirname"], "%i_psfimg.fits" % (reaindex))
	
	p = multiprocessing.current_process()
	logger.info("%s is starting to draw with PID %s" % (p.name, p.pid))
	stampgrid.drawimg(galcat = cat, **drawimgkwargs)
	logger.info("%s is done." % (p.name))
