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
from . import utils

import astropy

import logging
logger = logging.getLogger(__name__)





def res(ax, cat, feattru, featpre, featc=None, nbins=10, ncbins=3, ebarmode="bias", showidline=True, metrics=True, equalcount=False):
	"""
	Shows residues of a predicted feature featpre in bins of the corresponding truth feattru.
	If featc is specified (c stands for color), this analysis is done in several bins of featc
	(say to check that the shear estimate is unbiased for different galaxy sizes...).
	
	:param feattru: Feature with "true" value, for the x-axis
	:param featpre: Feature with "predicted" value. Residuals will be computed comparing this to feattru.
		Trick: the low and high of featpre are used to define the plot range for the residues.
	:param featc: Feature to make color-bins
	:param nbins: number of bins in the x-axis
	:param ncbins: number of color-bins
	:ebarmode: either "bias" or "scatter". If "bias", errorbars show the std on the mean, and not just the std of the full scatter.
	
	"""

	logger.info("Preparing res plot of '{}' in bins of '{}'".format(featpre.colname, feattru.colname))
	
	errorbarkwargs = {"ls":"None", "marker":".", "lw":1.5, "mew":1.5}

	# First, we get the 1D data, removing all masked points.
	features = [feattru, featpre]
	if featc is not None:
		features.append(featc)
	data = tools.feature.get1Ddata(cat, features, keepmasked=False)
	
	# We compute the residues, for every point.
	assert "res" not in data.colnames
	data["res"] = data[featpre.colname] - data[feattru.colname]
	
	# Defining the bins of the x axis:
	xbinrange = utils.getrange(data, feattru)
			
	# And for the "color" axis:
	if featc is not None:
		logger.info("Building bins in {}...".format(featc.colname))
		cbinrange = utils.getrange(data, featc)
		
		if equalcount is True:
			# With the latest numpy this should work without using a list comprehension, but ok...
			cbinlims = np.array([np.percentile(data[featc.colname], q) for q in np.linspace(0.0, 100.0, ncbins+1)])
		else:
			cbinlims = np.linspace(cbinrange[0], cbinrange[1], ncbins+1)
		
		cbinlows = cbinlims[0:-1]
		cbinhighs = cbinlims[1:]
		cbincenters = 0.5 * (cbinlows + cbinhighs)
		assert len(cbincenters) == ncbins
		
		if ncbins == 1:
			coloriter = iter(["black"])
		elif ncbins <= 3:
			coloriter = iter(["blue", "red", "darkgreen"])
		else:
			coloriter=iter(matplotlib.cm.brg(np.linspace(0,1,ncbins)))
		offsetscale = 0.5*((xbinrange[1] - xbinrange[0])/float(nbins))/float(ncbins)

		for i in range(ncbins):
			
			color = next(coloriter)
			label = "{0:.2g} < {1} < {2:.2g}".format(cbinlows[i], featc.nicename, cbinhighs[i])
			offset = (i - float(ncbins)/2) * offsetscale
			
			# We build the subset of data that is in this color bin:
			selcbin = tools.table.Selector(label, [("in", featc.colname, cbinlows[i], cbinhighs[i])])
			cbindata = selcbin.select(data)
			if len(cbindata) == 0:
				continue
			cbinfrac = float(len(cbindata)) / float(len(data))
			label += " ({0:.0%})".format(cbinfrac)
			
			# And we perform the line regression
			if metrics is True:
				try:
					md = tools.metrics.metrics(cbindata,
						tools.feature.Feature(feattru.colname), # Redefining those to get rid of any rea settings that don't apply to cbindata
						tools.feature.Feature("res"),
						pre_is_res=True)
					
					metricstext = "m = %.1f +/- %.1f, c = %.1f +/- %.1f" % (md["m"]*1000.0, md["merr"]*1000.0, md["c"]*1000.0, md["cerr"]*1000.0)				
					label += "\n" + metricstext
					ax.plot(np.array(xbinrange), md["m"]*np.array(xbinrange)+md["c"], color=color, ls="-")
					
				except:
					logger.warning("Metrics compuation failed", exc_info = True)
			
			
			# And now bin this in x:
			cbinsumma = utils.summabin(cbindata[feattru.colname], cbindata["res"], xbinrange=xbinrange, nbins=nbins, equalcount=False)
			
			yerr = cbinsumma["ystds"]
			#yerr = np.array([cbinsumma["ylowps"], cbinsumma["yhighps"]])
			yerrbias = yerr / np.sqrt(cbinsumma["ns"])
	
			if ebarmode == "scatter":
				ax.errorbar(cbinsumma["xbincents"]+offset, cbinsumma["ymeans"], yerr=yerr, color=color, label=label, **errorbarkwargs)
			elif ebarmode == "bias":
				ax.errorbar(cbinsumma["xbincents"]+offset, cbinsumma["ymeans"], yerr=yerrbias, color=color, label=label, **errorbarkwargs)
	
			
		
			

	else:	
	
		color="black"
		binsumma = utils.summabin(data[feattru.colname], data["res"], xbinrange=xbinrange, nbins=nbins)
	
		yerr = binsumma["ystds"]
		#yerr = np.array([bindata["ylowps"], bindata["yhighps"]])
		yerrbias = yerr / np.sqrt(binsumma["ns"])
	
		if ebarmode == "scatter":
			ax.errorbar(binsumma["xbincents"], binsumma["ymeans"], yerr=yerr, color=color, **errorbarkwargs)
		elif ebarmode == "bias":
			ax.errorbar(binsumma["xbincents"], binsumma["ymeans"], yerr=yerrbias, color=color, **errorbarkwargs)
	
		if metrics is True:
				try:
					md = tools.metrics.metrics(data,
						tools.feature.Feature(feattru.colname), # Redefining those to get rid of any rea settings that don't apply to cbindata
						tools.feature.Feature("res"),
						pre_is_res=True)
					
					metricstext = "m = %.1f +/- %.1f, c = %.1f +/- %.1f" % (md["m"]*1000.0, md["merr"]*1000.0, md["c"]*1000.0, md["cerr"]*1000.0)				
					ax.plot(np.array(xbinrange), md["m"]*np.array(xbinrange)+md["c"], color=color, ls="-")
					ax.annotate(metricstext, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -12), textcoords='offset points', ha='left', va='top')
			
				except:
					logger.warning("Metrics compuation failed", exc_info = True)
			
	
	
		
	if showidline: # Show the identity line
		idlinekwargs = {"ls":"--", "color":"gray", "lw":1}
		ax.plot(xbinrange, (0.0, 0.0), **idlinekwargs)

	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	ax.set_ylabel(featpre.nicename + " - " + feattru.nicename)
	ax.set_ylim(featpre.low, featpre.high)
	ax.set_xlabel(feattru.nicename)
	ax.set_xlim(xbinrange)

	if featc:
		ax.legend(prop={"size":"medium"})
	
	
	
	
	
	
	
	
	
	
	
	
