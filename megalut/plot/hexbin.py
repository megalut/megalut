"""
2-D histogram like plots using hexagonal bins
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D



import logging
logger = logging.getLogger(__name__)



def hexbin(ax, cat, featx, featy, featc=None, cmap="jet", title=None, text=None, **kwargs):
	"""
	
	"""
	
	xdata = cat[featx.colname]
	ydata = cat[featy.colname]
	extent = (featx.low, featx.high, featy.low, featy.high) # xmin xmax ymin ymax
	
	mykwargs = {"gridsize":30, "cmap":plt.cm.Blues, "extent":extent}
	# We overwrite these mykwargs with any user-specified kwargs:
	mykwargs.update(kwargs)
	
	#stuff = ax.hexbin(xdata, ydata, C=prerrabs_g, reduce_C_function = np.mean, gridsize=gridsize, cmap=plt.cm.jet, extent = extent, vmin=0.0, vmax=0.3)
	stuff = ax.hexbin(xdata, ydata, bins="log", C=None, **mykwargs)
		
	#cb = plt.colorbar(stuff, ax = ax)
	#cb.set_label("prerrabs_g")
	#ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	#ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))

	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))


	# Finally, we write the text:
	if text:
		ax.annotate(text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
	
