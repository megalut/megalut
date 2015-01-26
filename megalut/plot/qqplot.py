"""
QQ-plot to easily compare the distributions

.. note:: Require scipy.stats

.. seealso:: http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.probplot.html
"""

import logging
logger = logging.getLogger(__name__)

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import megalut.tools as tools

def _compute_qqplot(cat, feat, dist):
	"""
	Computes the quantiles needed for a qq plot. The fit keyword in probplot is always set to False
	
	:param cat: an astropy table
	:param feat: a Feature object
	:param dist: Distribution or distribution function name. See scipy.stats.probplot, "norm" is normal
	
	:returns: the output of `scipy.stats.probplot`
	
	.. note:: qqplot can't handle masked table, so we convert the array to numpy and remove masked values
	"""
	
	x = cat[feat.colname]
	x = np.ma.asarray(x)
	x = np.ma.compressed(x)
	
	res = stats.probplot(x, plot=None, dist=dist, fit=False)
	
	return res

def qqplot(ax, cat, feat, dist='norm', **kwargs):
	"""
	Draws a qqplot for a dataset and a distribution$
	
	:param ax: a matplotlib.axes.Axes object
	:param cat: an astropy table
	:param feat: a Feature object
	:param dist: Distribution or distribution function name. See scipy.stats.probplot, "norm" is normal
	
	:returns: the output of `scipy.stats.probplot`
	
	.. note:: qqplot can't handle masked table, so we convert the array to numpy and remove masked values
	
	Any further kwargs are either passed to ``plot()``
	"""

	mykwargs = {"marker":".", "ms":5, "color":"black", "ls":"None", "alpha":0.3}
	mykwargs.update(kwargs)
	
	res = _compute_qqplot(cat, feat, dist)
	
	xx = np.asarray(res[0])
	yy = np.asarray(res[1])

	ax.plot(xx, yy, **mykwargs)
		
	return res

def qqplot2dataset(ax, catx, caty, feat, dist='norm', **kwargs):
	"""
	Draws a qqplot for a dataset and a distribution$
	
	:param ax: a matplotlib.axes.Axes object
	:param catx: an astropy table for the quantiles on the x-axis
	:param catx: an astropy table for the quantiles on the y-axis
	:param feat: a common Feature object
	:param dist: Distribution or distribution function name. See scipy.stats.probplot, "norm" is normal
	:param title: the title to place on top of the axis.
		The reason why we do not leave this to the user is that the placement changes when sidehists is True.
	:param text: some text to be written in the figure (top left corner)
		As we frequently want to do this, here is a simple way to do it.
		For more complicated things, add the text yourself to the axes.
	
	:returns: the output of `scipy.stats.probplot`
	
	.. note:: qqplot can't handle masked table, so we convert the array to numpy and remove masked values
	
	Any further kwargs are either passed to ``plot()``
	"""
	
	mykwargs = {"marker":".", "ms":5, "color":"black", "ls":"None", "alpha":0.3}
	mykwargs.update(kwargs)
	
	res = _compute_qqplot(catx, feat, dist)
	binsx = np.asarray(res[0]) # res[0] is the theoretical quantiles
	xx = np.asarray(res[1])
	
	res = _compute_qqplot(caty, feat, dist)
	binsy = np.asarray(res[0]) # res[0] is the theoretical quantiles
	yy = np.asarray(res[1])
	
	datatoshow = []
	for by in binsy:
		ii = (np.abs(binsx-by)).argmin()
		datatoshow.append(ii)	

	ax.plot(xx[datatoshow], yy, **mykwargs)
	
	return xx[datatoshow], yy


