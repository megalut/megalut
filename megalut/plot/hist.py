"""
Histogram helper functions
"""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator


def hist(ax, cat, feat, text=None, title=None, **kwargs):
	"""
	Adds a simple histogram to the axes and sets limits and label.
	This function can be called repeatedly on the same axes to overplot several catalogs,
	or say different selections from a same catalog.
	
	:param ax: a matplotlib.axes.Axes object
	:param cat: an astropy table 
	:param feat: a Feature object that I should bin
	:param text: some text to be written in the figure (top left corner)
		As we frequently want to do this, here is a simple way to do it.
		For more complicated things, add the text yourself to the axes.
	:param title: the title to place on top of the axis.
		This is here only because scatter.scatter() has the same option.

	Any further kwargs are either passed to ``hist()``.
	"""
	
	logger.debug("Preparing hist of %i points" % (len(cat))) # Log it as this might be slow
	
	# By default, we want to limit the "binning" of the actual histogram (not just their display) to the specified range.
	# However, this fails when the "low" or "high" are set to None. Hence some explicit code:
	if feat.low is not None and feat.high is not None: 
		histrange = (feat.low, feat.high)
	else:
		histrange = None
	# If you do not like this default behaviour, you can overwrite it using the kwarg "range=None" !
	
	
	mykwargs = {"histtype":"stepfilled", "bins":100, "range":histrange, "alpha":0.5, "ec":"none", "color":"gray"}
	mykwargs.update(kwargs)

	# We call hist:
	n, bins, patches = ax.hist(cat[feat.colname], **mykwargs)
	
	# Set lim and label:
	ax.set_xlim(feat.low, feat.high)
	ax.set_xlabel(feat.nicename)
	
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))

	# The text:
	if text:
		ax.annotate(text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
	if title:
		ax.set_title(title)

