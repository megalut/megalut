"""
This module defines wrapper functionality to train ML algorithms in parallel.

It's mainly designed for data obtained using sim/run.py and meas/run.py.
"""
import os
import ml

import multiprocessing
import datetime

from .. import tools

import logging
logger = logging.getLogger(__name__)



def train(cat, workbasedir, paramslist, predict=False, ncpu=1):
	"""
	A very general multiprocessing wrapper for the training only.
	Importantly, there is no "magic" processing of "mean"-fields here:
	this function just trains using exactly the catalog field names that you specify.
	It does not care if you train a bunch of identical MLs to all predict exactly the same labels,
	or if each of your MLs is designed to predict different labels.
	
	:param cat: a single astropy table. This same cat will be used as input for all the ML trainings.
	:param workbasedir: path to a directory in which the results will be written.
	:param paramlist: a list of tuples (MLParams, toolparams), where toolparams can be for instance FANNParam or SkyNetParams.
	:param predict: **Not implemented** if True, I will save a pickle of a catalog including the trivial self-predictions for each tuple in paramslist.
		This is still done in parallel, I do not group these results into a single output catalog here.
	:param ncpu: how many cpus should be used in parallel.
	
	.. note:: As the training is done in parallel, this wrapper cannot be used for "iterative" training,
		where one ML uses the predictions of a previous ML as input.	
	
	"""
	starttime = datetime.datetime.now()
	
	# To run a multiprocessing pool map, we prepare a list of _WorkerSettings:
	wslist = []
	
	for (mlparams, toolparams) in paramslist:
	
		mlobj = ml.ML(mlparams, toolparams, workbasedir=workbasedir)
		wslist.append(_WorkerSettings(cat, mlobj, predict))
	
	# Before starting, we check that all the ml workdirs are different:
	mlnames = [str(ws.ml) for ws in wslist]
	if len(mlnames) != len(set(mlnames)):
		raise RuntimeError("The combinations of the MLParams and toolparams names in your paramslist are not unique.")
	
	logger.info("Starting to train %i MLs using %i CPUs" % (len(paramslist), ncpu))
			
	# The single-processing version:
	#map(_worker, wslist)
	
	# The simple multiprocessing map is:
	pool = multiprocessing.Pool(processes=ncpu)
	pool.map(_worker, wslist)
	pool.close()
	pool.join()
	
	endtime = datetime.datetime.now()
	logger.info("Done, the total time for training the %i MLs was %s" % (len(paramslist), str(endtime - starttime)))

		
class _WorkerSettings():
	"""
	Holds the settings for one worker to perform one ML training.
	"""
	def __init__(self, cat, mlobj, predict):
		self.cat = cat
		self.ml = mlobj
		self.predict = predict

	def __str__(self):
		return str(self.ml)


def _worker(ws):
	"""
	Runs one ML training corresponding to the given _WorkerSettings object.
	"""	
	starttime = datetime.datetime.now()
	p = multiprocessing.current_process()
	logger.info("%s is starting to draw %s with PID %s" % (p.name, str(ws), p.pid))
	
	# The actual task:
	ws.ml.train(ws.cat)	
	
	# We write the ML object to pickle
	tools.io.writepickle(ws.ml, os.path.join(ws.ml.workdir, "ML.pkl"))
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))





def predict(cat, workbasedir, paramslist):
	"""
	A wrapper to make different kinds of predictions, returning a single catalog.
	Unlike the above train(), this predict() is *smart* and does autoatically preform different tasks.
	
	It does require (and check) that all of the MLs specified in paramslist predict different labels. This allows the
	present function to return a single catalog containing the predictions from different MLs.
	
	
	By default, it will predict following exactly the column names that the MLparams of the paramslist specify.
	
	if "single", it will drop any "_mean" in the feature column names.
	This is the mode which is useful when predicting real observations!
	
	if "all"
	
	
	* 	Assumes that cat contains the columns as returned by meas.avg.onsims() with option removereas=False
	The training is performed usign the "_mean" measurements. This function is NOT taking care of appending the "_mean".
	You just specify the "normal" field names.

	
	"""
	
	#for (mlparams, toolparams) in paramslist:



