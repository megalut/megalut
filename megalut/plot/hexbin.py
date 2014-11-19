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



def hexbin(ax, cat, featx, featy, featc=None, makecolorbar=True, cblabel="Counts", title=None, text=None, **kwargs):
	"""
	Plots hexbin tiles on the axes.
	
	By default, if featc is None, the tile colors represent number counts,
	thus making it a 2-D histogram.
	If you pass a featc, note that you can also specify, via the kwarg reduce_C_function,
	what statistic to compute in each tile.
	
	:param ax: a matplotlib.axes.Axes object
	:param cat: an astropy table 
	:param featx: a Feature object telling what to draw on the x axis
	:param featy: idem for y
	:param featc: a Feature to use for the tile colormap.
	:param makecolorbar: set to False to avoid making the colorbar.
		This can be useful in particular when you want to overplot something else on the same axes.
	:param cblabel: what to write as label for the colorbar if featc is not specified.
		You might want to use "log(counts)" if usign the kwarg bins="log"
	:param title: the title to place on top of the axis.
	:param text: some text to be written in the figure (top left corner)
		As we frequently want to do this, here is a simple way to do it.
		For more complicated things, add the text yourself to the axes.
	
	Commonly used kwargs:
	
	- cmap = "Blues" # add "_r" to reverse...
	- reduce_C_function = np.mean
		
	More info at http://matplotlib.org/api/axes_api.html?highlight=hexbin#matplotlib.axes.Axes.hexbin
	
	How to select good colormaps: http://matplotlib.org/users/colormaps.html
	"""
	
	logger.debug("Preparing hexbin of %i points" % (len(cat))) # Log it as this might be slow or crash.
	
	xdata = cat[featx.colname]
	ydata = cat[featy.colname]
	
	if featx.low is not None and featx.high is not None and featy.low is not None and featy.high is not None: 
		extent = (featx.low, featx.high, featy.low, featy.high) # xmin xmax ymin ymax
	else:
		extent = None
	
	# Some good default values:
	mykwargs = {"gridsize":30, "cmap":"gist_heat_r", "extent":extent}
	
	# We overwrite these mykwargs with any user-specified kwargs:
	mykwargs.update(kwargs)
	
	if featc == None: # We use number counts to determine color
		cbstuff = ax.hexbin(xdata, ydata, **mykwargs)
		
	else: # We use featc to extract data
		cdata = cat[featc.colname]
		cbstuff = ax.hexbin(xdata, ydata, C=cdata, vmin=featc.low, vmax=featc.high,  **mykwargs)
		
	if makecolorbar:
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", "5%", pad="3%")	
		cb = plt.colorbar(cbstuff, cax)
	
		if featc == None:
			cb.set_label(cblabel)
		else:
			cb.set_label(featc.nicename)

	# The usual axes limit setting :
	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)
	# And the minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))

	# Writing any text:
	if text:
		ax.annotate(text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
	if title:
		ax.set_title(title)

