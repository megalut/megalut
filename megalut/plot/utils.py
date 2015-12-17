"""
Helper functions for plots
Stuff that can be useful in many plots, to avoid repeading it...
"""

import numpy as np
import copy



def showselector(ax, sel):
	"""
	Writes text about the selector on the axes
	"""
	
	
	text = "\n".join([repr(crit) for crit in sel.criteria])
			
	ax.annotate(text, xy=(0.0, 0.5), xycoords='axes fraction', xytext=(8, -12), textcoords='offset points', ha='left', va='top')
	



def getrange(cat, feature):
	"""
	Returns a range (hi, low) to use when plotting the feature, respecting the feature's settings if not "None".
	So it makes sure you get actual numbers.
	"""


	if feature.low is not None and feature.high is not None: 
		customrange = (feature.low, feature.high)
	else:
		customrange = (np.min(cat[feature.colname]), np.max(cat[feature.colname]))

	return customrange




def summabin(x, y, xbinrange=(None, None), nbins=10):
	"""
	For two 1D numpy arrays x and y, summarizes the y data in bins of x.
	
	Returns a dict with arrays containing different information for each bin:
	
	xbincents, xbinlows, xbinhighs,
	ymeans, ystds, ylowps, yhighps,
	ns
	
	
	"""
	
	# Some tests:
	assert x.ndim == 1
	assert y.ndim == 1
	assert x.size == y.size
	assert x.size > 1
	
	# Defining the bin range of the x axis:
	br = list(copy.deepcopy(xbinrange))
	if br[0] is None:
		br[0] = np.min(x)
	if br[1] is None:
		br[1] = np.max(x)
	
	# And now defining the bins:
	binlims = np.linspace(br[0], br[1], nbins+1)
	bincenters = 0.5 * (binlims[0:-1] + binlims[1:])
	assert len(bincenters) == nbins
	
	binindices = np.digitize(x, bins=binlims)
	inrangeindices = np.arange(nbins)+1 # those indices that are within the binlims
	assert len(inrangeindices) == nbins
	

	# And now we loop over the bins to compute our stuff.
	
	ymeans = []
	ystds = []
	ylowps = []
	yhighps = []
	ns = []
		
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools) # number of values falling into the current bin
		
		if nin < 2:
			ymeans.append(np.nan)
			ystds.append(np.nan)
			ylowps.append(np.nan)
			yhighps.append(np.nan)
			ns.append(np.nan)
			continue
		
		ns.append(nin)
		
		thesexvals = x[inbools]
		theseyvals = y[inbools]
		thisymean = np.mean(theseyvals)
				
		ymeans.append(thisymean)
		ystds.append(np.std(theseyvals))
		
		ylowps.append(np.fabs(np.percentile(theseyvals, 15.8) - thisymean))
		yhighps.append(np.fabs(np.percentile(theseyvals, 84.1) - thisymean))
		
	
	ret = {
		"xbincents":np.array(bincenters),
		"xbinlows":np.array(binlims[0:-1]),
		"xbinhighs":np.array(binlims[1:]),
		"ymeans":np.array(ymeans), 
		"ystds":np.array(ystds), 
		"ylowps":np.array(ylowps), 
		"yhighps":np.array(yhighps),
		"ns":np.array(ns)
	}	
	
	for key in ret.keys():
		assert len(ret[key]) == nbins
	
	return ret


