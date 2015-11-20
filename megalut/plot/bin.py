"""

2D plots of predictions versus truth, but shown in bins of truth, as points with error bars.



"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D

from .. import tools

import astropy

import logging
logger = logging.getLogger(__name__)



def res(ax, cat, featx, featy, nbins=10, selector=None, title=None, showidline=True, metrics=False):
	"""
	Shows the residues featy in bins of featx.
	
	"""

	logger.info("Preparing res plot of '{}' versus '{}'".format(featy.colname, featx.colname))
	
	nall = len(cat)
	nsel = nall
	if selector:
		cat = selector.select(cat)
		nsel = len(cat)
	
	features = [featx, featy]
	data = tools.feature.get1Ddata(cat, features, keepmasked=False)
	
	# Finding the range to bin:
	if featx.low is not None and featx.high is not None: 
		binrange = (featx.low, featx.high)
	else:
		binrange = (np.min(data[featx.colname]), np.max(data[featx.colname]))

	logger.info("Binning data along '{name}' in {nbins} bins in the range {ran}...".format(name=featx.colname, nbins=nbins, ran=binrange))

	binlims = np.linspace(binrange[0], binrange[1], nbins+1)
	bincenters = 0.5 * (binlims[0:-1] + binlims[1:])
	assert len(bincenters) == nbins
	
	binindices = np.digitize(data[featx.colname], bins=binlims)
	
	inrangeindices = np.arange(nbins)+1 # the indices that are within the binlims
	assert len(inrangeindices) == nbins
	
	
	ymeans = []
	ystds = []
		
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools)
		
		if nin < 2:
			ymeans.append(np.nan)
			ystds.append(np.nan)
			continue
		
		thesexvals = data[featx.colname][inbools]
		theseyvals = data[featy.colname][inbools]
		
		#assert len(thesexvals) == nin
		#assert len(theseyvals) == nin
		
		ymeans.append(np.mean(theseyvals))
		ystds.append(np.std(theseyvals))
		
				
	#errorbarkwargs = {"capthick":0, "zorder":-100}
	errorbarkwargs = {"color":"black", "ls":"None", "marker":"."}
	
	ax.errorbar(bincenters, ymeans, yerr=ystds, **errorbarkwargs)
	
	
	if showidline: # Show the identity line
		idlinekwargs = {"ls":"--", "color":"gray", "lw":1}
		ax.plot(binrange, (0.0, 0.0), **idlinekwargs)

	if metrics:
		
		logger.info("Now computing metrics for this res plot...")
		try:
			metrics = tools.metrics.metrics(cat, featx, featy, pre_is_res=True)
			
			#metrics_text = "predfrac: %.3f\nRMSD: %.5f\nm*1e3: %.1f +/- %.1f\nc*1e3: %.1f +/- %.1f" % (metrics["predfrac"], metrics["rmsd"], metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
			metrics_text = "RMSD = %.5f\nm = %.1f +/- %.1f, c = %.1f +/- %.1f e-3" % (metrics["rmsd"], metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
			
			
			ax.annotate(metrics_text, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top')
		except:
			logger.warning("Metrics compuation failed", exc_info = True)


	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	ax.set_ylabel(featy.nicename)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_xlim(binrange)

	if selector:
		ax.set_title(selector.name)

	if title:
		ax.set_title(title)

	
