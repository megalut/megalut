"""
This module defines wrapper functionality to train and use several ML algorithms (say several ANNs), using multiprocessing.
The motivation is that commonly we use independent ANNs to predict different features,
or need to test different ANN settings, etc.

.. note:: This module is NOT only designed for data obtained using sim/run.py + meas/run.py + meas/avg.py.
	Indeed train() is general and can be used for all kind of experiments, and
	predict() is also a great way to predict real observations without having to remove the "_mean"
	suffixes from the training params etc.

"""
import os
import ml

import multiprocessing
import datetime
import copy

from .. import tools

import logging
logger = logging.getLogger(__name__)



def train(cat, workbasedir, paramslist, ncpu=1):
	"""
	A very general multiprocessing wrapper for the training *only* (no predictions: it does not modify or return the input catalog).
	Importantly, there is no "magic" processing of any "_mean"-fields here:
	this function just trains using exactly the catalog field names that you specify.
	It does not care if you train a bunch of identical MLs to all predict exactly the same labels,
	or if each of your MLs is designed to predict different labels.
	
	:param cat: an astropy table. This same cat will be used as input for all the ML trainings.
	:param workbasedir: path to a directory in which the results will be written.
	:param paramlist: a **list** of tuples (MLParams, toolparams) (as many as you want),
		where the toolparams can be for instance FANNParam or SkyNetParams objects.
	:param ncpu: how many cpus should be used in parallel.
	
	.. note:: For developers: the reasons why no self-predictions are done (would in principle be possible by making
		the workers return the newly predicted columns, and merging them in the main process):
		
		- keep it working even for identical MLParams (committee, or tests with different toolparams only)
		  Although the best for such tests is probably to prepare different MLParams, so that you can later use run.predict().
		- avoid cluttering this function with all the different kind of predictions (individual realization, mean, etc).
	
		As the training is done in parallel, and as no predictions are done,
		this wrapper cannot be used for "iterative" training,
		where one ML uses the predictions of a previous ML as input.
		
		One could add a switch "predict": if True, it would save a pickle of a catalog including the trivial self-predictions
		for each tuple in paramslist (without grouping these results into a single output catalog).
		**But** writing all these catalogs to disk is not very elegant or helpful, so I thought that better just use predict
		even to get trivial self-predictions on training data.
	
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
	
	if ncpu == 1: # The single-processing version, much easier to debug !
		map(_worker, wslist)
	
	else: # The simple multiprocessing map is:
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
	A wrapper to make predictions from non-overlapping-predlabel MLs, returning a single merged catalog. 
	Unlike the above train(), this predict() is quite *smart* and can automatically preform sophisticated tasks
	related to the "_mean" averaging over realizations.
	 
	This function does require (and check) that all of the MLs specified in paramslist **predict different predlabels** 
	This allows the present function to return a single catalog containing the predictions from different MLs.
	 
	:param cat: an astropy table, has to contain all the required features
	:param paramslist: exactly the same as used in train()
	:param mode: a switch for different behaviors:		
	
		* If mode is "default", it will predict using exactly the column names that the MLParams of the paramslist specify.
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
	
	logger.debug("Predicting with mode '%s'..." % (mode))
	
	# We check that the MLs do not predict the same predlabels, as otherwise we can't merge the predictions into a single catalog.
	predlabels = []
	for (mlparams, toolparams) in paramslist:
		predlabels.extend(mlparams.predlabels)
	if len(predlabels) != len(set(predlabels)):
		raise RuntimeError("Your predlabels are not unique.")

	
	# And now we make the predictions one after the other, always reusing the same catalog.
	
	predcat = copy.deepcopy(cat)
	
	for (mlparams, toolparams) in paramslist:
		
		# We create a new ML object, to get the workdir that was used
		newmlobj = ml.ML(mlparams, toolparams, workbasedir=workbasedir)
		
		# We load the actual ML object that was used for the training:
		trainedmlobj = tools.io.readpickle(os.path.join(newmlobj.workdir, "ML.pkl"))
		
		# We now check that newmlobj has the same params as the one used for training.
		# This should be the case, we do not want to allow for any "hacking" here.
		if not newmlobj.looks_same(trainedmlobj):
			raise RuntimeError("Looks like the parameters for %s are not the ones used for the training." % (str(newmlobj)))
	
		# And now that we know that the params are fine, we tweak things according to the mode
		tweakedmlobj = copy.deepcopy(trainedmlobj)
		# Note that for the prediction we have to use trainedmlobj, and not newmlobj.
		# Indeed the training is free to save some information in the trainedmlobj, and so we cannot simply use a new object.
		
		if mode == "default":
			pass
			predcat = tweakedmlobj.predict(predcat)			
			
		elif mode == "single": # Drop any "_mean" from features
	
			tweakedfeatures = []
			for feature in tweakedmlobj.mlparams.features:
				if feature.endswith("_mean"):
					tweakedfeatures.append(feature[:-len("_mean")])
				else:
					tweakedfeatures.append(feature)
			tweakedmlobj.mlparams.features = tweakedfeatures
			predcat = tweakedmlobj.predict(predcat)
			
		elif mode == "first": # Replace "_mean" by "_0"
		
			tweakedfeatures = []
			for feature in tweakedmlobj.mlparams.features:
				if feature.endswith("_mean"):
					tweakedfeatures.append(feature[:-len("_mean")] + "_0")
				else:
					tweakedfeatures.append(feature)
			tweakedmlobj.mlparams.features = tweakedfeatures
			predcat = tweakedmlobj.predict(predcat)
		
		elif mode == "all": # Replace "_mean" by all realizations, and then groupstat...
			
			# We start with some preparatory work:
			# See how many realizations we have, and check that we have all the features that we need.
			
			print cat.meta["ngroupstats"]
			
			exit()
			reafeatures = [] # features that have many realizations
			for feature in tweakedmlobj.mlparams.features:
				if feature.endswith("_mean"):
					reafeatures.append(feature[:-len("_mean")])
			
			logger.debug("")
			
			
			
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		else:
			raise RuntimeError("Unknown mode '%s'" % mode)
			
	return predcat



