"""
Top level function implementing "mean-posterior" regression and then iterative bias corrections

These features are work in progress, not documented, and will have to be cleaned once a good way of calibrating the bias has
been found.

"""
import os
import ml

import multiprocessing
import datetime
import copy
import numpy as np

from .. import tools
from .. import plot

import astropy

import run

import logging
logger = logging.getLogger(__name__)



def ontruth(cats, workbasedir, paramslist, calibtoolparams, ncit = 10):
	"""
	
	Attempt to calibrate bias iteratively by fitting the bias(truth) relation and using it with predictions instead of truth.
	Does not work, as the corrections bring predictions away from the truth domain.

	cats are different realizations of the same cat
	
	The "first iteration" called "cit0" is the training based on the actual features (and not on previous predictions)
	
	"""

	#origparamslist = copy.deepcopy(paramslist)
		

	# We perform the first training on a single realization
	logger.info("Performing first ML training, based on measurements.")
	
		
	modparamslist = copy.deepcopy(paramslist) # this is for "cit0"
	for (mlparams, toolparams) in modparamslist:
		mlparams.name += "_cit0"
		mlparams.predlabels = [predlabel + "_cit0" for predlabel in mlparams.predlabels]
	
	run.train(cats[0], workbasedir, modparamslist) # For now, we just use the first cat.
	
	
	# We predict every realization with exactly this ML, leading to "_cit0" predictions:
		
	cats = [run.predict(cat, workbasedir, modparamslist, tweakmode="default") for cat in cats]


	# We compute errors for every prediction in every cat
	
	groupcols = [] # What we want to average over
	biasfeatures = [] # Will be used as feature for the next stage
	for (mlparams, toolparams) in modparamslist:
		for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			errcol = predlabel + "_err"
			groupcols.append(errcol)
			biasfeatures.append(label)
			
			for cat in cats:		
				cat[errcol] = cat[predlabel] - cat[label]


	if len(biasfeatures) != len(set(biasfeatures)):
		raise RuntimeError("biasfeatures error")
	logger.info("Bias correction will be learned in the parameter space: %s" % (biasfeatures))


	# Starting from here we loop over the different calibration iterations:
	for citi in range(ncit):
		logger.info("Learning calibration iteration %i..." % (citi))

		# In each loop, we will add columns to cats, update groupcols, and above all save the trained calibration MLs.

		# Average the errors over the realizations, in a temporary avgcat
		# We want the average cat to have only the minimum required fields for the next stage:
	
		removecols = [col for col in cats[0].colnames if col not in groupcols + biasfeatures]
		avgcat = tools.table.groupstats(cats, groupcols=groupcols, removecols=removecols, removereas=True, keepfirstrea=False)

		# And we train a ML to predic each bias, based on all true shape parameters
		# For this we build a new paramslist, as the ML is quite different
	
		tmpparamslist = copy.deepcopy(paramslist)
		biasparamslist = []
	
		for (mlparams, toolparams) in tmpparamslist:
	
			mlparams.name += "_cit%i_bias" % (citi)
			mlparams.features = biasfeatures
			mlparams.labels = [predlabel + "_cit%i_err_mean" % (citi) for predlabel in mlparams.predlabels]
		
			# temporary storing the feature names to be used when predicting, that is the predictions from "last stage"
			mlparams.tmppredfeatures = [predlabel + "_cit%i" % (citi)  for predlabel in mlparams.predlabels]
		
			mlparams.predlabels = [predlabel + "_cit%i_prebias" % (citi) for predlabel in mlparams.predlabels]
		
			biasparamslist.append((mlparams, calibtoolparams))
	

		# The training happens on the prepared avgcat
		run.train(avgcat, workbasedir, biasparamslist)
		
		# To visualize how this training went, let's self-predict on the avgcat
		avgcat = run.predict(avgcat, workbasedir, biasparamslist)
	
		# And now we predict the bias on the actual cats, using this ML
		# But here we replace the "true" features by our last estimates
	
		for (mlparams, toolparams) in biasparamslist:
			mlparams.features = mlparams.tmppredfeatures
		
		cats = [run.predict(cat, workbasedir, biasparamslist, modmlparams=True) for cat in cats]

		# "apply" these predicted calibrations, and compute current errors to be used for the next stage
	
		groupcols = []
		for (mlparams, toolparams) in paramslist:
			for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			
				for cat in cats:	
					# the calibrated prediction:
					cat[predlabel+"_cit%i" % (citi+1)] = cat[predlabel+"_cit%i" % (citi)] - cat[predlabel+"_cit%i_prebias" % (citi)]
					
					# And we clip, to the authorized region
					#minlabel = np.ma.min(cat[label])
					#maxlabel = np.ma.max(cat[label])
					#print minlabel, maxlabel
					#cat[predlabel+"_cit%i" % (citi+1)] = np.clip(cat[predlabel+"_cit%i" % (citi+1)], minlabel, maxlabel)
				
					# the error of the latter:
					cat[predlabel+"_cit%i_err" % (citi+1)] = cat[predlabel+"_cit%i" % (citi+1)] - cat[label]
			
				groupcols.append(predlabel+"_cit%i_err" % (citi+1))
				
				plotpath = os.path.join(workbasedir, "%s_%s_cit%i.png" % (mlparams.name, label, citi))
				#biasplot_truth(cats, avgcat, label, predlabel, citi, filepath=plotpath)
				biasplot_truth(cats, avgcat, label, predlabel, citi, filepath=None)
		
		# End of the loop. groupcols is defined for the next iteration. 






