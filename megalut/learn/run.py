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
	logger.info("%s is starting to train %s with PID %s" % (p.name, str(ws), p.pid))
	
	# The actual task:
	ws.ml.train(ws.cat)	
	
	# We write the ML object to pickle
	tools.io.writepickle(ws.ml, os.path.join(ws.ml.workdir, "ML.pkl"))
	
	endtime = datetime.datetime.now()
	logger.info("%s is done, it took %s" % (p.name, str(endtime - starttime)))



def predict(cat, workbasedir, paramslist, tweakmode="default", totweak="_mean", modmlparams=False):
	"""
	A wrapper to make predictions from non-overlapping-predlabel MLs, returning a single merged catalog. 
	Unlike the above train(), this predict() is quite *smart* and can automatically preform sophisticated tasks
	related to the "_mean" averaging over realizations.
	 
	This function does require (and check) that all of the MLs specified in paramslist **predict different predlabels** 
	This allows the present function to return a single catalog containing the predictions from different MLs.
	 
	:param cat: an astropy table, has to contain all the required features
	:param paramslist: exactly the same as used in train()
	:param tweakmode: a switch for different behaviors regarding which *features* to use for the predictions	
	
		* If mode is "default", it will predict using exactly the column names that the MLParams of the paramslist specify.
		* If "all", it will predict all realizations by replacing "totweak" with (_rea0, _rea1, ...), and then use groupstats to compute statistics
		  of the predictions coming from the different realizations, resulting in field names such as
		  pre_g1_mean, pre_g1_std, etc.
		  So this mode will only be used on simulations, and is related to debiasing or getting error bars on predictions.
		  The input catalog must in this case contain all the realizations: this is obtained by running
		  meas.avg.onsims with the option removereas=False.
		* If mode is an integer (say n), it will do the same as for mode "all", but using only the n first
		  realizations.
		* If any other string (even empty: ""), it will replace the suffix totweak (e.g., "_mean") by the given string.
		  Use an empty string to "drop" the suffix.
	
	:param totweak: the suffix that should be detected and tweaked, according to the tweakmode setting.
		
	When predicting simulations, one typically runs this twice in a row: once in mode "all" or "integer" to get pre_X_std,
	and once in mode "first" or "default" to get pre_X.
	Note that it has to be done in **this order**, otherwise ml.predict will complain, as it needs to be able to write columns pre_X
	in order to compute pre_X_std etc.	
	"""
	
	logger.debug("Predicting with tweakmode '%s' and totweak '%s'..." % (tweakmode, totweak))
	
	# We check that the MLs do not predict the same predlabels, as otherwise we can't merge the predictions into a single catalog.
	predictions = []
	for (mlparams, toolparams) in paramslist:
		predictions.extend(mlparams.predictions)
	if len(predictions) != len(set(predictions)):
		raise RuntimeError("Your predictions are not unique.")

	
	# And now we make the predictions one after the other, always reusing the same catalog.
	
	predcat = copy.deepcopy(cat)
	
	for (mlparams, toolparams) in paramslist:
		
		# We create a new ML object, to get the workdir that was used
		newmlobj = ml.ML(mlparams, toolparams, workbasedir=workbasedir)
		
		# We load the actual ML object that was used for the training:
		trainedmlobj = tools.io.readpickle(os.path.join(newmlobj.workdir, "ML.pkl"))
		
		if modmlparams == False:
			# We now check that newmlobj has the same params as the one used for training.
			# This should be the case, we do not want to allow for any "hacking" here.
			if not newmlobj.looks_same(trainedmlobj):
				pass
				logger.critical("Looks like the parameters for %s are not the ones used for the training." % (str(newmlobj)))
				#raise RuntimeError("Looks like the parameters for %s are not the ones used for the training." % (str(newmlobj)))
	
			# And now that we know that the params are fine, we tweak things according to the mode
			tweakedmlobj = copy.deepcopy(trainedmlobj)
			# Note that for the prediction we have to use trainedmlobj, and not newmlobj.
			# Indeed the training is free to save some information in the trainedmlobj, and so we cannot simply use a new object.
		
		else:
			# Else, the MLparamslist given to predict has been modified compared to the one used for training.
			# We start from the actual training object:
			tweakedmlobj = copy.deepcopy(trainedmlobj)
			
			#if not newmlobj.looks_same(trainedmlobj):
			#	print "yep, something changed"
	
			# And copy the modifications:
			tweakedmlobj.mlparams = mlparams
		
		
		
		if tweakmode == "default":
			predcat = tweakedmlobj.predict(predcat)			
			
		elif tweakmode == "all" or type(tweakmode) == int: # Replace "totweak" successively by all realizations, and then run groupstat...
			
			# We start with some preparatory work:
			# See how many realizations we have
			try:
				nrea_available = cat.meta["ngroupstats"]
			except:
				raise RuntimeError("Input catalog has no ngroupstats in its meta dict")
			
			reapredcats = [] # Predicted catalogs will get added to this list
			origfeatures = copy.deepcopy(trainedmlobj.mlparams.features) # A list of the features (we won't change this list)
			
			if type(tweakmode) == int:
				nrea_touse = tweakmode
				if nrea_touse > nrea_available:
					raise RuntimeError("Cannot use %i realizations, as only %i are available in the input catalog" % (nrea_touse, nrea_available))
			else:
				nrea_touse = nrea_available
				
			logger.info("Starting predictions on %i (out of %i) realizations..." % (nrea_touse, nrea_available))
			for irea in range(nrea_touse):
				replacement_suffix = "_rea%i" % (irea)
				tweakedfeatures = tweakfeatures(origfeatures, mode=replacement_suffix, totweak=totweak)
				tweakedmlobj.mlparams.features = tweakedfeatures
				reapredcats.append(tweakedmlobj.predict(predcat))
			
			logger.info("Done, now calling groupstats")
			
			# We want to group the predictions (predlabels) obtained on the different realizations.
			groupcols = tweakedmlobj.mlparams.predlabels
			
			# We can't and shouldn't remove the realization measurements here, they might be needed for the next step in paramslist !
			removecols = None
			
			# And we run groupstats:
			predcat = tools.table.groupstats(reapredcats, groupcols=groupcols, removecols=removecols, removereas=False, keepfirstrea=False)
			# We use removereas = True as we do not want the predictiosn for every realization in the catalog
			# We use keepfirstrea = False as we do not want columns like pre_g1_0

		
		else: # we just call tweakfeatures, with whatever the user asks for:
			tweakedfeatures = tweakfeatures(tweakedmlobj.mlparams.features, mode=tweakmode, totweak=totweak)
			tweakedmlobj.mlparams.features = tweakedfeatures
			predcat = tweakedmlobj.predict(predcat)
			
	return predcat



def tweakfeatures(features, mode=None, totweak="_mean"):
	"""
	A helper function to "tweak" feature names, for instance by replacing "_mean" with "_0" to
	get predictions from the first realisation, etc.
	This function is used/called for example by predict().
	
	:param features: a list of strings
	:param mode: how to perform the tweaking
		
		* If mode is None, nothing gets tweaked, we return the input features.
		* If mode is an empty string (""), it will drop any totweak-suffix (e.g., "_mean")
		* If any other string, it will replace totweak by this string
		
	:param totweak: suffix of features to be tweaked
	:returns: a list of tweaked strings (same size as input list).
	
	"""

	if mode == None:
		return copy.deepcopy(features)
	
	else:
		if type(mode) != str:
			raise RuntimeError("Argument mode should be a string")
		tweakedfeatures = []
		for feature in features:
			if feature.endswith(totweak):
				tweakedfeatures.append(feature[:-len(totweak)] + mode)
			else:
				tweakedfeatures.append(feature)
		
		assert len(features) == len(tweakedfeatures)
		return tweakedfeatures
