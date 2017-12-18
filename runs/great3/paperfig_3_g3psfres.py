#import matplotlib
#matplotlib.use("AGG")
#matplotlib.use("pdf")

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
from matplotlib.ticker import AutoMinorLocator, LogLocator

"""
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)
"""


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

from matplotlib.ticker import Locator



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
	

SMALL_SIZE = 16
MEDIUM_SIZE = 18
BIGGER_SIZE = 22

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
#print megalut.tools.table.info(cat)
#mets = megalutgreat3.utils.metrics(cat, ("tru_s1", "tru_s2"), ("pre_s1w", "pre_s2w"), psfgcols=("tru_psf_g1", "tru_psf_g2"))



#fig = plt.figure(figsize=(9, 6))
fig = plt.figure(figsize=(8, 7))

fig.text(.005, .94, config.great3.get_branchacronym().upper(), fontdict={"fontsize":22})



#ax = plt.axes([.09, paneltoplevel, panelxw, panelyw])

resr = 0.039
symthres = 0.004

ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_g1"), Feature("pre_s1_res", -resr, resr), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_e1", -0.2, 0.15, nicename=r"True $e_{1, \mathrm{PSF}}$"), Feature("pre_s1w_res", -resr, resr, nicename=r"Predicted $g_1$ $-$ True $g_1$"), showidline=True, yisres=True,
color="black", markersize=5, alpha=1.0)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])

ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_g2"), Feature("pre_s2_res", -resr, resr), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

ax = fig.add_subplot(2, 2, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_psf_g2"), Feature("pre_s2w_res", -resr, resr), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')



plt.tight_layout()


plotpath = config.great3.path("fig_3_{}.pdf".format(config.great3.get_branchacronym()))
#plt.savefig(plotpath)
plt.show()
print plotpath