def onpred(cat, workbasedir, paramslist, calibtoolparams, ncit = 10):
	"""
	Here we don't use cats, but a single cat
	
	"""
		

	# We perform the first training on a single realization
	logger.info("Performing first ML training, based on measurements.")
	
		
	modparamslist = copy.deepcopy(paramslist) # this is for "cit0"
	for (mlparams, toolparams) in modparamslist:
		mlparams.name += "_cit0"
		mlparams.predlabels = [predlabel + "_cit0" for predlabel in mlparams.predlabels]
	
	run.train(cat, workbasedir, modparamslist) # For now, we just use the first cat.
	
	
	# We predict every realization with exactly this ML, leading to "_cit0" predictions:
		
	cat = run.predict(cat, workbasedir, modparamslist, tweakmode="default")


	# We compute errors for every prediction
	
	biasfeatures = [] # Will be used as feature for the next stage
	for (mlparams, toolparams) in modparamslist:
		for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			errcol = predlabel + "_err"
			
			biasfeatures.append(predlabel)
			
			cat[errcol] = cat[predlabel] - cat[label]

	logger.info("Bias correction will be learned in the parameter space: %s" % (biasfeatures))


	# Starting from here we loop over the different calibration iterations:
	for citi in range(ncit):
		logger.info("Learning calibration iteration %i..." % (citi))

		# In each loop, we will add columns to cat, update groupcols, and above all save the trained calibration MLs.

		# And we train a ML to predic each bias, based on all true shape parameters
		# For this we build a new paramslist, as the ML is quite different
	
		tmpparamslist = copy.deepcopy(paramslist)
		biasparamslist = []
		biasfeatures = [] # Will be used as feature for the next stage
	
		for (mlparams, toolparams) in tmpparamslist:
			for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
				biasfeatures.append(predlabel + "_cit%i" % (citi))
		
		if len(biasfeatures) != len(set(biasfeatures)):
			raise RuntimeError("biasfeatures error")
		
	
		for (mlparams, toolparams) in tmpparamslist:
	
			mlparams.name += "_cit%i_bias" % (citi)
			mlparams.features = biasfeatures # all of them
			mlparams.labels = [predlabel + "_cit%i_err" % (citi) for predlabel in mlparams.predlabels] # just the ones from this mlparams object
		
			mlparams.predlabels = [predlabel + "_cit%i_prebias" % (citi) for predlabel in mlparams.predlabels]
		
			biasparamslist.append((mlparams, calibtoolparams))
	

		# The training
		run.train(cat, workbasedir, biasparamslist)
		
		# self-predict
		cat = run.predict(cat, workbasedir, biasparamslist)
	
		# "apply" these predicted calibrations, and compute current errors to be used for the next stage
	
		for (mlparams, toolparams) in paramslist:
			for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			
				
				# the calibrated prediction:
				cat[predlabel+"_cit%i" % (citi+1)] = cat[predlabel+"_cit%i" % (citi)] - cat[predlabel+"_cit%i_prebias" % (citi)]
				
				# the error of the latter:
				cat[predlabel+"_cit%i_err" % (citi+1)] = cat[predlabel+"_cit%i" % (citi+1)] - cat[label]
			
				
				plotpath = os.path.join(workbasedir, "%s_%s_cit%i_pred.png" % (mlparams.name, label, citi))
				biasplot_pred(cat, label, predlabel, citi, filepath=plotpath)
				#biasplot_pred(cat, label, predlabel, citi, filepath=None)
		
		# End of the loop. groupcols is defined for the next iteration. 




