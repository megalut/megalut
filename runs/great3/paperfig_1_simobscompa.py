"""
Classic simobscompa plot
"""
import matplotlib
#matplotlib.use("AGG")
matplotlib.use("pdf")

import megalut
import megalutgreat3
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

from megalut import tools

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)


import matplotlib.cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LinearSegmentedColormap, colorConverter
from matplotlib.ticker import ScalarFormatter
import matplotlib.lines as mlines
import matplotlib.ticker as plticker


from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

def _contour(ax, x, y, color="black", bins=30, minline=0.5, maxline=4.0, nlines=3, smooth=2.0, **kwargs):
	"""
	Note that this accepts numpy arrays, not a catalog and features.
	Write a contour wrapper that accepts same input as the others!
	"""
	
	range = [[x.min(), x.max()], [y.min(), y.max()]]
	
	# Choose the default "sigma" contour levels.
	levels = 1.0 - np.exp(-0.5 * np.linspace(minline, maxline, nlines) ** 2)

	H, X, Y = np.histogram2d(x.flatten(), y.flatten(), bins=bins, range=range)

	from scipy.ndimage import gaussian_filter
	if smooth is not None:
		 if gaussian_filter is None:
			 raise ImportError("Please install scipy for smoothing")
		 H = gaussian_filter(H, smooth)

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
	#ax.contour(X2, Y2, H2.T, V, colors=color, **kwargs) # Complains about repeated and non-sorted V values, so here is a quick fix, putting them in the right order:
	V = sorted(list(set(V)))
	ax.contour(X2, Y2, H2.T, V, colors=color, **kwargs)


def simobs(ax, obscat, simcatg3, simcattrain, featx, featy, sidehists=True, sidehistkwargs=None, title=None, legend=False, plotpoints=True, **kwargs):
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
	obsdata = tools.feature.get1Ddata(obscat, [featx, featy] , keepmasked=False)	
	simdatag3 = tools.feature.get1Ddata(simcatg3, [featx, featy], keepmasked=False)
	simdatatrain = tools.feature.get1Ddata(simcattrain, [featx, featy], keepmasked=False)


	
	# And the contours:
	contourkwargs = {"bins":100, "smooth":4.0, "minline":1.0, "maxline":2.0, "nlines":2, "zorder":100}
	contourkwargs.update(kwargs)
	_contour(ax, obsdata[featx.colname], obsdata[featy.colname], color="red", linestyles='-', **contourkwargs)
	_contour(ax, simdatag3[featx.colname], simdatag3[featy.colname], color="blue", linestyles=':', **contourkwargs)
	_contour(ax, simdatatrain[featx.colname], simdatatrain[featy.colname], color="green", linestyles='--', **contourkwargs)
	
	
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
		mysidehistxkwargs = {"histtype":"step", "normed":"True", "bins":50, "alpha":1, "range":histxrange} # for x
		mysidehistxkwargs.update(sidehistkwargs)
		mysidehistykwargs = {"histtype":"step", "normed":"True", "bins":50, "alpha":1, "range":histyrange} # for y
		mysidehistykwargs.update(sidehistkwargs)
	
		divider = make_axes_locatable(ax)
		axhistx = divider.append_axes("top", 1.0, pad=0.1, sharex=ax)
		axhisty = divider.append_axes("right", 1.0, pad=0.1, sharey=ax)
		
		axhistx.hist(obsdata[featx.colname], color="blue", ec="red", ls="-", **mysidehistxkwargs)	
		axhistx.hist(simdatag3[featx.colname], color="red", ec="blue", ls=":", **mysidehistxkwargs)
		axhistx.hist(simdatatrain[featx.colname], color="green", ec="green", ls="--", **mysidehistxkwargs)
		
		axhisty.hist(obsdata[featy.colname], color="blue", ec="red", ls="-", orientation='horizontal', **mysidehistykwargs)
		axhisty.hist(simdatag3[featy.colname], color="red", ec="blue", ls=":", orientation='horizontal', **mysidehistykwargs)
		axhisty.hist(simdatatrain[featy.colname], color="green", ec="green", ls="--", orientation='horizontal', **mysidehistykwargs)
		
		# Hiding the ticklabels
		for tl in axhistx.get_xticklabels():
			tl.set_visible(False)
		for tl in axhisty.get_yticklabels():
			tl.set_visible(False)

		# Hide the hist ticks
		axhistx.yaxis.set_ticks([]) # or set_ticklabels([])
		axhisty.xaxis.set_ticks([])
	
	
	
	# We set the limits and labels:
	ax.set_xlim(featx.low, featx.high)
	ax.set_ylim(featy.low, featy.high)
	ax.set_xlabel(featx.nicename)
	ax.set_ylabel(featy.nicename)
	
	# We want minor ticks:
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))
	ax.yaxis.set_minor_locator(AutoMinorLocator(5))
	
	"""
	if legend:
		ax.annotate("Simulations", color="red", xy=(1.0, 1.0), xycoords='axes fraction', xytext=(-8, -8), textcoords='offset points', ha='right', va='top')
		ax.annotate("Observations", color="blue", xy=(1.0, 1.0), xycoords='axes fraction', xytext=(-8, -24), textcoords='offset points', ha='right', va='top')
	"""
	



