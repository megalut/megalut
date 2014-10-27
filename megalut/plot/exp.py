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



def colorscatter(ax, cat, featx, featy, featc=None, invertc=False, showdiag=False, sidehists=False, sidehistkwargs=None, **kwargs):
	"""
	A scatter plot with a colorbar
	"""

	xdata = cat[featx.colname]
	ydata = cat[featy.colname]
	
	if featc is not None:
		cdata = cat[featc.colname]
	
	if invertc:
		cmap = matplotlib.cm.get_cmap('jet_r')
	else:
		cmap = matplotlib.cm.get_cmap('jet')

	if featc is not None: # Then we prepare to use scatter, with a colorbar
		mykwargs = {"marker":"o", "lw":0, "s":15, "cmap":cmap, "vmin":featc.low, "vmax":featc.high}
	else: # we will just use plot
		mykwargs = {"marker":".", "ms":5, "color":"black", "ls":"None", "mec":"None", "alpha":0.3}
	
	mykwargs.update(kwargs)

	if featc is not None:
		stuff = ax.scatter(xdata, ydata, c=cdata, **mykwargs)
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", "5%", pad="3%")
		cax = plt.colorbar(stuff, cax)
		cax.set_label(featc.nicename)
	
	else:
		ax.plot(xdata, ydata, **mykwargs)

	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	if showdiag:
		ax.plot([-1000.0, 1000.0], [-1000.0, 1000.0], color="gray", lw=1)


	if sidehists:
		mysidehistkwargs = {"histtype":"stepfilled", "bins":100, "ec":"none", "color":"gray"}
		if sidehistkwargs is None:
			sidehistkwargs = {}
		mysidehistkwargs.update(sidehistkwargs)
		
		
		divider = make_axes_locatable(ax)
		axhistx = divider.append_axes("top", 1.0, pad=0.1, sharex=ax)
		axhisty = divider.append_axes("right", 1.0, pad=0.1, sharey=ax)
		
		axhistx.hist(xdata, **mysidehistkwargs)
		axhisty.hist(ydata, orientation='horizontal', **mysidehistkwargs)
		
		# Hiding the ticklabels
		for tl in axhistx.get_xticklabels():
			tl.set_visible(False)
		for tl in axhisty.get_yticklabels():
			tl.set_visible(False)
		
		# Reducing the number of major ticks...
		axhistx.yaxis.set_major_locator(MaxNLocator(nbins = 2))
		axhisty.xaxis.set_major_locator(MaxNLocator(nbins = 2))
		# Or hide them completely
		axhistx.yaxis.set_ticks([]) # or set_ticklabels([])
		axhisty.xaxis.set_ticks([])
		
			
		
	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)

