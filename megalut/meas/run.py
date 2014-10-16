"""
High-level functions to measure features on a set of images. This addresses two situations:

- measure features on real observed images of your survey
- measure on simulated stamps produced by megalut.sim.run.multi()

Use the function multi() to deal with both situations.
For both situations we want to use multiprocessing.Pool to distribute the work.
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


def multi(simdir, simparamsname, measdir, measfct, measfctkwargs, ncpu=1):
	"""
	
	:param measfct: the function that measures the shapes. It must take two positional arguments
		(an image, an input catalog), and return an output catalog.
	
	:param measfctkwargs: keyword arguments controlling the behavior of the measfct
	:type measfctkwargs: dict
	
	
	It's quite easy to immitate the sim.run.multi() structure.
	I do not require the timestamps etc.
	
	"""
	
	wslist = [] # The list to be filled with workersettings
	
	simworkdir = os.path.join(simdir, simparamsname)
	inputcats = sorted(glob.glob(os.path.join(simworkdir, "*_cat.pkl")))
	
	measworkdir = os.path.join(measdir, simparamsname)
	if not os.path.exists(measworkdir):
		os.makedirs(measworkdir)
	
	for inputcat in inputcats:
		catname = os.path.basename(inputcat)[:-8]
		imgdir = os.path.join(simworkdir, catname + "_img")
		if not os.path.exists(imgdir):
			logger.warning("I could not find the image directory for '%s' (skipping this one)" % (inputcat))
			continue
			
		images = sorted(glob.glob(os.path.join(imgdir, "*_galimg.fits")))
		imageindexes = map(lambda fp: os.path.basename(fp)[:-12], images) # We do not require an int
		
		if len(images) == 0:
			logger.warning("I could not find any images for '%s' (skipping this one)" % (inputcat))
			continue
			
		for imageindex in imageindexes:
		
			ws = _WorkerSettings(
				imgfilepath = os.path.join(imgdir, "%s_galimg.fits" % (imageindex)),
				incatfilepath = inputcat,
				outcatfilepath = os.path.join(measworkdir, "%s_%s_meascat.pkl" % (catname, imageindex)),
				measfct = measfct,
				measfctkwargs = measfctkwargs
			)
			
			
			wslist.append(ws)
	
	# And we run a pool of workers on this wslist.
	
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()
	
		


class _WorkerSettings():
	"""
	Holds together all the instructions for a worker.
	"""
	
	def __init__(self, imgfilepath=None, incatfilepath=None, outcatfilepath=None, measfct=None, measfctkwargs=None):
		self.imgfilepath = imgfilepath
		self.incatfilepath = incatfilepath
		self.outcatfilepath = outcatfilepath
		self.measfct = measfct
		self.measfctkwargs = measfctkwargs
		

def _worker(ws):
	"""
	Worker function that the different processes will execute.
	"""
	# Read image file
	img = megalut.tools.image.loadimg(ws.imgfilepath)
	
	# Read input catalog
	incat = megalut.tools.io.readpickle(ws.incatfilepath)
	
	# Run measfct
	outcat = ws.measfct(img, incat, **ws.measfctkwargs)
	
	# Write output catalog
	megalut.tools.io.writepickle(outcat, ws.outcatfilepath)