def onpredavg(cats, workbasedir, paramslist, calibtoolparams, ncit = 10):
	"""
	
	fitting bias(truth), where bias is determined by avaraging errs over realizations
	
	"""

	#origparamslist = copy.deepcopy(paramslist)
		

	# We perform the first training on a single realization
	logger.info("Performing first ML training, based on measurements.")
	
		
	modparamslist = copy.deepcopy(paramslist) # this is for "cit0"
	for (mlparams, toolparams) in modparamslist:
		mlparams.name += "_cit0"
		mlparams.predlabels = [predlabel + "_cit0" for predlabel in mlparams.predlabels]
	
	run.train(cats[0], workbasedir, modparamslist) # For now, we just use the first cat.
	
	
	# We predict every realization with exactly this ML, leading to "_cit0" predictions:
		
	cats = [run.predict(cat, workbasedir, modparamslist, tweakmode="default") for cat in cats]


	# We compute errors for every prediction in every cat
	
	groupcols = [] # What we want to average over
	for (mlparams, toolparams) in modparamslist:
		for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			errcol = predlabel + "_err"
			groupcols.append(errcol)
			#groupcols.append(predlabel)
			
			for cat in cats:		
				cat[errcol] = cat[predlabel] - cat[label]


	# Starting from here we loop over the different calibration iterations:
	for citi in range(ncit):
		logger.info("Learning calibration iteration %i..." % (citi))

		# In each loop, we will add columns to cats, update groupcols, and above all save the trained calibration MLs.

		# Average the errors over the realizations, in a temporary avgcat
		
		removecols = [col for col in cats[0].colnames if col not in groupcols]
		avgcat = tools.table.groupstats(cats, groupcols=groupcols, removecols=removecols, removereas=True, keepfirstrea=False)
		
		# We copy cats[0] into this avgcat, to have the fields at hand.
		avgcat = astropy.table.hstack([avgcat, cats[0]])
		#print avgcat.colnames
		
		
		biasfeatures = [] # Will be used as feature for the next stage
		for (mlparams, toolparams) in paramslist:
			for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
				biasfeatures.append(predlabel + "_cit%i" % (citi))
			
		# And we train a ML to predic each bias, based on all true shape parameters
		# For this we build a new paramslist, as the ML is quite different
	
		tmpparamslist = copy.deepcopy(paramslist)
		biasparamslist = []
	
		for (mlparams, toolparams) in tmpparamslist:
	
			mlparams.name += "_cit%i_bias" % (citi)
			mlparams.features = biasfeatures
			mlparams.labels = [predlabel + "_cit%i_err_mean" % (citi) for predlabel in mlparams.predlabels]
		
			mlparams.predlabels = [predlabel + "_cit%i_prebias" % (citi) for predlabel in mlparams.predlabels]
		
			biasparamslist.append((mlparams, calibtoolparams))
	

		# The training happens on the prepared avgcat
		run.train(avgcat, workbasedir, biasparamslist)
		
		# To visualize how this training went, let's self-predict on the avgcat
		avgcat = run.predict(avgcat, workbasedir, biasparamslist)
	
		# And now we predict the bias on the actual cats, using this ML
		
		cats = [run.predict(cat, workbasedir, biasparamslist) for cat in cats]

		# "apply" these predicted calibrations, and compute current errors to be used for the next stage
	
		groupcols = []
		for (mlparams, toolparams) in paramslist:
			for (label, predlabel) in zip(mlparams.labels, mlparams.predlabels):
			
				for cat in cats:	
					# the calibrated prediction:
					cat[predlabel+"_cit%i" % (citi+1)] = cat[predlabel+"_cit%i" % (citi)] - cat[predlabel+"_cit%i_prebias" % (citi)]
					
					# And we clip, to the authorized region
					#minlabel = np.ma.min(cat[label])
					#maxlabel = np.ma.max(cat[label])
					#print minlabel, maxlabel
					#cat[predlabel+"_cit%i" % (citi+1)] = np.clip(cat[predlabel+"_cit%i" % (citi+1)], minlabel, maxlabel)
				
					# the error of the latter:
					cat[predlabel+"_cit%i_err" % (citi+1)] = cat[predlabel+"_cit%i" % (citi+1)] - cat[label]
			
				groupcols.append(predlabel+"_cit%i_err" % (citi+1))
				
				plotpath = os.path.join(workbasedir, "%s_%s_cit%i_onpredavg.png" % (mlparams.name, label, citi))
				#biasplot_predavg(cats, avgcat, label, predlabel, citi, filepath=plotpath)
				biasplot_predavg(cats, avgcat, label, predlabel, citi, filepath=None)
		
		# End of the loop. groupcols is defined for the next iteration. 






	