"""	
	binlims = np.linspace(binrange[0], binrange[1], nbins+1)
	bincenters = 0.5 * (binlims[0:-1] + binlims[1:])
	assert len(bincenters) == nbins
	
	binindices = np.digitize(data[feattru.colname], bins=binlims)
	inrangeindices = np.arange(nbins)+1 # those indices that are within the binlims
	assert len(inrangeindices) == nbins
	
	
	# Defining the bins in "colour"
	if featc is not None:
		cbinrange = utils.getrange(data, featc)
		cbinlims = np.linspace(cbinrange[0], cbinrange[1], ncbins+1)
		cbincenters = 0.5 * (cbinlims[0:-1] + cbinlims[1:])
		assert len(cbincenters) == ncbins
		
	
	ymeans = []
	ystds = []
	ylowps = []
	yhighps = []
	ns = []
		
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools)
		
		if nin < 2:
			ymeans.append(np.nan)
			ystds.append(np.nan)
			ylowps.append(np.nan)
			yhighps.append(np.nan)
			ns.append(np.nan)
			continue
		
		ns.append(nin)
		
		thesexvals = data[feattru.colname][inbools]
		theseyvals = data["res"][inbools]
		
		#assert len(thesexvals) == nin
		#assert len(theseyvals) == nin
		
		ymeans.append(np.mean(theseyvals))
		ystds.append(np.std(theseyvals))
		
		ylowps.append(np.fabs(np.percentile(theseyvals, 15.8) - np.mean(theseyvals)))
		yhighps.append(np.fabs(np.percentile(theseyvals, 84.1) - np.mean(theseyvals)))
		
		
				
	#errorbarkwargs = {"capthick":0, "zorder":-100}
	errorbarkwargs = {"color":"black", "ls":"None", "marker":".", "lw":1.0, "mew":1.0}
	
	#yerr = ystds
	yerr = np.array([ylowps, yhighps])
	yerr_bias = yerr / np.sqrt(np.array(ns))
	yerr_stdbias = np.array(ystds) / np.sqrt(np.array(ns))
	
	if ebarmode == "scatter":
		ax.errorbar(bincenters, ymeans, yerr=yerr, **errorbarkwargs)
	elif ebarmode == "bias":
		ax.errorbar(bincenters, ymeans, yerr=yerr_bias, **errorbarkwargs)
	
	#yerr = np.array(ystds) / np.sqrt(np.array(ns))
	#ax.errorbar(bincenters, ymeans, yerr=yerr, color="red", ls="None", marker=".")
	
	if showidline: # Show the identity line
		idlinekwargs = {"ls":"--", "color":"gray", "lw":1}
		ax.plot(binrange, (0.0, 0.0), **idlinekwargs)


	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	ax.set_ylabel(featpre.nicename + " - " + feattru.nicename)
	ax.set_ylim(featpre.low, featpre.high)
	ax.set_xlabel(feattru.nicename)
	ax.set_xlim(binrange)
	
	
"""	




















