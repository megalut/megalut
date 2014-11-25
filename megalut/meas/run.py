"""
High-level functionality to measure features on several images using multiprocessing.

We have two public functions:

- a onsims() which is specialised in exploring the file structure made by
  megalut.sim.run.multi(), and run on them by calling
- general(), which can be used for any images.

Behind the scenes, the approach taken by general() is the following:

- make a list of _WorkerSetting objects, each of them describing the elementary task of
  measuring shapes on one single image.
- feed this list into _run(), which takes care of running the measurements.
  We use the simple multiprocessing.Pool to distribute the work on several cpus.
  This seems easier than implementing a pool-like queue ourself.

  
"""


import os
import sys
import glob
import datetime
import multiprocessing
import copy

import megalut

from .. import tools

import logging
logger = logging.getLogger(__name__)


def onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=1, skipdone=True):
	"""
	Run the given measfct on sims created by sim.run.multi() for this simdir and simparams.
	This explores the simdir for potential images, and passes them to general().
	
	:param simdir: the simdir that you gave to sim.run.multi()
	:param simparams: the sim.params.Params that you gave to sim.run.multi()
		(Needed to get the simparams.name)
	:param measdir: Path to a directory where the catalogs should be written.
		As for the simdir, you can keep the same measdir for different simparams,
		as the results will be stored in subdirectories using simparams.name.
		But **the measdir should be changed if anything is changed on the measfct**.

	See the doc for general() for the explanation of the other parameters.
	
	As an illustration, the written file structure looks like::
	
		$ ls -1 measdir/name_of_simparams/
		20141017T185236_Cx9D5b_0_galimg_meascat.pkl
		20141017T185236_Cx9D5b_1_galimg_meascat.pkl
		20141017T185236_Cx9D5b_2_galimg_meascat.pkl
		20141017T185236_j8xBv6_0_galimg_meascat.pkl
		20141017T185236_j8xBv6_1_galimg_meascat.pkl
		20141017T185236_j8xBv6_2_galimg_meascat.pkl

	"""

	simworkdir = os.path.join(simdir, simparams.name)
	logger.info("Exploring the contents of simdir '%s'" % (simworkdir))
	
	incatfilepaths = sorted(glob.glob(os.path.join(simworkdir, "*_cat.pkl")))
	
	measworkdir = os.path.join(measdir, simparams.name)
	if not os.path.exists(measworkdir):
		os.makedirs(measworkdir)
	
	# The input lists for general():
	genincatfilepaths = [] # This is not incatfilepaths! The same catalogs will appear multiple times in here.
	genoutcatfilepaths = []
	genincatmetadicts = [] # Indeed we will have to set meta["img"] to point to the different realizations.
	
	
	for incatfilepath in incatfilepaths:
		
		# We read the catalog
		incat = megalut.tools.io.readpickle(incatfilepath)
		
		# And loop over the "declared" realization ImageInfo objects:
		for imgrea in incat.meta["imgreas"]:
			
			# Let's check that the declared image file does exist:
			if not os.path.exists(imgrea.filepath):
				logger.warning("Could not find image realization '%s', will skip it" % (imgrea.filepath))
				continue
			
			# If everything seems ok, we prepare the entries for general for this realization
			outcatfilepath = os.path.join(measdir, simparams.name, imgrea.name + "_meascat.pkl")
			
			# Now the ImageInfo object for meta["img"]. We make a new object, based on the
			# info for this realization, and add a workdir (in case measfct uses it).
			workdir = os.path.join(measdir, simparams.name, imgrea.name + "_workdir")
			imageinfo = tools.imageinfo.ImageInfo(
				imgrea.filepath, imgrea.xname, imgrea.yname, imgrea.stampsize,
				workdir = workdir
				)
			
			genincatfilepaths.append(incatfilepath)
			genoutcatfilepaths.append(outcatfilepath)
			genincatmetadicts.append({"img":imageinfo})
				
	
	# And we pass the ball to general():
	general(genincatfilepaths, genoutcatfilepaths, measfct, measfctkwargs,
		ncpu=ncpu, skipdone=skipdone, incatmetadicts=genincatmetadicts)
	


