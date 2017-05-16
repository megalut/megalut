"""
Modules for metrics computations, using astropy tables as input.
"""
import numpy as np

import calc
import table
import feature

try:
	import statsmodels.api as sm
except:
	pass

import logging
logger = logging.getLogger(__name__)


def metrics(catalog, labelfeature, predlabelfeature, pre_is_res=False):
	"""
	Returns a dict with some simple standard metrics compareing a "label"-column (truth) to the corresponding predictions.
	This function explicitly takes care of masked columns, only unmasked data will be used and also handles 2D columns,
	via the fact that Feature objects have to be given.
	
	:param catalog: an astropy table containing both label and predlabel. It can be masked.
	:param labelfeature: Feature object describing the label
	:param predlabelfeature: idem for predlabel (set Feature.rea as you feel appropriate, if 2D)
	
	:param pre_is_res: if True, predlabelfeature is interpreted as being residues, and
		labelfeature will be added to these before computing the metrics.
	
	:returns: a dict containing
		
		- **predfrac**: Fraction of rows having an unmasked predlabel
		- **rmsd**: the RMSD
		- **m**: multiplicative bias (slope minus one)
		- **merr**: error on multiplicative bias
		- **c**: additive bias
		- **cerr**: error on additive bias

	"""
	
	logger.debug("Computing metrics for label = %s and predlabel = %s" % (labelfeature.colname, predlabelfeature.colname))
	
	#features = [feature.Feature(colname=label, rea=None), feature.Feature(colname=predlabel, rea="full")]

	metcat = feature.get1Ddata(catalog, [labelfeature, predlabelfeature], keepmasked=False)
	
	lab = metcat[labelfeature.colname]
	pre = metcat[predlabelfeature.colname]
	if pre_is_res:
		pre += lab
	
	assert lab.ndim == 1
	assert pre.ndim == 1
	
	# And we prepare the return dict:
	ret = {"predfrac":float(len(metcat))/float(len(catalog))}
	
	ret["rmsd"] = calc.rmsd(lab, pre)
	ret.update(calc.linreg(lab, pre))
	
	return ret
	

def wmetrics(cat, trufeat, predfeat, wfeat=None):
	"""
	An attempt to get metrics with errors when one has weights, *without* first "bining" things.
	Warning, this is experimental, not yet fully tested.
	"""
	logger.info("Computing metrics for {} -> {}".format(predfeat.colname, trufeat.colname))
	
	if wfeat is None:
		logger.info("WARNING: not using any weights!")
		metcat = feature.get1Ddata(cat, [trufeat, predfeat], keepmasked=False)
		x = metcat[trufeat.colname]
		y = metcat[predfeat.colname]
		w = np.ones(len(x))
		
	else:
		logger.info("Using {} as weights.".format(wfeat.colname))
		metcat = feature.get1Ddata(cat, [trufeat, predfeat, wfeat], keepmasked=False)
		x = metcat[trufeat.colname]
		y = metcat[predfeat.colname]
		w = metcat[wfeat.colname]
	print x
	print y
	print w
	
	X = sm.add_constant(x)
	#model = sm.OLS(y, X)
	model = sm.WLS(y, X, w=1.0/w)
	
	results = model.fit()
	print(results.summary())
	
	print('Parameters: ', results.params)
	print('Standard errors: ', results.bse)
	
	c = results.params[0]
	m = results.params[1] - 1.0
	cerr = results.bse[0]
	merr = results.bse[1]
	ret = {"m":m, "c":c, "merr":merr, "cerr":cerr}
	
	txt = "m*1e3: %.1f +/- %.1f   c*1e3: %.1f +/- %.1f" % (m*1000.0, merr*1000.0, c*1000.0, cerr*1000.0)
	logger.info("Regression: {}".format(txt))	
	
	return ret
	
	
	
	
	
	
