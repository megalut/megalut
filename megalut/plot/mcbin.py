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




def mcbin(ax, cat, feattru, featpre, featbin, featprew=None, nbins=10, binlims=None, showbins=True, comp=0, showlegend=False, regressmethod=1, sigma_shape=0.2):
	"""
	Makes plots of mu and c bias terms evaluated in bins of some (usually true) parameter.
	
	feattru: the true parameter (for example tru_s1)
	featpre: the predicted point estimate (for example pre_s1)
	featbin: the feature to bin in (for example tru_g)
	featprew: the predicted weights (optional, for example pre_s1w)

	comp: 0, 1 or 2, if not 0 selects the symbol and color to use
	
	Either give nbins (to get equal-part-of-population bins) or binlims (an array of the "n+1" bin limits to use).
	
	About the regressmethod:
	This affects how the weights given by featprew are used: if you don't have weights, you can ignore regressmethod.
	
	regressmethod = 1 : a weighted least squares regression is performed on *all* individual realizations within a bin.
		For this, a value of sigma_shape is required to turn the weights into shear errors and give meaningful error bars.
		
	regressmethod = 2 : the weights are used to compute the weighted average true shear within each *case*, and then a non-weighted
		least square regression is performed on the true-shear vs weighted-average-shear relation.
		In this case sigma_shape is not used, as it is not required.
		A pracitcal advantage of regessmethod 2 is that it gives meaningful errors even if SNC is used within the cases.
		You want to use this if your care about all cases equally, for instance if different cases have different PSFs.
	
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
		
		if regressmethod is 1:
	
			# And we perform the linear regression
			# Redefining features, to get rid of any rea settings that don't apply here (?)
		
			if featprew is None:
				md = tools.metrics.metrics(bindata,
						feattru, 
						featpre,
						pre_is_res=False)
			else:
				md = tools.metrics.metricsw(bindata,
						feattru, 
						featpre,
						featprew,
						sigma_shape=sigma_shape
						)
		elif regressmethod is 2:
		
			# We first compute (weighted) average shear per case, for each selected case (meaningful for cases that have the same shear).
			# Then we perform a non-weighted regression to get m and c 
			# Advantage is for the weights: we don't care about sigma_shape or any SNC which modifies the shape noise
			
			
			if bindata[feattru.colname].shape[0] != len(bindata):
				raise RuntimeError("Using regressmethod 2 implies that the cases should all have the same feattru value!")
			
			tools.table.addstats(bindata, featpre.colname, wcol=featprew.colname)
			#print tools.table.info(bindata)
			
			wmeancolname = featpre.colname + "_wmean"
			featwmean = tools.feature.Feature(wmeancolname)
			
			md = tools.metrics.metrics(bindata,
						feattru, 
						featwmean,
						pre_is_res=False)
			
			
			
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



def make_symlog(ax, featbin, linthresh=2e-3, lim=1e-1):
	"""
	Converts the y axis to a symlog scale with custom ticks, usually for the mcbin-plot from above
	"""
	
	ax.set_yscale('symlog', linthreshy=linthresh)
	ax.set_ylim([-lim, lim])
	ticks = np.concatenate([np.arange(-linthresh, linthresh, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
	s = ax.yaxis._scale
	ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
	ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
	ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
	
	
	xlim = (featbin.low, featbin.high)
	ax.fill_between(xlim, -linthresh, linthresh, alpha=0.2, facecolor='darkgrey')
	ax.set_xlim(xlim)

