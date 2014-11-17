"""
This module defines wrapper functionality to train ML algorithms in parallel.

It's mainly designed for data obtained using sim/run.py and meas/run.py
"""
import os
import ml

import multiprocessing
import datetime

from .. import tools

import logging
logger = logging.getLogger(__name__)



def train(cat, workbasedir, paramslist, ncpu=1, predict=True):
	"""
	A very general multiprocessing wrapper for the training only.
	
	
	:param paramlist: a list of tuples (MLParams, toolparams), where toolparams can be for instance FANNParam or SkyNetParams.
	
	:param predict: if True, I will save a pickle of a catalog including predictions for each tuple in paramslist.
	
	I'll process this list tuple by tuple.
	
	Assumes that cat contains the columns as returned by meas.avg.onsims() with option removereas=False
	The training is performed usign the "_mean" measurements. This function is taking care of appending the "_mean".
	You just specify the "normal" field names.
	
	
	"""

	# A check that we will not mess up with directories :
	#mlnames = [paramtuple[0].name for paramtuple in paramlist]
	#assert len(mlnames) == len(set(mlnames))
	
	
	# So to run a multiprocessing pool map, we prepare a list of _WorkerSettings:
	wslist = []
			
	for (mlparams, toolparams) in paramslist:
		wslist.append(_WorkerSettings(cat, workbasedir, mlparams, toolparams))
					
	# The single-processing version:
	map(_worker, wslist)
	
	
	
	
		
class _WorkerSettings():
	"""
	Holds the settings for one worker
	"""
	def __init__(self, cat, workbasedir, mlparams, toolparams):
		self.cat = cat
		self.workbasedir = workbasedir
		self.mlparams = mlparams
		self.toolparams = toolparams

	def __str__(self):
		return "(%s, %s)" % (self.mlparams.name, self.toolparams.name)


def _worker(ws):
	"""
	Runs one ML training corresponding to the given _WorkerSettings object.
	"""	
	starttime = datetime.datetime.now()
	p = multiprocessing.current_process()
	logger.info("%s is starting to draw %s with PID %s" % (p.name, str(ws), p.pid))
	
	# The actual task :
	mlobj = ml.ML(ws.mlparams, ws.toolparams, workbasedir=ws.workbasedir)
	mlobj.train(ws.cat)	
	mldir = mlobj.get_workdir()
	print mldir
	tools.io.writepickle(mlobj, os.path.join(mldir, "ML.pkl"))
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))





def predict(cat, workbasedir, paramslist):
	"""
	A smart wrapper to make different kinds of predictions	
	
	* 
	
	"""
	
	for (mlparams, toolparams) in paramslist:



