"""
Plots the figure of the paper 
"""

import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.colors
import matplotlib

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)



#megalut.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)



valname = config.wvalname

#selstr = "snr-above-10"
selstr = "snr-above-10-sigma-above-1.5"
#selstr = "realcut"


if selstr in config.datasets["vo"] and not selstr in config.datasets["tw"]:
	#title=r"Retaining only galaxies with S/N $>$ 10.0 for the validation"
	#title=r"Retaining only galaxies with S/N $>$ 10.0 and {\tt adamom\_sigma} $>$ 1.5 for the validation"
	title=r"Same shear estimator applied on a selection of sources with S/N $>$ 10.0 and {\tt adamom\_sigma} $>$ 1.5 pixel:"
	if selstr == "realcut":
		title = r"Same shear estimator applied on a (theoretical) selection of sources in R and mag to match."
	
	mode = 2
	
elif selstr in config.datasets["vo"] and selstr in config.datasets["tw"]:
	#title=r"Retaining galaxies with S/N $>$ 10.0 for the training and the validation"
	#title=r"Retaining only galaxies with S/N $>$ 10.0 and {\tt adamom\_sigma} $>$ 1.5 for the training and the validation"
	#title=r"Using weight predictions trained with the selection S/N $>$ 10.0 and {\tt adamom\_sigma} $>$ 1.5 pixel:"
	title=r"Applying the same selection S/N $>$ 10.0 and {\tt adamom\_sigma} $>$ 1.5 pixel for both training and validation:"
	
	mode = 3

else:
	title=r"Without specific selection of training or validation galaxies:"
	mode = 1

valcatpath = os.path.join(config.valdir, valname + ".pkl")
cat = megalut.tools.io.readpickle(valcatpath)


# Important so that masked point don't show up in the third panel
cat["snr"].mask = cat["pre_s1"].mask

#print megalut.tools.table.info(cat)

for comp in ["1","2"]:

	
	#cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])
	#megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]


resr = 0.01
wplotrea = -10

snr = Feature("snr", 3.0, 150.0, nicename="S/N", rea=wplotrea)
tru_mag = Feature("tru_mag", 20, 25.7, nicename="Magnitude", rea=wplotrea)
tru_rad = Feature("tru_rad", 0.0, 13.0, nicename=r"Half-light radius $R$ [pix]", rea=wplotrea)


tru_s1 = Feature("tru_s1", nicename=r"$g_1^{\mathrm{true}}$")
tru_s2 = Feature("tru_s2", nicename=r"$g_2^{\mathrm{true}}$")

pre_s1_bias = Feature("pre_s1_bias", -resr, resr, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
pre_s2_bias = Feature("pre_s2_bias", -resr, resr, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
pre_s1_wbias = Feature("pre_s1_wbias", -resr, resr, nicename=r"$\left(\sum\hat{g}_1 w_1 / \sum w_1 \right) - g_{1}^{\mathrm{true}}$")
pre_s2_wbias = Feature("pre_s2_wbias", -resr, resr, nicename=r"$\left(\sum\hat{g}_2 w_2 / \sum w_2 \right) - g_{2}^{\mathrm{true}}$")



def addmetrics(ax, xfeat, yfeat):
	metrics = megalut.tools.metrics.metrics(cat, xfeat, yfeat, pre_is_res=True)
	line1 = r"$10^3 \mu=%.1f \pm %.1f $" % (metrics["m"]*1000.0, metrics["merr"]*1000.0)
	line2 = r"$10^3 c=%.2f \pm %.2f $" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	
	ax.annotate(line1, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -9), textcoords='offset points', ha='left', va='top', fontsize=12)
	ax.annotate(line2, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top', fontsize=12)
	

fig = plt.figure(figsize=(10, 3))
plt.subplots_adjust(
	left  = 0.09,  # the left side of the subplots of the figure
	right = 0.93,    # the right side of the subplots of the figure
	bottom = 0.18,   # the bottom of the subplots of the figure
	top = 0.85,      # the top of the subplots of the figure
	wspace = 0.45,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
	hspace = 0.25,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
	)

idlinekwargs = {"color":"black", "ls":"-"}

#==================================================================================================



ax = fig.add_subplot(1, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
addmetrics(ax, tru_s1, pre_s1_wbias)

#ax.set_xlabel("")
#ax.set_xticklabels([])
#ax.set_ylabel("")
#ax.set_yticklabels([])


ax = fig.add_subplot(1, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
addmetrics(ax, tru_s2, pre_s2_wbias)

#ax.set_ylabel("")
#ax.set_yticklabels([])


if mode != 3:
	ax = fig.add_subplot(1, 3, 3)
	cb = megalut.plot.scatter.scatter(ax, cat, tru_mag, tru_rad, snr, cmap="plasma_r", rasterized = True, norm=matplotlib.colors.LogNorm(vmin=3.0, vmax=150.0))
	ticks = [5, 10, 20, 40, 80]
	ticklabels = [str(tick) for tick in ticks]
	cb.set_ticks(ticks)
	cb.ax.set_yticklabels(ticklabels)


fig.text(.005, .94, title, fontdict={"fontsize":12})

megalut.plot.figures.savefig(os.path.join(config.valdir, valname.replace(".", "p") + "_selbiaseffect"), fig, fancy=True, pdf_transparence=True, nocrop=True)
plt.show()


