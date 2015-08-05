"""
Modules for metrics computations, using astropy tables as input.
"""
import numpy as np

import calc
import table
import feature

import logging
logger = logging.getLogger(__name__)


def metrics(catalog, labelfeature, predlabelfeature):
	"""
	Returns a dict with some simple standard metrics compareing a "label"-column (truth) to the corresponding predictions.
	This function explicitly takes care of masked columns, only unmasked data will be used and also handles 2D columns,
	via the fact that Feature objects have to be given.
	
	:param catalog: an astropy table containing both label and predlabel. It can be masked.
	:param labelfeature: Feature object describing the label
	:param predlabelfeature: idem for predlabel (set Feature.rea as you feel appropriate, if 2D)
	
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
	
	assert lab.ndim == 1
	assert pre.ndim == 1
	
	# And we prepare the return dict:
	ret = {"predfrac":float(len(metcat))/float(len(catalog))}
	
	ret["rmsd"] = calc.rmsd(lab, pre)
	ret.update(calc.linreg(lab, pre))
	
	return ret
	