def main():

	assert len(config.great3.subfields) == 1
	subfield = config.great3.subfields[0]
	
			

	plotpath = config.great3.path("fig_1_{}_{}.pdf".format(config.great3.get_branchacronym(), subfield))
		
	measdir = config.great3.subpath(subfield, "simmeas")

	simcatg3 = megalut.tools.io.readpickle(os.path.join(measdir, "simobscompa-G3", "groupmeascat.pkl"))
	#print megalut.tools.table.info(simcat)
	simcattrain = megalut.tools.io.readpickle(os.path.join(measdir, "simobscompa-train", "groupmeascat.pkl"))
	#print megalut.tools.table.info(simcat)

	obscat = megalut.tools.io.readpickle(config.great3.subpath(subfield, "obs", "img_meascat.pkl"))
	#print megalut.tools.table.info(obscat)
	#obscat = obscat[:1000]
			
	for cat in [simcatg3, simcattrain, obscat]:
		cat["adamom_log_flux"] = np.log10(cat["adamom_flux"])
		cat["adamom_g"] = np.hypot(cat["adamom_g1"], cat["adamom_g2"])
	

	fig = plt.figure(figsize=(9, 3))
	#fig = plt.figure(figsize=(8, 8))
	
	subfieldstr = str(subfield)
	if len(subfieldstr) == 4: # We cut the "1000"
		subfieldstr = subfieldstr[1:]
	
	fig.text(.02, .58, config.great3.get_branchacronym().upper(), fontdict={"fontsize":22})
	fig.text(.02, .5, "Subfield {}".format(subfieldstr), fontdict={"fontsize":10})

	#fig.text(.05, .7, "GREAT3".format(subfieldstr), fontdict={"fontsize":10, "color":"red"})
	#fig.text(.05, .65, "Mock".format(subfieldstr), fontdict={"fontsize":10, "color":"blue"})
	#fig.text(.05, .6, "Uniform".format(subfieldstr), fontdict={"fontsize":10, "color":"green"})

	
	ax = plt.axes([.3, .2, .29, .78])
	#ax = fig.add_subplot(1, 2, 1)
	if config.great3.obstype == "space":
		simobs(ax, obscat, simcatg3, simcattrain, Feature("adamom_log_flux", 0.3, 2.5, nicename=r"$log_{10}(\mathtt{adamom\_flux})$"), Feature("adamom_sigma", 0, 10, nicename=r"$\mathtt{adamom\_sigma} [\mathrm{pix}]$"), legend=True, plotpoints=False)
	elif config.great3.obstype == "ground":
		simobs(ax, obscat, simcatg3, simcattrain, Feature("adamom_log_flux", 0.3, 2.5, nicename=r"$log_{10}(\mathtt{adamom\_flux})$"), Feature("adamom_sigma", 1., 3., nicename=r"$\mathtt{adamom\_sigma} [\mathrm{pix}]$"), legend=True, plotpoints=False)


	#ax = fig.add_subplot(1, 2, 2)
	ax = plt.axes([.7, .2, .29, .78])
	simobs(ax, obscat, simcatg3, simcattrain, Feature("adamom_g", -0.09, 0.6, nicename=r"$\mathtt{adamom\_g}$"), Feature("adamom_rho4", 1.8, 2.8, nicename=r"$\mathtt{adamom\_rho4}$"), plotpoints=False)
	ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.2))


	obsline = mlines.Line2D([], [], color='red', ls="-", marker=None, label='GREAT3')
	simg3line = mlines.Line2D([], [], color='blue', ls=":", marker=None, label='Mock sims')
	simtrainline = mlines.Line2D([], [], color='green', ls="--", marker=None, label='Uniform sims')
	
	#plt.legend(handles=[obsline])
	plt.legend(handles=[obsline, simg3line, simtrainline], bbox_to_anchor=(0.16, 0.999), bbox_transform=plt.gcf().transFigure, fontsize=10)
		   
	#plt.tight_layout()

	
	plt.savefig(plotpath)
	

if __name__ == "__main__":
    main()
	
