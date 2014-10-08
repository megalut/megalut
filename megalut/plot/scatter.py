"""
This module contains scatter plots :)
"""

import logging
logger = logging.getLogger(__name__)



def scatter2d(ax, cat, featx, featy, **kwargs):
	"""
	Simple 2D scatter plot of one feature against another, for a single catalog.
	
	:param ax: a matplotlib.axes.Axes object
	:param cat: an astropy table 
	:param featx: a Feature object telling me what to draw on my x axis
	:param featy: idem for y
	
	Any further kwargs are passed to plot().
	Some commonly used kwargs:
	
	* **marker**: default is ".", you can switch to single pixel (",") or anythign else...
	* **ms**: marker size in points
	* **color**: e.g. "red"
	* **label**: for the legend
	
	"""
	
	if cat.masked is True:
		logger.warning("Input catalog is masked, some points might not be shown !")
	
	xdata = cat[featx.colname].data
	ydata = cat[featy.colname].data
	
	assert len(xdata) == len(ydata)
	logger.info("%i datapoints to plot on (%s, %s)" % (len(xdata), featx.colname, featy.colname))
	
	plotkwargs = {"marker":".", "ms":5, "color":"red", "ls":"None", "mec":"None"}
	plotkwargs.update(kwargs)
	
	ax.plot(xdata, ydata, **plotkwargs)
	# The rendering of plot is much faster than the rendering of scatter.
	# So use plot if possible.
	
	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)



def simobs_scatter2d(ax, simcat, obscat, featx, featy, **kwargs):
	"""
	A scatter2d overplotting simulations and observations in two different colors.
	
	:param ax: a matplotlib Axes object
	:param simcat: simulation catalog
	:param obscat: observation catalog
	:param featx: a Feature object telling me what to draw on my x axis
	:param featy: idem for y
	
	All further kwargs are directly passed to scatter2d.
	
	
	"""
	scatter2d(ax, simcat, featx, featy, color="red", label="Simulations", **kwargs)
	scatter2d(ax, obscat, featx, featy, color="green", label="Observations", **kwargs)
	ax.legend()

