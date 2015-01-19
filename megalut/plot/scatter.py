"""
Helper functions to create scatter-like plots from an astropy table and Feature objects.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D

from .. import tools


import logging
logger = logging.getLogger(__name__)


def getdata(cat, featx, featy, featc=None):
	"""
	Prepares the data to be plotted, given a catalog and two features.
	In a world without masked columns, this would be rather trivial.
	But when some of the data is masked, we have to properly "combine" the masks from the different
	features to select only those rows for which every feature is available.
	That's what this function does.
	It also extracts the errorbars, if available.
	Importantly, we log a bit about the masked points that we remove.
	
	:param cat: an astropy table
	:param featx: a Feature object describing what should be drawn on the x axis
	:param featy: idem for y
	:param featc: idem for an optional color feature
	
	The function returns a dict with fields x, y, xerr, yerr, and c, each containing a column (aka numpy array) of the same size.
	
	"""
	# Potentially, 5 masks can exist:	
	colnames = [featx.colname, featy.colname, featx.errcolname, featy.errcolname]
	if featc != None:
		colnames.append(featc.colname)
	
	# Remove None (i.e., undefined errcolnames):
	colnames = filter(lambda x: x != None, colnames)
	
	# We first build one combined mask.
	masks = np.column_stack([np.array(np.ma.getmaskarray(np.ma.array(cat[colname])), dtype=bool) for colname in colnames])
	combimask = np.logical_not(np.sum(masks, axis=1).astype(bool)) # So "True" means "keep this".
	assert combimask.size == len(cat)
	ngood = np.sum(combimask)
	nbad = combimask.size - ngood
		
	logger.info("'%s' vs '%s': %i out of %i (%.2f %%) rows have masked values which will be disregarded" \
		% (featy.nicename, featx.nicename, nbad, combimask.size, 100.0 * float(nbad) / float(combimask.size)))
	
	# We disregard the masked rows:
	nomaskcat = cat[combimask]
	assert len(nomaskcat) == ngood
	
	# And get the data:
	x = nomaskcat[featx.colname]
	y = nomaskcat[featy.colname]
	
	assert len(x) == ngood
	assert len(y) == ngood
	assert np.all(np.logical_not(x.mask)) == True
	assert np.all(np.logical_not(y.mask)) == True
	
	xerr = None
	yerr = None	
	if featx.errcolname != None:
		xerr = nomaskcat[featx.errcolname]
		assert len(xerr) == ngood
	if featy.errcolname != None:
		yerr = nomaskcat[featy.errcolname]
		assert len(yerr) == ngood
	
	c = None
	if featc != None:
		c = nomaskcat[featc.colname]
	
	return {"x":x, "y":y, "xerr":xerr, "yerr":yerr, "c":c}

	



def scatter(ax, cat, featx, featy, featc=None, cmap="jet", title=None, text=None, show_id_line=False, idlinekwargs=None,
	metrics=False, sidehists=False, sidehistkwargs=None, errorbarkwargs=None, **kwargs):
	"""
	A simple scatter plot of cat, between two Features. A third Feature, featc, gives an optional colorbar.
	
	.. note:: If you specify this ``featc``, this function uses matplotlib's ``scatter()``. Otherwise, the function uses ``plot()``, as
		plot is much faster for large numbers of points! The possible ``**kwargs`` change accordingly!

	:param ax: a matplotlib.axes.Axes object
	:param cat: an astropy table 
	:param featx: a Feature object telling me what to draw on my x axis
	:param featy: idem for y
	:param featc: a Feature to use for the colorbar, decides if plot() or scatter() is used.
	:param cmap: the color bar to use. For a scatter plot one usually wants to see every point, avoid white!
	:param title: the title to place on top of the axis.
		The reason why we do not leave this to the user is that the placement changes when sidehists is True.
	:param text: some text to be written in the figure (top left corner)
		As we frequently want to do this, here is a simple way to do it.
		For more complicated things, add the text yourself to the axes.
	:param show_id_line: draws an "identity" diagonal line
	:param idlinekwargs: a dict of kwargs that will be passed to plot() to draw the idline
	:param metrics: if True, assumes that featx is a label ("tru") and featy is the corresponding predlabel ("pre"), and
		writes the RMSD and other metrics on the plot.
	:param sidehists: adds projection histograms on the top and the left (not nicely compatible with the colorbar)
		The range of these hists are limited by your features limits. Bins outside your limits are not computed!
	:param sidehistkwargs: a dict of keyword arguments to be passed to these histograms.
		Add range=None to these if you want all bins to be computed.
	:param errorbarkwargs: a dict of keywords to be passed to errorbar()
	
	Any further kwargs are either passed to ``plot()`` (if no featc is given) or to ``scatter()``.
	
	Some commonly used kwargs for plot() are:
	
	* **marker**: default is ".", you can switch to single pixel (",") or anything else...
	* **ms**: marker size in points
	* **color**: e.g. "red"
	* **label**: for the legend

	Some commonly used kwargs for scatter() are:
	
	* **s**: marker size
	* **label**: for the legend

	By default plots will be rasterized if the catalog has more than 5000 entries. To overwrite,
	just pass rasterized = True or False as kwarg.

	"""
	
	# Some initial settings:
	if sidehistkwargs is None:
		sidehistkwargs = {}
	if errorbarkwargs is None:
		errorbarkwargs = {}
	
	if len(cat) > 5000: # We rasterize plot() and scatter(), to avoid millions of vector points.
		logger.info("Plot will be rasterized, use kwarg rasterized=False if you want to avoid this")
		rasterized = True
	else:
		rasterized = False
	
	# Getting the data (without masked points):
	data = getdata(cat, featx, featy, featc)		
		
	# And now, two options:
	if featc is not None: # We will use scatter(), to have a colorbar
		
		logger.info("Preparing scatter plot of %i points with colorbar" % (len(data["x"]))) # Log it as this might be slow
		
		# We prepare to use scatter, with a colorbar
		cmap = matplotlib.cm.get_cmap(cmap)
		mykwargs = {"marker":"o", "lw":0, "s":15, "cmap":cmap, "vmin":featc.low, "vmax":featc.high, "rasterized":rasterized}
		
		# We overwrite these mykwargs with any user-specified kwargs:
		mykwargs.update(kwargs)
		
		# And make the plot:
		
		if featx.errcolname != None or featy.errcolname != None:
			myerrorbarkwargs = {"fmt":"none", "capthick":0, "ecolor":"gray", "zorder":-100, "rasterized":rasterized}
			myerrorbarkwargs.update(errorbarkwargs)
			ax.errorbar(data["x"], data["y"], xerr=data["xerr"], yerr=data["yerr"], **myerrorbarkwargs)
		
		stuff = ax.scatter(data["x"], data["y"], c=data["c"], **mykwargs)
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", "5%", pad="3%")
		cax = plt.colorbar(stuff, cax)
		cax.set_label(featc.nicename)
	
			
	else: # We will use plot()
	
		logger.info("Preparing plain plot of %i points without colorbar" % (len(data["x"])))
		mykwargs = {"marker":".", "ms":5, "color":"black", "ls":"None", "alpha":0.3, "rasterized":rasterized}
	
		# We overwrite these mykwargs with any user-specified kwargs:
		mykwargs.update(kwargs)
		
		# And we also prepare any errorbarkwargs
		myerrorbarkwargs = {"capthick":0, "zorder":-100, "rasterized":rasterized} # Different from the defaults for scatter() !
		myerrorbarkwargs.update(errorbarkwargs)
		
		# And now the actual plot:
		if featx.errcolname == None and featy.errcolname == None:
			# Plain plot:
			ax.plot(data["x"], data["y"], **mykwargs)
		else:
			mykwargs.update(myerrorbarkwargs)
			ax.errorbar(data["x"], data["y"], xerr=data["xerr"], yerr=data["yerr"], **mykwargs)
		
	
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	if sidehists:
		
		# By default, we want to limit the "binning" of the actual histograms (not just their display) to the specified ranges.
		# However, this needs some special treatment for the case when the "low" or "high" are set to None.
		if featx.low is not None and featx.high is not None: 
			histxrange = (featx.low, featx.high)
		else:
			histxrange = None
		if featy.low is not None and featy.high is not None: 
			histyrange = (featy.low, featy.high)
		else:
			histyrange = None
		# If you do not like this behaviour, simply set the sidehistkwarg "range" to None !
		
		
		# Same as for kwargs: we first define some defaults, and then update these defaults:
		
		mysidehistxkwargs = {"histtype":"stepfilled", "bins":100, "ec":"none", "color":"gray", "range":histxrange}
		mysidehistxkwargs.update(sidehistkwargs)
		mysidehistykwargs = {"histtype":"stepfilled", "bins":100, "ec":"none", "color":"gray", "range":histyrange}
		mysidehistykwargs.update(sidehistkwargs)
		
		# We prepare the axes for the hists:
		divider = make_axes_locatable(ax)
		axhistx = divider.append_axes("top", 1.0, pad=0.1, sharex=ax)
		axhisty = divider.append_axes("right", 1.0, pad=0.1, sharey=ax)
		
		# And draw the histograms		
		axhistx.hist(data["x"], **mysidehistxkwargs)
		axhisty.hist(data["y"], orientation='horizontal', **mysidehistykwargs)
		
		# Hiding the ticklabels
		for tl in axhistx.get_xticklabels():
			tl.set_visible(False)
		for tl in axhisty.get_yticklabels():
			tl.set_visible(False)
		
		# Reducing the number of major ticks...
		#axhistx.yaxis.set_major_locator(MaxNLocator(nbins = 2))
		#axhisty.xaxis.set_major_locator(MaxNLocator(nbins = 2))
		# Or hide them completely
		axhistx.yaxis.set_ticks([]) # or set_ticklabels([])
		axhisty.xaxis.set_ticks([])
	
		if title:
			axhistx.set_title(title)
		
	else:
		if title:
			ax.set_title(title)
	
	if show_id_line: # Show the "diagonal" identity line
	
		# It would be nice to get this working with less code
		# (usign get_lims and axes transforms, for instance)
		# But in the meantime this seems to work fine.
		# It has to be so complicated to keep the automatic ranges working if low and high are None !
		
		# For "low":
		if featx.low is None or featy.low is None: # We use the data...
			minid = max(np.min(data["x"]), np.min(data["y"]))
		else:
			minid = max(featx.low, featy.low)
		# Same for "high":
		if featx.high is None or featy.high is None: # We use the data...
			maxid = min(np.max(data["x"]), np.max(data["y"]))
		else:
			maxid = min(featx.high, featy.high)
			
		if idlinekwargs == None:
			idlinekwargs = {}
		myidlinekwargs = {"ls":"--", "color":"gray", "lw":1}
		myidlinekwargs.update(idlinekwargs)	
		
		# And we plot the line:
		ax.plot((minid, maxid), (minid, maxid), **myidlinekwargs)


	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)


	# Finally, we write the text:
	if text:
		ax.annotate(text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -8), textcoords='offset points', ha='left', va='top')
	
	if metrics:
	
		metrics_label = featx.colname
		metrics_predlabel = featy.colname
		metrics = tools.metrics.metrics(cat, metrics_label, metrics_predlabel)
	
		metrics_text = "predfrac: %.3f\nRMSD: %.3f\nm*1e3: %.1f +/- %.1f" % (metrics["predfrac"], metrics["rmsd"], metrics["m"]*1000.0, metrics["merr"]*1000.0)
		ax.annotate(metrics_text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top')
	
		



def simobs(ax, simcat, obscat, featx, featy, sidehists=True, sidehistkwargs=None, title=None, legend=False, **kwargs):
	"""
	A scatter plot overplotting simulations (in red) and observations (in blue, like the sky).
	Previously the observations were green (like nature), but blue is better for most colorblind people.
			
	:param ax: a matplotlib Axes object
	:param simcat: simulation catalog
	:param obscat: observation catalog
	:param featx: a Feature object telling me what to draw on my x axis
	:param featy: idem for y
	:param sidehists: set this to False if you don't want side histograms
	:param sidehistkwargs: keyword arguments passed to the side hists
	:param title: the title to place on top of the axis.
		The reason why we do not leave this to the user is that the placement changes when sidehists is True.
	:param legend: if True, it writes a self-styled non-invasive "legend" in the top right corner
	
	All further **kwargs** are passed to axes.plot() to make the scatter plot.
		
	"""
	
	# Could we warn the user in case it seems that the catalogs are inverted ?
	# (not implemented -- maybe by detecting the precens of some typical "sim" fields in the obscat ?)
	
	simdata = getdata(simcat, featx, featy)
	obsdata = getdata(obscat, featx, featy)
	
	
	if len(simcat) > 5000 or len(obscat) > 5000: # We rasterize plot() to avoid millions of vector points.
		logger.info("Plot will be rasterized, use kwarg rasterized=False if you want to avoid this")
		rasterized = True
	else:
		rasterized = False

	# First we use plot() to get a scatter, directly on the axes:
	plotkwargs = {"marker":".", "ms":5, "ls":"None", "alpha":0.3, "rasterized":rasterized}
	plotkwargs.update(kwargs)
	ax.plot(simdata["x"], simdata["y"], color="red", **plotkwargs)
	ax.plot(obsdata["x"], obsdata["y"], color="blue", **plotkwargs)
	
	
	# Now we build the sidehists:
	if sidehists:
	
		# By default, we want to limit the "binning" of the actual histograms (not just their display) to the specified ranges.
		# However, this fails when the "low" or "high" are set to None. Hence some explicit code:
		if featx.low is not None and featx.high is not None: 
			histxrange = (featx.low, featx.high)
		else:
			histxrange = None
		if featy.low is not None and featy.high is not None: 
			histyrange = (featy.low, featy.high)
		else:
			histyrange = None
		# If you do not like this default behaviour, you can overwrite it using the sidehistkwarg "range=None" !
	
		# We now prepare the kwargs for calling hist:
		if sidehistkwargs is None:
			sidehistkwargs = {}
		mysidehistxkwargs = {"histtype":"stepfilled", "normed":"True", "bins":100, "alpha":0.5, "range":histxrange} # for x
		mysidehistxkwargs.update(sidehistkwargs)
		mysidehistykwargs = {"histtype":"stepfilled", "normed":"True", "bins":100, "alpha":0.5, "range":histyrange} # for y
		mysidehistykwargs.update(sidehistkwargs)
	
		divider = make_axes_locatable(ax)
		axhistx = divider.append_axes("top", 1.0, pad=0.1, sharex=ax)
		axhisty = divider.append_axes("right", 1.0, pad=0.1, sharey=ax)
		
		
		axhistx.hist(simdata["x"], color="red", ec="red", **mysidehistxkwargs)
		axhistx.hist(obsdata["x"], color="blue", ec="blue", **mysidehistxkwargs)
		
		
		axhisty.hist(simdata["y"], color="red", ec="red", orientation='horizontal', **mysidehistykwargs)
		axhisty.hist(obsdata["y"], color="blue", ec="blue", orientation='horizontal', **mysidehistykwargs)
		
		# Hiding the ticklabels
		for tl in axhistx.get_xticklabels():
			tl.set_visible(False)
		for tl in axhisty.get_yticklabels():
			tl.set_visible(False)

		# Hide the hist ticks
		axhistx.yaxis.set_ticks([]) # or set_ticklabels([])
		axhisty.xaxis.set_ticks([])
	
		if title:
			axhistx.set_title(title)
		
	else:
		if title:
			ax.set_title(title)

	# We set the limits and labels:
	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)
	
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	if legend:
		ax.annotate("Simulations", color="red", xy=(1.0, 1.0), xycoords='axes fraction', xytext=(-8, -8), textcoords='offset points', ha='right', va='top')
		ax.annotate("Observations", color="blue", xy=(1.0, 1.0), xycoords='axes fraction', xytext=(-8, -24), textcoords='offset points', ha='right', va='top')
	
	
	
	
