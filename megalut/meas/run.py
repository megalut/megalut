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

import megalut

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
	
	As an illustration, the file structure looks like::
	
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
	
	
	# Building the input for general():
	genimgfilepaths = []
	genincatfilepaths = [] # This is not incatfilepaths! Catalogs will appear multiple times in here.
	genimgnames = []
	
	for incatfilepath in incatfilepaths:
		catname = os.path.basename(incatfilepath).replace("_cat.pkl","")
		imgdir = os.path.join(simworkdir, catname + "_img")
		if not os.path.exists(imgdir):
			logger.warning("Could not find the image directory for '%s' (skipping this one)" % (inputcat))
			continue
			
		imgfilepaths = sorted(glob.glob(os.path.join(imgdir, "*_galimg.fits")))
		
		if len(imgfilepaths) == 0:
			logger.warning("Could not find any images for '%s' (skipping this one)" % (inputcat))
			continue
			
		for imgfilepath in imgfilepaths:
		
			# We add the relevant things to the gen* lists:
			genimgfilepaths.append(imgfilepath)
			genincatfilepaths.append(incatfilepath)
			
			#imgname = os.path.basename(imgfilepath)[:-12] # e.g. 20141016T170441_BJjhps_0
			imgname = os.path.splitext(os.path.basename(imgfilepath))[0] # e.g. 20141016T170441_BJjhps_0_galimg
			# Well, doesn't make a big difference for the moment, but let's take the more general one.
			
			genimgnames.append(imgname)
	
	# And we pass the ball to general():
	
	general(genimgfilepaths, genincatfilepaths, measworkdir, measfct, measfctkwargs,
		imgnames = genimgnames, ncpu=ncpu, skipdone=skipdone)
		


def general(imgfilepaths, incatfilepaths, measdir, measfct, measfctkwargs, imgnames=None, ncpu=1, skipdone=True):
	"""
	Run the given shape measurement (measfct) on your images using multiprocessing (ncpu).
	The input should give all the necessary paths.  This is the general case.
	If you want to run on MegaLUT simulations, see the function onsims() above (which calls this function).
	
	:param imgfilepaths: list of paths to the FITS image files
	:param incatfilepaths: list of paths to the **corresponding** pickled input catalogs.
		These catalogs must contain the information required by measfct (and the measfctkwargs)
		to run on the image files. So typically, the catalogs should contain at least some position.
	:param measdir: path to a directory in which the output catalogs should be written.
		**Change the measdir if you change anything to the measfct or its kwargs**.
	:param measfct: The function that measures the shapes. It must take two positional arguments
		(an image, an input catalog), and return an output catalog.
	:param measfctkwargs: keyword arguments controlling the behavior of the measfct
	:type measfctkwargs: dict
	:param imgnames: list of names of the FITS images. If None (default), use the FITS
		image filenames to build a name for the output catalogs.
		Specifying imgnames is required if some of the images happen to have the same filenames,
		or if you don't want the filenames to be used.
	:param ncpu: Maximum number of processes that should be used. Default is 1.
		Set to 0 for maximum number of available CPUs.
	:type ncpu: int
	:type skipdone: If set to False, run on every file found, overwriting previous catalogs.


	.. warning:: If called "in parallel" (e.g., from several python scripts launched at about the same time),
		(in the worst case) all the work in every script might be run.
		Not a safety issue (hence currently no fix for this).  We can see if we want a fix for that.
		(can be done e.g. with temporary files written/detected and deleted by the workers)

	"""
		
	if len(imgfilepaths) != len(incatfilepaths):
		raise RuntimeError("The lists imgfilepaths and incatfilepaths must have the same length")

	if imgnames != None:
		if len(imgfilepaths) != len(imgnames):
			raise RuntimeError("The lists imgfilepaths and imgnames must have the same length")
		# And we check that the user-provided imgnames are indeed unique:
		if len(set(imgnames)) != len(imgnames):
			raise RuntimeError("Give me a unique imgname for every image.")
		
	else:
		# We build our own imgnames
		imgnames = [os.path.splitext(os.path.basename(imgfilepath))[0] for imgfilepath in imgfilepaths]
		if len(set(imgnames)) != len(imgnames):
			raise RuntimeError("Some of your images have the same filename. Give me imgnames to differentiate them.")
		
		
	if not os.path.exists(measdir):
		os.makedirs(measdir)
	
	wslist = [] # The list to be filled with workersettings
	
	for (imgfilepath, imgname, incatfilepath) in zip(imgfilepaths, imgnames, incatfilepaths):
		
		outcatfilepath = os.path.join(measdir, "%s_meascat.pkl" % (imgname))
			
		if skipdone and os.path.exists(outcatfilepath):
			logger.info("Image '%s' has already been measured for this measdir" % (imgname))	
			continue
		else:
			ws = _WorkerSettings(imgfilepath, imgname, incatfilepath, outcatfilepath,
					measfct, measfctkwargs, skipdone)
			wslist.append(ws)
			break ## DEBUG FOR fdntfunc.py, REMOVE LATER
	
	logger.info("Ready to run measurents on %i images." % (len(wslist)))
			
	# And we run a pool of workers on this wslist.
	_run(wslist, ncpu)
		



class _WorkerSettings():
	"""
	A class that holds together all the settings for measuring an image.
	"""
	
	def __init__(self, imgfilepath, imgname, incatfilepath, outcatfilepath,
				 measfct, measfctkwargs, skipdone):
		
		self.imgfilepath = imgfilepath
		self.imgname = imgname
		self.incatfilepath = incatfilepath
		self.outcatfilepath = outcatfilepath
		self.measfct = measfct
		self.measfctkwargs = measfctkwargs
		self.skipdone = skipdone
	
	def __str__(self):
		return "[image '%s']" % (os.path.basename(self.imgfilepath))



def _worker(ws):
	"""
	Worker function that the different processes will execute, processing the
	_WorkerSettings objects.
	"""
	starttime = datetime.datetime.now()
	p = multiprocessing.current_process()
	logger.info("%s is starting to measure %s with PID %s" % (p.name, str(ws), p.pid))
	
	# Read input catalog
	incat = megalut.tools.io.readpickle(ws.incatfilepath)
	
	# Run measfct, it will read the image by itself:
	outcat = ws.measfct(ws.imgfilepath, incat, **ws.measfctkwargs)
	
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

	# We only want to see warnings or worse from the following low-level stuff:
	for modulename in ["megalut.meas.galsim_adamom", "megalut.meas.sewfunc",
			"sewpy.sewpy", "megalut.tools.io", "megalut.tools.image"]:
		lowlevellogger = logging.getLogger(modulename)
		lowlevellogger.setLevel(logging.WARNING)
	
	if ncpu == 0:
		try:
			ncpu = multiprocessing.cpu_count()
		except:
			logger.warning("multiprocessing.cpu_count() is not implemented!")
			ncpu = 1
	
	starttime = datetime.datetime.now()
	
	logger.info("Starting the measurement on %i images using %i CPUs" % (len(wslist), ncpu))
	
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()

	endtime = datetime.datetime.now()
	logger.info("Done, the total measurement time was %s" % (str(endtime - starttime)))
	



