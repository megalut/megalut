"""
This module defines wrapper functionality to train and use ML algorithms in parallel.

It's mainly designed for data obtained using sim/run.py + meas/run.py + meas/avg.py.

But train() is general and can be used for all kind of experiments, and
predict() is also a great way to predict real observations without having to remove the "_mean"
suffixes from the training params etc.
"""
import os
import ml

import multiprocessing
import datetime

from .. import tools

import logging
logger = logging.getLogger(__name__)



def train(cat, workbasedir, paramslist, ncpu=1):
	"""
	A very general multiprocessing wrapper for the training only.
	Importantly, there is no "magic" processing of any "_mean"-fields here:
	this function just trains using exactly the catalog field names that you specify.
	It does not care if you train a bunch of identical MLs to all predict exactly the same labels,
	or if each of your MLs is designed to predict different labels.
	
	:param cat: an astropy table. This same cat will be used as input for all the ML trainings.
	:param workbasedir: path to a directory in which the results will be written.
	:param paramlist: a list of tuples (MLParams, toolparams), where toolparams can be for instance FANNParam or SkyNetParams.
	:param ncpu: how many cpus should be used in parallel.
	
	.. note:: As the training is done in parallel, this wrapper cannot be used for "iterative" training,
		where one ML uses the predictions of a previous ML as input.	
	
	"""
	#:param predict: **Not implemented** if True, I will save a pickle of a catalog including the trivial self-predictions for each tuple in paramslist.
	#	This is still done in parallel, I do not group these results into a single output catalog here.
	
	
	
	
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





def predict(cat, workbasedir, paramslist, mode="default"):
	"""
	A wrapper to make predictions from non-overlapping-label MLs, returning a single merged catalog. 
	Unlike the above train(), this predict() is quite *smart* and can automatically preform sophisticated tasks.
	 
	This function does require (and check) that all of the MLs specified in paramslist predict different labels. 
	This allows the present function to return a single catalog containing the predictions from different MLs. 
	 
	 
	:param cat: an astropy table, has to contain all the required features
	:param paramslist: exactly the same as used in train()
	:param mode: a switch for different behaviors.
		
		* If mode is "default", it will predict following exactly the column names that the MLparams of the paramslist specify.
		* If "single", it will drop any "_mean" in the feature column names.
		  This is the mode which is meant to be useful when predicting real observations!
		* If "first", it will replace any "_mean" by "_0", thus using only the first realization.
		  This is a mode only useful for simulations.
		  It allows a fair comparisions of the predictions based on simulations and real observations. 
		  Of course it works only if meas.avg.onsims() was run with the option removereas=False. 
		  It allows a fair comparisions of the predictions based on simulations and real observations.
		* If "all", it will predict all realizations (_0, _1, ...), and then use groupstats to compute statistics
		  of the predictions coming from the different realizations.
		  So this mode is related to error bars on predictions, subject to be analysed.
	
		
	"""
	
	#for (mlparams, toolparams) in paramslist:



