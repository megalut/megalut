"""
QQ-plot to easily compare the distributions

:requires.. scipy
"""

import logging
logger = logging.getLogger(__name__)

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

def _compute_qqplot(cat, feat, dist):
	"""
	Computes the quantiles needed for a qq plot. The fit keyword in probplot is always set to False
	
	:param cat: an astropy table
	:param feat: a Feature object
	:param dist: Distribution or distribution function name. See scipy.stats.probplot, "norm" is normal
	
	:returns: the output of `scipy.stats.probplot`
	
	:notes.. qqplot can't handle masked table, so we convert the array to numpy and remove masked values
	
	More info : http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.probplot.html
	"""
	x = cat[feat.colname]
	x = np.ma.asarray(x)
	x = np.ma.compressed(x)
	
	res = stats.probplot(x, plot=None, dist=dist, fit=False)
	
	return res

def qqplot(ax, cat, feat, dist='norm', title=None, text=None, **kwargs):

	mykwargs = {"marker":".", "color":"black", "alpha":0.3, "edgecolor":"None"}
	mykwargs.update(kwargs)
	
	res = _compute_qqplot(cat, feat, dist)
	
	xx = np.asarray(res[0])
	yy = np.asarray(res[1])

	ax.scatter(xx, yy, **mykwargs)
	
	# Writing any text:
	if text:
		ax.annotate(text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
	if title:
		ax.set_title(title)
		
	return res

def qqplot2dataset(ax, catx, caty, feat, dist='norm', **kwargs):
	
	mykwargs = {"marker":".", "alpha":0.3, "edgecolor":"None"}
	mykwargs.update(kwargs)
	
	res = _compute_qqplot(catx, feat, dist)
	binsx = np.asarray(res[0]) # res[0] is the theoretical quantiles
	xx = np.asarray(res[1])
	
	res = _compute_qqplot(caty, feat, dist)
	binsy = np.asarray(res[0]) # res[0] is the theoretical quantiles
	yy = np.asarray(res[1])
	
	datatoshow = []
	for by in binsy:
		ii = find_nearest(binsx, by)
		datatoshow.append(ii)	
	
	print mykwargs
	ax.scatter(xx[datatoshow], yy, **mykwargs)