import matplotlib.pyplot as plt

def biasplot_truth(cats, avgcat, label, predlabel, citi, filepath=None):
	flabel = plot.feature.Feature(label) # avgcat and cats
	fbias = plot.feature.Feature(predlabel + "_cit%i_err_mean" % (citi), -1.0, 1.0) # avgcat
	fbiaslearn = plot.feature.Feature(predlabel + "_cit%i_prebias" % (citi), -1.0, 1.0) # avgcat
	fpredlabel = plot.feature.Feature(predlabel + "_cit%i" % (citi)) # cats
	fpredlabelerr = plot.feature.Feature(predlabel + "_cit%i_err" % (citi)) # cats
	
	
	fig = plt.figure(figsize=(12, 10))
	
	ax = fig.add_subplot(2, 2, 1)
	plot.scatter.scatter(ax, avgcat, flabel, fbias, ms=3, text="Errors averaged over realizations")
	ax.axhline(0.0, color="black")
	plot.scatter.scatter(ax, avgcat, flabel, fbiaslearn, color="green", ms=2)
	ytext = fbias.colname # "Bias(%s) at iteration %i" % (predlabel, citi)
	ax.set_ylabel(ytext)
	
	ax = fig.add_subplot(2, 2, 2)
	plot.scatter.scatter(ax, cats[0], flabel, fpredlabel, ms=3, text="Single realization", show_id_line=True, idlinekwargs={"lw":2, "color":"red"}, metrics=True)
	
	ax = fig.add_subplot(2, 2, 3)
	plot.scatter.scatter(ax, cats[0], fpredlabel, fpredlabelerr, ms=3, text="Errors on single realization")
	ax.axhline(0.0, color="black")
		
	ax = fig.add_subplot(2, 2, 4)
	plot.hist.hist(ax, cats[0], flabel, label=flabel.colname, text="Single realization")
	plot.hist.hist(ax, cats[0], fpredlabel, color="red", label=fpredlabel.colname)
	ax.set_ylabel(flabel.colname)
	ax.legend()
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()


