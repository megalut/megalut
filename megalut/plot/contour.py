"""
Helper functions to create contour-like plots from an astropy table and Feature objects.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LinearSegmentedColormap, colorConverter
from matplotlib.ticker import ScalarFormatter


from .. import tools

import astropy

import logging
logger = logging.getLogger(__name__)



def _contour(ax, x, y, color="black", bins=10, minline=0.5, maxline=4.0, nlines=3, **kwargs):
    """
    Note that this accepts numpy arrays, not a catalog and features.
    Write a contour wrapper that accepts same input as the others!
    """
    
    range = [[x.min(), x.max()], [y.min(), y.max()]]
    
    # Choose the default "sigma" contour levels.
    levels = 1.0 - np.exp(-0.5 * np.linspace(minline, maxline, nlines) ** 2)

    H, X, Y = np.histogram2d(x.flatten(), y.flatten(), bins=bins, range=range)

    #from scipy.ndimage import gaussian_filter
    #if smooth is not None:
    #    if gaussian_filter is None:
    #        raise ImportError("Please install scipy for smoothing")
    #    H = gaussian_filter(H, smooth)

    # Compute the density levels.
    Hflat = H.flatten()
    inds = np.argsort(Hflat)[::-1]
    Hflat = Hflat[inds]
    sm = np.cumsum(Hflat)
    sm /= sm[-1]
    V = np.empty(len(levels))
    for i, v0 in enumerate(levels):
        try:
            V[i] = Hflat[sm <= v0][-1]
        except:
            V[i] = Hflat[0]

    # Compute the bin centers.
    X1, Y1 = 0.5 * (X[1:] + X[:-1]), 0.5 * (Y[1:] + Y[:-1])

    # Extend the array for the sake of the contours at the plot edges.
    H2 = H.min() + np.zeros((H.shape[0] + 4, H.shape[1] + 4))
    H2[2:-2, 2:-2] = H
    H2[2:-2, 1] = H[:, 0]
    H2[2:-2, -2] = H[:, -1]
    H2[1, 2:-2] = H[0]
    H2[-2, 2:-2] = H[-1]
    H2[1, 1] = H[0, 0]
    H2[1, -2] = H[0, -1]
    H2[-2, 1] = H[-1, 0]
    H2[-2, -2] = H[-1, -1]
    X2 = np.concatenate([
        X1[0] + np.array([-2, -1]) * np.diff(X1[:2]),
        X1,
        X1[-1] + np.array([1, 2]) * np.diff(X1[-2:]),
    ])
    Y2 = np.concatenate([
        Y1[0] + np.array([-2, -1]) * np.diff(Y1[:2]),
        Y1,
        Y1[-1] + np.array([1, 2]) * np.diff(Y1[-2:]),
    ])

    # Plot the contours
    ax.contour(X2, Y2, H2.T, V, colors=color, **kwargs)


def simobs(ax, simcat, obscat, featx, featy, sidehists=True, sidehistkwargs=None, title=None, legend=False, plotpoints=True, **kwargs):
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
	
	All further **kwargs** are passed to contour() to make the contours.
		
	"""
	
	# Could we warn the user in case it seems that the catalogs are inverted ?
	# (not implemented -- maybe by detecting the precens of some typical "sim" fields in the obscat ?)
	
	simdata = tools.feature.get1Ddata(simcat, [featx, featy], keepmasked=False)
	obsdata = tools.feature.get1Ddata(obscat, [featx, featy] , keepmasked=False)

	# The data points:
	if plotpoints:
		rasterized = True
		simcolor_points = '#FF7777'
		obscolor_points = '#7777FF'
		plotkwargs = {"marker":".", "ms":5, "ls":"None", "alpha":0.2, "rasterized":rasterized}
		ax.plot(simdata[featx.colname], simdata[featy.colname], color=simcolor_points, **plotkwargs)
		ax.plot(obsdata[featx.colname], obsdata[featy.colname], color=obscolor_points, **plotkwargs)
	
	# And the contours:
	contourkwargs = {"bins":50, "minline":0.5, "maxline":4.0, "nlines":8, "zorder":100}
	contourkwargs.update(kwargs)
	_contour(ax, simdata[featx.colname], simdata[featy.colname], color="red", **contourkwargs)
	_contour(ax, obsdata[featx.colname], obsdata[featy.colname], color="blue", **contourkwargs)
	
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
		
		
		axhistx.hist(simdata[featx.colname], color="red", ec="red", **mysidehistxkwargs)
		axhistx.hist(obsdata[featx.colname], color="blue", ec="blue", **mysidehistxkwargs)
		
		
		axhisty.hist(simdata[featy.colname], color="red", ec="red", orientation='horizontal', **mysidehistykwargs)
		axhisty.hist(obsdata[featy.colname], color="blue", ec="blue", orientation='horizontal', **mysidehistykwargs)
		
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
	
	
	
	