def bin(ax, cat, featx, featy, nbins=10, selector=None, showselector=True, title=None, showidline=True, metrics=False,
	ebarmode="scatter"):
	"""
	Summarizes featy in bins of featx.
	
	:param ebarmode: controls what should be shown as error-bars
	
	"""

	logger.info("Preparing bin plot of '{}' versus '{}'".format(featy.colname, featx.colname))
	
	nall = len(cat)
	nsel = nall
	if selector:
		cat = selector.select(cat)
		nsel = len(cat)
		selfrac = float(nsel)/float(nall)
	
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
	ylowps = []
	yhighps = []
	ns = []
		
	for ind in inrangeindices: # We loop over the bins
		
		inbools = binindices == ind # a boolean array
		nin = np.sum(inbools)
		
		if nin < 2:
			ymeans.append(np.nan)
			ystds.append(np.nan)
			ylowps.append(np.nan)
			yhighps.append(np.nan)
			ns.append(np.nan)
			continue
		
		ns.append(nin)
		
		thesexvals = data[featx.colname][inbools]
		theseyvals = data[featy.colname][inbools]
		
		#assert len(thesexvals) == nin
		#assert len(theseyvals) == nin
		
		ymeans.append(np.mean(theseyvals))
		ystds.append(np.std(theseyvals))
		
		ylowps.append(np.fabs(np.percentile(theseyvals, 15.8) - np.mean(theseyvals)))
		yhighps.append(np.fabs(np.percentile(theseyvals, 84.1) - np.mean(theseyvals)))
		
		
				
	#errorbarkwargs = {"capthick":0, "zorder":-100}
	errorbarkwargs = {"color":"black", "ls":"None", "marker":".", "lw":1.0, "mew":1.0}
	
	#yerr = ystds
	yerr = np.array([ylowps, yhighps])
	yerr_bias = yerr / np.sqrt(np.array(ns))
	yerr_stdbias = np.array(ystds) / np.sqrt(np.array(ns))
	
	if ebarmode == "scatter":
		ax.errorbar(bincenters, ymeans, yerr=yerr, **errorbarkwargs)
	elif ebarmode == "bias":
		ax.errorbar(bincenters, ymeans, yerr=yerr_bias, **errorbarkwargs)
	
	#yerr = np.array(ystds) / np.sqrt(np.array(ns))
	#ax.errorbar(bincenters, ymeans, yerr=yerr, color="red", ls="None", marker=".")
	
	
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

	if selector and showselector:
		utils.showselector(ax, selector)


	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	ax.set_ylabel(featy.nicename)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_xlim(binrange)

	if selector and showselector:
		ax.set_title(selector.name + " ({:3.0f} %)".format(100.0*selfrac))

	if title:
		ax.set_title(title)

	