def general(incatfilepaths, outcatfilepaths, measfct, measfctkwargs, ncpu=1, skipdone=True, incatmetadicts=None):
	"""
	Run the given shape measurement (measfct) on your images using a multiprocessing pool map (ncpu).
	This measfct must be MegaLUT-compliant, i.e. find all the required images by reading the meta of the passed catalog.
	Note that if you want to run on MegaLUT simulations, see the function onsims() above (which calls this function).
	
	
	:param incatfilepaths: list of paths to the pickled input catalogs.
		These catalogs must contain the information required by measfct (and the measfctkwargs)
		to run on the image file(s) specified as ImageInfo objects in the catalog's meta dicts.
		Note that there is a trick to run with **different meta dicts**, see argument incatmetadicts below.
	:param outcatfilepaths: list of paths where the corresponding output catalog pickles should be written.
	:param measfct: The function that measures the sources. It has to be MegaLUT-compliant, i.e., it has to find
		all the required images by reading the meta of the passed catalog.
		Often you will define this funtion yourself, as you might want to run different algorithms in one shot.
	:param measfctkwargs: keyword arguments controlling the behavior of the measfct.
		Usually these stay the same for every catalog/image (then give only one dict), but sometimes you might
		want to explore a range of different settings (then give a list of dicts, as long as incatfilepaths).
	:type measfctkwargs: dict or list of dicts
	:param ncpu: Maximum number of processes that should be used. Default is 1.
		Set to 0 for maximum number of available CPUs.
	:type ncpu: int
	:type skipdone: If set to False, re-run even if the output catalog already exists.
	:param incatmetadicts: If specified, these dicts will update the meta of the incats (for example
		the meta["img"] ...)
		This trick is very useful when running over several images of the same incat. Using this trick,
		you don't have to prepare and write to disk one copy of incat for every image.
	:type incatmetadicts: list of dicts


	.. warning:: If called "in parallel" (e.g., from several python scripts launched at about the same time),
		(in the worst case) all the work in every script might be run, i.e., skipdone will not work.
		Not a safety issue (hence currently no fix for this).  We can see if we want a fix for that.
		(can be done e.g. with temporary files written/detected and deleted by the workers)

	"""
	
	# Some trivial tests:
	
	n = len(incatfilepaths)
	if len(outcatfilepaths) != n:
		raise RuntimeError("The input/output catalog lists must have the same length")
	if incatmetadicts is not None:
		if len(incatmetadicts) != n:
			raise RuntimeError("The list incatmetadicts does not have the same length as incatfilepaths")
	else: # We turn this None into a list of None:
		incatmetadicts = [None] * n
		
		
	# If measfctkwargs is a simple dict, we make a list of identical dicts.
	
	if type(measfctkwargs) is dict:
		measfctkwargslist = [copy.deepcopy(measfctkwargs) for i in range(n)]
	else:
		measfctkwargslist = measfctkwargs
		if len(measfctkwargs) != n:
			raise RuntimeError("Your list of measfctkwargs does not have the same length as incatfilepaths")
			
	# It could be that the measfct wants to use the workdir of each image, if such workdirs are set.
	# In this case, it would be nice to test if all the workdirs are different (as they probably should).
	# A priori it seems not necessery to enforce this, but it's a simple way to avoid race conditions
	# at directory creation, or any unwanted file overwriting.
	# However, for this we would have to open the incats from the main process, this seems weird.
	# And so we skip this test.
	
	# Now we prepare the parallel processing.
	wslist = [] # The list to be filled with workersettings
	
	for (incatfilepath, outcatfilepath, measfctkwargsdict, incatmetadict) in zip(incatfilepaths, outcatfilepaths, measfctkwargslist, incatmetadicts):
			
		if skipdone and os.path.exists(outcatfilepath):
			logger.info("Output catalog %s already exists, skipping this one..." % (outcatfilepath))	
			continue
						
		ws = _WorkerSettings(incatfilepath, outcatfilepath, measfct, measfctkwargsdict, incatmetadict)
		wslist.append(ws)
	
	logger.info("Ready to run measurents on %i images." % (len(wslist)))
			
	# And we run a pool of workers on this wslist.
	_run(wslist, ncpu)
		



class _WorkerSettings():
	"""
	A class that holds together all the settings for measuring an image.
	"""
	
	def __init__(self, incatfilepath, outcatfilepath, measfct, measfctkwargs, incatmetadict):
		
		self.incatfilepath = incatfilepath
		self.outcatfilepath = outcatfilepath
		self.measfct = measfct
		self.measfctkwargs = measfctkwargs
		self.incatmetadict = incatmetadict
	
	def __str__(self):
		return "%s" % (os.path.basename(self.incatfilepath))



def _worker(ws):
	"""
	Worker function that the different processes will execute, processing the
	_WorkerSettings objects.
	"""
	starttime = datetime.datetime.now()
	p = multiprocessing.current_process()
	logger.info("%s is starting to measure catalog %s with PID %s" % (p.name, str(ws), p.pid))
	logger.debug("%s uses measfctkwargs %s" % (p.name, str(ws.measfctkwargs)))
	
	# Read input catalog
	incat = megalut.tools.io.readpickle(ws.incatfilepath)
	if ws.incatmetadict is not None:
		logger.debug("%s updates the catalog meta dict with %s" % (p.name, str(ws.incatmetadict)))
		incat.meta.update(ws.incatmetadict)
	
	
	# Run measfct, it will read the image by itself:
	logger.debug("%s will now run on image %s" % (p.name, incat.meta["img"].name))
	outcat = ws.measfct(incat, **ws.measfctkwargs)
	
	# Write output catalog
	megalut.tools.io.writepickle(outcat, ws.outcatfilepath)

	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))


def _run(wslist, ncpu):
	"""
	Wrapper around multiprocessing.Pool with some verbosity.
	"""
	
	if len(wslist) == 0: # This test is useful, as pool.map otherwise starts and is a pain to kill.
		logger.info("No images to measure.")
		return

	# We do not want to see the log from the low-level stuff:
	mutemodules = ["megalut.meas.galsim_adamom", "megalut.meas.sewfunc",
			"sewpy.sewpy", "megalut.tools.io", "megalut.tools.image"]
	for modulename in mutemodules:
		lowlevellogger = logging.getLogger(modulename)
		#lowlevellogger.propagate = False
		lowlevellogger.setLevel(logging.WARNING)


	if ncpu == 0:
		try:
			ncpu = multiprocessing.cpu_count()
		except:
			logger.warning("multiprocessing.cpu_count() is not implemented!")
			ncpu = 1
	
	starttime = datetime.datetime.now()
	
	logger.info("Starting the measurement on %i images using %i CPUs" % (len(wslist), ncpu))
	
	# The single process way (MUCH MUCH EASIER TO DEBUG...)
	#map(_worker, wslist)
	
	# The multiprocessing way:
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()
	
	endtime = datetime.datetime.now()
	logger.info("Done, the total measurement time was %s" % (str(endtime - starttime)))
	
	# We unmute the mutemodules:
	#for modulename in mutemodules:
	#	lowlevellogger = logging.getLogger(modulename)
	#	lowlevellogger.propagate = True



