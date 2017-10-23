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

from scipy.optimize import curve_fit

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
	
def linregress_with_errors(x, y, y_err):
    """
	Test for comparision, GSL's gsl_fit_wlinear function
	"""
    
    y_weights = y_err**-2
    total_weight = y_weights.sum()
    
    x_weighted_mean = np.average(x,weights=y_weights)
    y_weighted_mean = np.average(y,weights=y_weights)
    
    dx = x-x_weighted_mean
    dy = y-y_weighted_mean
    
    dx2_weighted_mean = np.average(dx**2,weights=y_weights)
    dxdy_weighted_mean = np.average(dx*dy,weights=y_weights)
    
    slope = dxdy_weighted_mean / dx2_weighted_mean
    intercept = y_weighted_mean - x_weighted_mean*slope
    
    slope_err = np.sqrt(1./(total_weight*dx2_weighted_mean))
    intercept_err = np.sqrt((1.0 + x_weighted_mean**2 / dx2_weighted_mean) / total_weight)
    slope_intercept_covar = -x_weighted_mean / (total_weight*dx2_weighted_mean)

    return slope, intercept, slope_err, intercept_err, slope_intercept_covar


def wmetrics(cat, trufeat, predfeat, wfeat=None):
	"""
	An attempt to get metrics with errors when one has weights, *without* first "bining" things.
	Warning, this is experimental, not yet fully tested.
	
	Note that the scale of weights matters for the errors!
	Provide weights corresponding to 1/sigma**2
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
	

	y_err = np.sqrt(1.0/np.clip(w, 1e-18, 1e18)) # We don't want weights of exactly zero here.
	
	########### GSL
	(slope, intercept, slope_err, intercept_err, slope_intercept_covar) = linregress_with_errors(x, y, y_err)
	txt = "m*1e3: %.1f +/- %.1f   c*1e3: %.1f +/- %.1f" % ((slope-1.0)*1000.0, slope_err*1000.0, intercept*1000.0, intercept_err*1000.0)
	logger.info("GSL regression: {}".format(txt))	
	

	########### Scipy
	def f(x, a, b):
		return a * x + b

	p0 = [0, 0] # initial parameter estimate
	popt, pcov = curve_fit(f, x, y, p0, y_err, absolute_sigma=True)
	perr = np.sqrt(np.diag(pcov))
	txt = "m*1e3: %.1f +/- %.1f   c*1e3: %.1f +/- %.1f" % ((popt[0]-1.0)*1000.0, perr[0]*1000.0, popt[1]*1000.0, perr[1]*1000.0)
	logger.info("Scipy regression: {}".format(txt))	
	
	
	########### statsmodels
	X = sm.add_constant(x)
	#model = sm.OLS(y, X)
	model = sm.WLS(y, X, weights=1.0/(y_err**2)) # Yes, this "w" should be proportional to the inverse of the variance
	
	results = model.fit(cov_type='fixed scale')
	print(results.summary())
	
	print('Parameters: ', results.params)
	print('Standard errors: ', results.bse)
	
	c = results.params[0]
	m = results.params[1] - 1.0
	cerr = results.bse[0]
	merr = results.bse[1]
	ret = {"m":m, "c":c, "merr":merr, "cerr":cerr}
	
	txt = "m*1e3: %.1f +/- %.1f   c*1e3: %.1f +/- %.1f" % (m*1000.0, merr*1000.0, c*1000.0, cerr*1000.0)
	logger.info("StatsModels Regression: {}".format(txt))	
	
	return ret
	
	
	
	
	
	
