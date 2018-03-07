"""

Plot of m and c as datapoints versus bins of some feature.



"""

import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.cm
#from mpl_toolkits.axes_grid1 import make_axes_locatable
#from matplotlib.ticker import MaxNLocator
#from matplotlib.ticker import AutoMinorLocator
#from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

from .. import tools
from . import utils

import astropy

import logging
logger = logging.getLogger(__name__)




def mcbin(ax, cat, feattru, featpre, featbin, featprew=None, nbins=10, binlims=None, showbins=True, comp=0, showlegend=False, sigma_shape=0.2):
	"""
	
	feattru: the true parameter (for example tru_s1)
	featpre: the predicted point estimate (for example pre_s1)
	featbin: the feature to bin in (for example tru_g)
	featprew: the predicted weights (optional, for example pre_s1w)

	comp: 0, 1 or 2, if not 0 selects the symbol and color to use
	
	Either give nbins (to get equal-part-of-population bins) or binlims (an array of the "n+1" bin limits to use).
	
	
	"""
	
	logger.info("Plot mcbin with featbin '{}'".format(featbin.colname))
	
	if binlims is None:		
		binrange = utils.getrange(cat, featbin)
		binlims = np.array([np.percentile(cat[featbin.colname], q) for q in np.linspace(0.0, 100.0, nbins+1)])
	else:
		nbins = len(binlims) - 1
		if nbins < 1:
			raise ValueError("Provide more binlims!")
	
	binlows = binlims[0:-1]
	binhighs = binlims[1:]
	#logger.info("binlims: {}".format(binlims))
		
	binpointcenters = []
	ms = []
	merrs = []
	cs = []
	cerrs = []

	for i in range(nbins):
			
		selbin = tools.table.Selector(featbin.colname, [("in", featbin.colname, binlows[i], binhighs[i])])
		bindata = selbin.select(cat)
		
	
		# And we perform the linear regression
		# Redefining features, to get rid of any rea settings that don't apply here (?)
		
		#if featprew is None:
		#	md = tools.metrics.metrics(bindata,
		#			feattru, 
		#			featpre,
		#			pre_is_res=False)
		#else:
		md = tools.metrics.metricsw(bindata,
					feattru, 
					featpre,
					featprew,
					sigma_shape=sigma_shape
					)
			
			
			
		ms.append(md["m"])
		merrs.append(md["merr"])
		cs.append(md["c"])
		cerrs.append(md["cerr"])
			
		binpointcenters.append(np.mean(bindata[featbin.colname]))
	
			
	
	if comp is 0:
		mkwargs = {}
		ckwargs = {}
	elif comp is 1:
		mkwargs = {"marker":'s', "color":"black", "label":r"$\mu_{}$ ".format(comp)}
		ckwargs = {"marker":'*', "color":"black", "label":r"$c_{}$ ".format(comp), "ls":":"}
	elif comp is 2:
		mkwargs = {"marker":'d', "color":"red", "label":r"$\mu_{}$ ".format(comp)}
		ckwargs = {"marker":'x', "color":"red", "label":r"$c_{}$ ".format(comp), "ls":":"}
	else:
		raise ValueError("Unknown comp")
	
	
	ax.errorbar(binpointcenters, ms, yerr=merrs, **mkwargs)
	ax.errorbar(binpointcenters, cs, yerr=cerrs, **ckwargs)
		
	if showbins:
		for x in binlims:
			ax.axvline(x, color='gray', lw=0.5)
	
	if showlegend:
		#plt.legend(loc="best", handletextpad=0.07, fontsize="small", framealpha=1.0, columnspacing=0.1, ncol=2)
		plt.legend(loc="best",  handletextpad=0.2, framealpha=1.0, columnspacing=0.1, ncol=2)



def make_symlog(ax, featbin):
	"""
	Converts the y axis to a symlog scale with custom ticks, usually for the mcbin-plot from above
	"""
	
	lintresh=2e-3
	ax.set_yscale('symlog', linthreshy=lintresh)
	ax.set_ylim([-1e-1, 1e-1])
	ticks = np.concatenate([np.arange(-lintresh, lintresh, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
	s = ax.yaxis._scale
	ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
	ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
	ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
	
	
	xlim = (featbin.low, featbin.high)
	ax.fill_between(xlim, -lintresh, lintresh, alpha=0.2, facecolor='darkgrey')
	ax.set_xlim(xlim)

