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



def res(ax, cat, featx, featy, featres=None, nbins=10, selector=None, title=None):
	"""
	Shows the residues featy-featx in bins of featx.
	
	
	:param featres: a **fake** Feature, to specify a name and range to be used in the plot.
		No data from the catalog will be extracted using this feature.
	
	"""

	logger.info("Preparing plainbin plot of '{}' versus '{}'".format(featy.colname, featx.colname))
	
	nall = len(cat)
	nsel = nall
	if selector:
		cat = selector.select(cat)
		nsel = len(cat)
	
	features = [featx, featy]
	data = tools.feature.get1Ddata(cat, features, keepmasked=False)
	residues = data[featy.colname] - data[featx.colname] # We'll plot the bias, in fact
	
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
	resmeans = []
	resstds = []
	
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools)
		
		if nin < 2:
			ymeans.append(np.nan)
			ystds.append(np.nan)
			resmeans.append(np.nan)
			resstds.append(np.nan)
			continue
		
		thesexvals = data[featx.colname][inbools]
		theseyvals = data[featy.colname][inbools]
		theseresvals = residues[inbools]
		
		#assert len(thesexvals) == nin
		#assert len(theseyvals) == nin
		#assert len(theseresvals) == nin
		
		ymeans.append(np.mean(theseyvals))
		ystds.append(np.std(theseyvals))
		resmeans.append(np.mean(theseresvals))
		resstds.append(np.std(theseresvals))
		
				
	
	#errorbarkwargs = {"capthick":0, "zorder":-100}
	errorbarkwargs = {"color":"black", "ls":"None", "marker":"."}
	
	ax.errorbar(bincenters, resmeans, yerr=resstds, **errorbarkwargs)
		
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))

	if featres:
		ax.set_ylim(featres.low, featres.high)
		ax.set_ylabel(featres.nicename)
	else:
		ax.set_ylabel("{} - {}".format(featy.nicename, featx.nicename))

	ax.set_xlabel(featx.nicename)
	ax.set_xlim(binrange)

	if selector:
		ax.set_title(selector.name)

	if title:
		ax.set_title(title)

	
