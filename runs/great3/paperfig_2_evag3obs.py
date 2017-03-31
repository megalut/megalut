import matplotlib
#matplotlib.use("AGG")
matplotlib.use("pdf")

import megalut
import megalut.tools
import megalut.plot
from megalut.tools.feature import Feature

import megalutgreat3
import astropy


import config
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import AutoMinorLocator, LogLocator

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

from matplotlib.ticker import Locator


#Fixing a minor locator symlog bug: 
#http://stackoverflow.com/questions/20470892/how-to-place-minor-ticks-on-symlog-scale
class MinorSymLogLocator(Locator):
	"""
	Dynamically find minor tick positions based on the positions of
	major ticks for a symlog scaling.
	"""
	def __init__(self, linthresh):
		"""
		Ticks will be placed between the major ticks.
		The placement is linear for x between -linthresh and linthresh,
		otherwise its logarithmically
		"""
		self.linthresh = linthresh

	def __call__(self):
		'Return the locations of the ticks'
		majorlocs = self.axis.get_majorticklocs()

		# iterate through minor locs
		minorlocs = []

		# handle the lowest part
		for i in xrange(1, len(majorlocs)):
			majorstep = majorlocs[i] - majorlocs[i-1]
			if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
				ndivs = 10
			else:
				ndivs = 9
			minorstep = majorstep / ndivs
			locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
			minorlocs.extend(locs)

		return self.raise_if_exceeds(np.array(minorlocs))

	def tick_values(self, vmin, vmax):
		raise NotImplementedError('Cannot get tick locations for a '
								  '%s type.' % type(self))



catpath = config.great3.path("summary_{}.pkl".format(config.predcode))
#catpath = config.great3.path("{}_summary_{}.pkl".format(config.datasets["mimic-great3"], config.predcode))


cat = megalut.tools.io.readpickle(catpath)


# Computing residuals

cat["pre_s1_res"] = cat["pre_s1"] - cat["tru_s1"]
cat["pre_s2_res"] = cat["pre_s2"] - cat["tru_s2"]

cat["pre_s1w_res"] = cat["pre_s1w"] - cat["tru_s1"]
cat["pre_s2w_res"] = cat["pre_s2w"] - cat["tru_s2"]



# Computing PSF rotated errors
# angles:
rotations = .5 * np.arctan2(cat["tru_psf_g2"], cat["tru_psf_g1"]) # Note the inverted order of components
		

# rotating  predictions:
cat["pre_s+"] = cat["pre_s1"] * np.cos(-2. * rotations) - cat["pre_s2"] * np.sin(-2. * rotations)
cat["pre_sx"] = cat["pre_s1"] * np.sin(-2. * rotations) + cat["pre_s2"] * np.cos(-2. * rotations)

# rotating weighted predictions:
cat["pre_s+w"] = cat["pre_s1w"] * np.cos(-2. * rotations) - cat["pre_s2w"] * np.sin(-2. * rotations)
cat["pre_sxw"] = cat["pre_s1w"] * np.sin(-2. * rotations) + cat["pre_s2w"] * np.cos(-2. * rotations)

# rotating truth:
cat["tru_s+"] = cat["tru_s1"] * np.cos(-2. * rotations) - cat["tru_s2"] * np.sin(-2. * rotations)
cat["tru_sx"] = cat["tru_s1"] * np.sin(-2. * rotations) + cat["tru_s2"] * np.cos(-2. * rotations)

# And again the residuals
cat["pre_s+_res"] = cat["pre_s+"] - cat["tru_s+"]
cat["pre_sx_res"] = cat["pre_sx"] - cat["tru_sx"]

cat["pre_s+w_res"] = cat["pre_s+w"] - cat["tru_s+"]
cat["pre_sxw_res"] = cat["pre_sxw"] - cat["tru_sx"]


#print megalut.tools.table.info(cat)
#mets = megalutgreat3.utils.metrics(cat, ("tru_s1", "tru_s2"), ("pre_s1w", "pre_s2w"), psfgcols=("tru_psf_g1", "tru_psf_g2"))


def labeloutliers(ax, cat, pre, tru, thr=0.01, whichones=None):
	"""
	whichones supercedes threshold
	"""
	cat["offset"] = cat[pre] - cat[tru]
	for row in cat:
		
		if whichones is not None:
			if row["subfield"] not in whichones:
				continue
		elif np.fabs(row["offset"]) < thr:
			continue
		
		# We are here only if we want to draw that label
		#print row[tru], row[pre], str(row["subfield"])
		ax.text(row[tru]+0.003, row[pre] - row[tru], str(row["subfield"]), fontsize=8)
	

def addmetrics(ax, xfeat, yfeat):
	metrics = megalut.tools.metrics.metrics(cat, xfeat, yfeat, pre_is_res=True)
	line1 = r"$\mathrm{RMSD} = %.5f $" % (metrics["rmsd"])
	#line2 = r"$m: %.1f +/- %.1f; c: %.1f +/- %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	#line2 = r"$m=%.1f \pm %.1f; c=%.1f \pm %.1f \, [10^{-3}]$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	line2 = r"$m=%.1f \pm %.1f \cdot 10^{-3}$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0)
	line3 = r"$c=%.1f \pm %.1f \cdot 10^{-3}$" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	
	ax.annotate(line1, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -7), textcoords='offset points', ha='left', va='top', fontsize=8)
	ax.annotate(line2, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -16), textcoords='offset points', ha='left', va='top', fontsize=8)
	ax.annotate(line3, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -25), textcoords='offset points', ha='left', va='top', fontsize=8)

	


