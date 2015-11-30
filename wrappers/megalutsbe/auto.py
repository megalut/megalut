"""
This module contains stuff for a "single-step" application of MegaLUT to SBE data, for testing by the SDC.

Given the very different approach from what I did when playing with the SBE interactively...
	1) regarding the multiprocessing (one job per image, end-to-end: we do not use MegaLUT's own multiprocessing)
	2) regarding the configuration (seen as pure input, not generated  by previous steps)
...we do not attempt to reuse any run.Run code here.
So there is some code duplication from run.Run.

Malte, November 2015
"""

import os
import sys
import glob
import datetime
import multiprocessing

import astropy
import numpy as np

from . import io

import megalut

import logging
logger = logging.getLogger(__name__)



def buildworkers(sbedatadir, configdir, topworkdir, n=None):
	"""
	Sets up the workers to process some SBE data.
	
	:param n: return only the "n" first workers
	
	"""
	logger.info("Starting to build workers...")
	
	sbepaths = io.get_filenames(sbedatadir)
	
	workers = [Worker(sbepath, configdir, topworkdir) for sbepath in sbepaths]
	
	if n != None:
		workers = workers[:n]
	
	logger.info("Done with building {} workers".format(len(workers)))
	return workers
	

def run(workers, ncpu=1):
	"""
	Runs the workers, usign a multiprocessing pool.
	"""
	
	if ncpu == 1: # The single process way (MUCH MUCH EASIER TO DEBUG...)
		logger.info("Starting to run {} workers one after the other on a single CPU...".format(len(workers)))
		map(work, workers)
	
	else:
		logger.info("Starting to run {} workers in a pool of {} CPUs...".format(len(workers), ncpu))
		pool = multiprocessing.Pool(processes=ncpu)
		pool.map(work, workers)
		pool.close()
		pool.join()
	
	logger.info("All workers are done!")
		
		
def work(worker):
	"""
	Defines the work to be done by a Worker
	"""
	
	worker.prepare()
	worker.makeobsincat()
	worker.measobs()
	worker.predictobs()



class Worker():
	"""
	A Worker does its work on one single SBE image.
	
	"""


	def __init__(self, sbepath, configdir, topworkdir):
		"""
			
		:param sbepath: something like /vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_v3/thread_0/low_SN_image_2
		:param workdir: a top-level workdir in which each worker can make its own sub-workdir.
		
		"""
		self.sbepath = sbepath
		self.configdir = configdir
		self.topworkdir = topworkdir
		
		self.sbeimagepath = io.imagefile(self.sbepath)
		self.sbedatapath = io.datafile(self.sbepath)
		self.workname = io.workname(self.sbepath)
		self.workdir = os.path.join(self.topworkdir, self.workname) # The general workdir to be used for this particular worker
		self.imageworkdir = os.path.join(self.workdir, "imageworkdir")
		
		self.incatfilepath = os.path.join(self.workdir, "incat.pkl")
		self.meascatfilepath = os.path.join(self.workdir, "meascat.pkl")
		
	
	def __str__(self):
		"""
		Uses the workname
		"""
		return "Worker({})".format(self.workname)

	
	def prepare(self):
		"""
		Creates directories
		"""
	
		logger.info("Preparing directories for {}...".format(self))
		
		if not os.path.exists(self.topworkdir):
			os.makedirs(self.topworkdir)
		if not os.path.exists(self.workdir):
			os.makedirs(self.workdir)
	
		
	def makeobsincat(self, stampsize=200, n=32):
		"""
		Turns the SBE catalogs into MegaLUT catalogs 
		"""
		
		logger.info("Making the input catalog for {}...".format(self))
		
		# We read the data file and turn it into an astropy table
		cat = astropy.io.ascii.read(self.sbedatapath)
			
		# Let's keep the file identification also in the meta dict:
		cat.meta["workname"] = self.workname
		   
		# We add the xid, yid, x and y columns
		# Did some trial and error tests, to find out that one should start y at the bottom
		# to get compatible with MegaLUT standarts.
		cat["xid"] = np.concatenate([np.arange(n) for i in range(n)])
		cat["yid"] = np.concatenate([np.ones(n, dtype=np.int)*i for i in range(n)])		
		cat["x"] = stampsize/2.0 + cat["xid"]*(stampsize + 1) + 0.5
		cat["y"] = stampsize/2.0 + cat["yid"]*(stampsize + 1) + 0.5
					
		# We create the ImageInfo object
		img = megalut.tools.imageinfo.ImageInfo(
			filepath = self.sbeimagepath,
			xname = "x", yname = "y",
			stampsize = stampsize,
			workdir = self.imageworkdir
		)
		cat.meta["img"] = img
			
		# And save the catalog
		megalut.tools.io.writepickle(cat, self.incatfilepath)


	def measobs(self):
		"""
		Measures features on the inputs
		"""
		logger.info("Starting feature measurement {}...".format(self))
		
		# We read the measfct
		measfct = {}
		execfile(os.path.join(self.configdir, "measfct.py"), measfct)
		measfctkwargs = {}
	
		megalut.meas.run.general([self.incatfilepath], [self.meascatfilepath], measfct["default"], measfctkwargs, ncpu=1, skipdone=False)

	
	
	def predictobs(self):
		"""
		Runs the ANNs to predict shear
		"""
		
		
		"""
		cat = megalut.tools.io.readpickle(self.groupobspath)
		#print cat.colnames
		#print len(cat)
		#exit()
		
		cat["pw"] = cat["snr"]**2 # does not harm for non-pw trainings...
		
		traindir = os.path.join(self.workmldir, "with_" + simparams.name)
		
		cat = megalut.learn.run.predict(cat, traindir, mlparams)
			
		megalut.tools.io.writepickle(cat, os.path.join(self.workobsdir, "predgroupobs.pkl"))

		"""
		
		
		
		