def biasplot_predavg(cats, avgcat, label, predlabel, citi, filepath=None):
	flabel = plot.feature.Feature(label)
	ferrmean = plot.feature.Feature(predlabel + "_cit%i_err_mean" % (citi), -1.0, 1.0)
	fbiaslearn = plot.feature.Feature(predlabel + "_cit%i_prebias" % (citi), -1.0, 1.0)
	fpredlabel = plot.feature.Feature(predlabel + "_cit%i" % (citi))
	fpredlabelerr = plot.feature.Feature(predlabel + "_cit%i_err" % (citi))
	
	
	fig = plt.figure(figsize=(18, 10))
	
	ax = fig.add_subplot(2, 3, 1)
	plot.scatter.scatter(ax, avgcat, flabel, ferrmean, ms=3)
	ax.axhline(0.0, color="black")
	plot.scatter.scatter(ax, avgcat, flabel, fbiaslearn, color="green", ms=2)
	ax.set_ylabel(ferrmean.colname)
	
	
	ax = fig.add_subplot(2, 3, 2)
	plot.scatter.scatter(ax, cats[0], flabel, fpredlabel, ms=3, show_id_line=True, idlinekwargs={"lw":2, "color":"red"}, metrics=True)
	
	ax = fig.add_subplot(2, 3, 3)
	plot.scatter.scatter(ax, cats[0], fpredlabel, fpredlabelerr, ms=3)
	ax.axhline(0.0, color="black")
		
	ax = fig.add_subplot(2, 3, 4)
	plot.hist.hist(ax, cats[0], flabel, label=flabel.colname, text="Single realization")
	plot.hist.hist(ax, cats[0], fpredlabel, color="red", label=fpredlabel.colname)
	ax.set_ylabel(flabel.colname)
	ax.legend()
	
	
	ax = fig.add_subplot(2, 3, 5)
	plot.scatter.scatter(ax, avgcat, fpredlabel, ferrmean, ms=3)
	plot.scatter.scatter(ax, avgcat, fpredlabel, fbiaslearn, color="green", ms=3)
	ax.set_ylabel(ferrmean.colname)
	
	
	ax = fig.add_subplot(2, 3, 6)
	plot.scatter.scatter(ax, avgcat, fbiaslearn, fpredlabelerr, ms=3)
	
	
	
	
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()



def biasplot_pred(cat, label, predlabel, citi, filepath=None):
	flabel = plot.feature.Feature(label) # avgcat and cats
	fbias = plot.feature.Feature(predlabel + "_cit%i_err" % (citi), -1.0, 1.0)
	fbiaslearn = plot.feature.Feature(predlabel + "_cit%i_prebias" % (citi), -1.0, 1.0)
	fpredlabel = plot.feature.Feature(predlabel + "_cit%i" % (citi))
	fpredlabelerr = plot.feature.Feature(predlabel + "_cit%i_err" % (citi))
	
	
	fig = plt.figure(figsize=(12, 10))
	
	ax = fig.add_subplot(2, 2, 1)
	plot.scatter.scatter(ax, cat, flabel, fbias, ms=3)
	ax.axhline(0.0, color="black")
	
	ax = fig.add_subplot(2, 2, 2)
	plot.scatter.scatter(ax, cat, flabel, fpredlabel, ms=3, show_id_line=True, idlinekwargs={"lw":2, "color":"red"}, metrics=True)
	
	ax = fig.add_subplot(2, 2, 3)
	plot.scatter.scatter(ax, cat, fpredlabel, fpredlabelerr, ms=3)
	plot.scatter.scatter(ax, cat, fpredlabel, fbiaslearn, color="green", ms=2)
	ax.axhline(0.0, color="black")
		
	ax = fig.add_subplot(2, 2, 4)
	plot.hist.hist(ax, cat, flabel, label=flabel.colname)
	plot.hist.hist(ax, cat, fpredlabel, color="red", label=fpredlabel.colname)
	ax.set_ylabel(flabel.colname)
	ax.legend()
	
	
	plt.tight_layout()
	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()

