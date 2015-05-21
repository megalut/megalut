"""
Modules for metrics computations, using astropy tables as input.
"""
import numpy as np

import calc
import table

import logging
logger = logging.getLogger(__name__)


def metrics(catalog, label, predlabel):
	"""
	Returns a dict with some simple standard metrics compareing a "label"-column (truth) to the corresponding predictions.
	This function explicitly takes care of masked columns, only unmasked data will be used.
	
	:param catalog: an astropy table containing both label and predlabel. It can be masked.
	:param label: column name of the label
	:param predlabel: column name of the predlabel
	
	:returns: a dict containing
		
		- **predfrac**: Fraction of rows having an unmasked predlabel
		- **rmsd**: the RMSD
		- **m**: multiplicative bias (slope minus one)
		- **merr**: error on multiplicative bias
		- **c**: additive bias
		- **cerr**: error on additive bias

	"""
	
	logger.debug("Computing metrics for label = %s and predlabel = %s" % (label, predlabel))
	
	# We get the unmasked points :
	metcat = table.cutmasked(catalog, colnames=[label, predlabel])	
	lab = metcat[label]
	pre = metcat[predlabel]
	
	# And we prepare the return dict:
	ret = {"predfrac":float(len(metcat))/float(len(catalog))}
	
	ret["rmsd"] = calc.rmsd(lab, pre)
	ret.update(calc.linreg(lab, pre))
	
	return ret
	
