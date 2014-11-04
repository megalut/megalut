"""
Experimental plots

"""

import logging
logger = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator


def hist(ax, cat, feat, **kwargs):
	"""
	A simple histogram
	"""
	
	myrange = (feat.low, feat.high)
	
	mykwargs = {"histtype":"stepfilled", "bins":100, "range":myrange, "alpha":0.5, "ec":"none", "color":"gray"}
	mykwargs.update(kwargs)

	n, bins, patches = ax.hist(cat[feat.colname], **mykwargs)
	ax.set_xlim(feat.low, feat.high)
	ax.set_xlabel(feat.nicename)