sr = 0.06 # shear range
srp = 0.25 # shear range predictions
swrp = 0.02
symthres = 0.01
#subs = [1.1,2.,3.,4.,5.,6.,7.,8.,9.,-1.1,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]
#subs = [2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]

fig = plt.figure(figsize=(9, 6))

fig.text(.005, .94, config.great3.get_branchacronym().upper(), fontdict={"fontsize":22})


paneltoplevel = 0.55
panelbottomlevel = 0.1
panelxw = 0.23
panelyw = 0.35

#cmap="coolwarm"
#cmap="viridis_r"
cmap="plasma_r"

# Little numbers
acro = config.great3.get_branchacronym()
if acro == "cgc":
	whichones = [2]
elif acro == "csc":
	#whichones = None
	whichones = []


#minorlocator = LogLocator(10,subs=subs[:])
minorlocator = MinorSymLogLocator(1e-1)

defaultmetrics = False

xaxislabelpad = -1

featc = Feature("psf_adamom_sigma", nicename=r"PSF $\mathtt{adamom\_sigma}$ [pix]")


ax = plt.axes([.09, paneltoplevel, panelxw, panelyw])
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr, nicename=r"True $\gamma_1$"), Feature("pre_s1_res", -srp, srp, nicename=r"Predicted $\gamma_1$ $-$ True $\gamma_1$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, hidecbar=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s1", "tru_s1", whichones=whichones)
ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#cb = fig.colorbar(ax) 
#cb = ax.images[-1].colorbar
#cb.remove()
ax.yaxis.labelpad = xaxislabelpad
addmetrics(ax, Feature("tru_s1"), Feature("pre_s1_res"))


ax = plt.axes([.33, paneltoplevel, panelxw, panelyw])
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr, nicename=r"True $\gamma_1$"), Feature("pre_s1w_res", -srp, srp, nicename=r"Predicted $\gamma_1$ $-$ True $\gamma_1$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, hidecbar=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s1w", "tru_s1", thr=0.004, whichones=whichones)
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])
ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#ax.yaxis.set_visible(False)
ax.set_yticklabels([])
ax.yaxis.label.set_visible(False)
addmetrics(ax, Feature("tru_s1"), Feature("pre_s1w_res"))


ax = plt.axes([.68, paneltoplevel, panelxw+0.02, panelyw])
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s+", -sr, sr, nicename=r"True $\gamma_+$"), Feature("pre_s+w_res", -srp, srp, nicename=r"Predicted $\gamma_+$ $-$ True $\gamma_+$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s+w", "tru_s+", thr=0.004, whichones=whichones)
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])
ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#ax.yaxis.set_visible(False)
#ax.set_yticklabels([])
#ax.yaxis.label.set_visible(False)
ax.yaxis.labelpad = xaxislabelpad
addmetrics(ax, Feature("tru_s+"), Feature("pre_s+w_res"))

	
### Bottom row

ax = plt.axes([.09, panelbottomlevel, panelxw, panelyw])

megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr, nicename=r"True $\gamma_2$"), Feature("pre_s2_res", -srp, srp, nicename=r"Predicted $\gamma_2$ $-$ True $\gamma_2$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, hidecbar=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s2", "tru_s2", whichones=whichones)

ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#cb = fig.colorbar(ax) 
#cb = ax.images[-1].colorbar
#cb.remove()
ax.yaxis.labelpad = xaxislabelpad
addmetrics(ax, Feature("tru_s2"), Feature("pre_s2_res"))


ax = plt.axes([.33, panelbottomlevel, panelxw, panelyw])

megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr, nicename=r"True $\gamma_2$"), Feature("pre_s2w_res", -srp, srp, nicename=r"Predicted $\gamma_2$ $-$ True $\gamma_2$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, hidecbar=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s2w", "tru_s2", thr=0.004, whichones=whichones)

ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#ax.yaxis.set_visible(False)
ax.set_yticklabels([])
ax.yaxis.label.set_visible(False)
addmetrics(ax, Feature("tru_s2"), Feature("pre_s2w_res"))


ax = plt.axes([.68, panelbottomlevel, panelxw, panelyw])

megalut.plot.scatter.scatter(ax, cat, Feature("tru_sx", -sr, sr, nicename=r"True $\gamma_{\times}$"), Feature("pre_sxw_res", -srp, srp, nicename=r"Predicted $\gamma_{\times}$ $-$ True $\gamma_{\times}$"), featc, yisres=True, cmap=cmap, metrics=defaultmetrics, showidline=True, hidecbar=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_sxw", "tru_sx", thr=0.004, whichones=whichones)
#labeloutliers(ax, cat, "pre_sx", "tru_sx")

ax.set_yscale('symlog', linthreshy=symthres)
ax.xaxis.set_major_locator(plticker.MultipleLocator(base=0.05))
#ax.yaxis.set_minor_locator(plticker.MultipleLocator(base=0.002))
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
#ax.yaxis.set_visible(False)
#ax.set_yticklabels([])
#ax.yaxis.label.set_visible(False)
ax.yaxis.labelpad = xaxislabelpad
addmetrics(ax, Feature("tru_sx"), Feature("pre_sxw_res"))





plotpath = config.great3.path("fig_2_{}.pdf".format(config.great3.get_branchacronym()))
plt.savefig(plotpath)
#plt.show()
print plotpath
