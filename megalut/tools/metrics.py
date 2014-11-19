"""
Modules for metrics computations, using astropy tables as input.
"""
import numpy as np

import calc

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
		
		- **predfrac**: Fraction of predlabels / labels.
			For example, 0.5 means that only half of the rows having a label value also have a predlabel value.
		- **rmsd**: the RMSD
		- **m**: multiplicative bias (slope minus one)
		- **merr**: error on multiplicative bias
		- **c**: additive bias
		- **cerr**: error on additive bias

	"""

	logger.debug("Input catalog is masked: %s" % (catalog.masked))
		
	# In any case, we convert this to masked numpy arrays:
	lab = np.ma.array(catalog[label])
	pre = np.ma.array(catalog[predlabel])
	
	# We gather some info about the mask
	ncat = len(catalog)
	nlab = np.sum(np.logical_not(lab.mask))
	npre = np.sum(np.logical_not(pre.mask))
	goodmask = np.logical_or(lab.mask, pre.mask) # Indeed, to use a point, we need both values to be unmasked.
	ngood = np.sum(np.logical_not(goodmask))
	logger.debug("ncat = %i, nlab = %i, npre = %i, ngood = %i" % (ncat, nlab, npre, ngood))


	# Now we manually take care of the masks here, and convert the data to simple non-masked arrays.
	lab = np.array(lab[np.logical_not(goodmask)])
	pre = np.array(pre[np.logical_not(goodmask)])
	assert len(lab) == ngood and len(pre) == ngood
	
	# And we prepare the return dict:
	
	ret = {"predfrac":float(npre)/float(nlab)}
	
	ret["rmsd"] = calc.rmsd(lab, pre)
	ret.update(calc.linreg(lab, pre))
	
	logger.debug("metrics: %s" % (ret))
	
	return ret
	
