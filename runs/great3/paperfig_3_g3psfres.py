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
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import AutoMinorLocator, LogLocator, MultipleLocator, FixedLocator


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


import galsim

cat["tru_psf_e1"] = 0.0
cat["tru_psf_e2"] = 0.0

for row in cat:
	s = galsim.Shear(g1=row["tru_psf_g1"], g2=row["tru_psf_g2"])
	row["tru_psf_e1"] = s.e1
	row["tru_psf_e2"] = s.e2
	

"""
SMALL_SIZE = 14
MEDIUM_SIZE = 16
BIGGER_SIZE = 30

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
#print megalut.tools.table.info(cat)
#mets = megalutgreat3.utils.metrics(cat, ("tru_s1", "tru_s2"), ("pre_s1w", "pre_s2w"), psfgcols=("tru_psf_g1", "tru_psf_g2"))

"""
featc = Feature("psf_adamom_sigma", nicename=r"PSF $\mathtt{adamom\_sigma}$ [pix]")
cmap="plasma_r"


#fig = plt.figure(figsize=(8, 7))
#fig = plt.figure(figsize=(9, 4.5))
fig = plt.figure(figsize=(7.5, 6.4))

fig.text(.005, .94, config.great3.get_branchacronym().upper(), fontdict={"fontsize":22})



#ax = plt.axes([.09, paneltoplevel, panelxw, panelyw])

resr = 0.039
symthres = 0.004
alpha = 0.5
majorLocator = MultipleLocator(0.1)
minorlocator = MinorSymLogLocator(1.0)


#subs = [2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]
#minorlocator = LogLocator(10,subs=subs[:])


tickpos = np.array([0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1])
minorlocator = FixedLocator(list(tickpos) + list(-tickpos))

ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_e1", -0.2, 0.15, nicename=r"True $e_{1, \mathrm{PSF}}$"), Feature("pre_s1_res", -0.2, 0.2, nicename=r"Predicted $g_1$ $-$ True $g_1$"), featc,
cmap=cmap, showidline=True, yisres=True)
ax.set_yscale('symlog', linthreshy=symthres)
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
ax.xaxis.set_major_locator(majorLocator)
#ax.yaxis.set_minor_locator(minorlocator)
# Hiding "0" as it collides with the 10-3:
#ax.axes.yaxis.set_ticklabels([" ", "-0.1", "-0.01", "-0.001"," ", "0.001", "0.01", "0.1"])
ticks = ax.yaxis.get_major_ticks()
ticks[4].label1.set_visible(False)

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_e1", -0.2, 0.15, nicename=r"True $e_{1, \mathrm{PSF}}$"), Feature("pre_s1w_res", -resr, resr, nicename=r"Predicted $g_1$ $-$ True $g_1$"), showidline=True, yisres=True,
alpha=alpha)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])
ax.xaxis.set_major_locator(majorLocator)


ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_e2", nicename=r"True $e_{2, \mathrm{PSF}}$"), Feature("pre_s2_res", -0.2, 0.2, nicename=r"Predicted $g_2$ $-$ True $g_2$"), featc,
cmap=cmap, showidline=True, yisres=True, hidecbar=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.xaxis.set_major_locator(majorLocator)
ax.set_yscale('symlog', linthreshy=symthres)
ax.yaxis.set_minor_locator(minorlocator)
# Hiding "0" as it collides with the 10-3:
#ax.axes.yaxis.set_ticklabels([" ", "-0.1", "-0.01", "-0.001"," ", "0.001", "0.01", "0.1"])
ticks = ax.yaxis.get_major_ticks()
ticks[4].label1.set_visible(False)

ax = fig.add_subplot(2, 2, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_e2", nicename=r"True $e_{2, \mathrm{PSF}}$"), Feature("pre_s2w_res", -0.2, 0.2, nicename=r"Predicted $g_2$ $-$ True $g_2$"), featc,
cmap=cmap, showidline=True, yisres=True, hidecbar=True)
ax.set_yscale('symlog', linthreshy=symthres)
ax.yaxis.set_minor_locator(minorlocator)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.xaxis.set_major_locator(majorLocator)
# Hiding "0" as it collides with the 10-3:
#ax.axes.yaxis.set_ticklabels([" ", "-0.1", "-0.01", "-0.001"," ", "0.001", "0.01", "0.1"])
ticks = ax.yaxis.get_major_ticks()
ticks[4].label1.set_visible(False)





plt.tight_layout()


plotpath = config.great3.path("fig_3_{}.pdf".format(config.great3.get_branchacronym()))
plt.savefig(plotpath)
#plt.show()
print plotpath
