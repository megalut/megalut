"""
Plots the figure of the paper 
"""

import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

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



mode = "vo"



if mode == "vs":
	valname = config.valname
elif mode == "vo":
	valname = config.wvalname

valcatpath = os.path.join(config.valdir, valname + ".pkl")
cat = megalut.tools.io.readpickle(valcatpath)

#print megalut.tools.table.info(cat)

for comp in ["1","2"]:

	# This is an interesting experiement. it reminds us how HUGE selection biases are...
	#snrcutmask = cat["snr"] < 10.0
	#cat["pre_s1w"][snrcutmask] = 0.0
	#cat["pre_s2w"][snrcutmask] = 0.0
	

	# If no weights are in the catalog (or not yet), we add ones
	if not "pre_s{}w".format(comp) in cat.colnames:
		
		# First putting all weights to 1.0:
		cat["pre_s{}w".format(comp)] = np.ones(cat["adamom_g1"].shape)
		logger.info("Setting weights to one")	
	
	cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]


resr = 0.015
symthres = 0.002
wplotrea = -10
snr = Feature("snr", nicename="S/N", rea=wplotrea)
#tru_rad = Feature("tru_rad", nicename=r"$R$ [pix]", rea=wplotrea)

tru_sb = Feature("tru_sb", 0, 16, nicename=r"Surface brightness $S$ [pix$^{-2}$]", rea=wplotrea)
tru_rad = Feature("tru_rad", 1.5, 8.5, nicename=r"Half-light radius $R$ [pix]", rea=wplotrea)

adamom_flux = Feature("adamom_flux", 0, 1000, nicename="adamom\_flux", rea=wplotrea)
adamom_sigma = Feature("adamom_sigma", 0, 8, nicename="adamom\_sigma", rea=wplotrea)
adamom_g2 = Feature("adamom_g2", nicename="adamom\_g2", rea=wplotrea)
adamom_rho4 = Feature("adamom_rho4", nicename="adamom\_rho4", rea=wplotrea)


tru_s1 = Feature("tru_s1", nicename=r"$g_1^{\mathrm{true}}$")
tru_s2 = Feature("tru_s2", nicename=r"$g_2^{\mathrm{true}}$")

#pre_s1_bias = Feature("pre_s1_bias", -resr, resr, nicename=r"$\langle \hat{g}_{1} \rangle - g_{1}^{\mathrm{true}} $")
#pre_s2_bias = Feature("pre_s2_bias", -resr, resr, nicename=r"$\langle \hat{g}_{2} \rangle - g_{2}^{\mathrm{true}} $")
#pre_s1_wbias = Feature("pre_s1_wbias", -resr, resr, nicename="Shear bias")
#pre_s2_wbias = Feature("pre_s2_wbias", -resr, resr, nicename="Shear bias")
pre_s1_bias = Feature("pre_s1_bias", -resr, resr, nicename=r"Bias on $\hat{g}_{1}$")
pre_s2_bias = Feature("pre_s2_bias", -resr, resr, nicename=r"Bias on $\hat{g}_{2}$")
pre_s1_wbias = Feature("pre_s1_wbias", -resr, resr)
pre_s2_wbias = Feature("pre_s2_wbias", -resr, resr)


def addmetrics(ax, xfeat, yfeat):
	metrics = megalut.tools.metrics.metrics(cat, xfeat, yfeat, pre_is_res=True)
	line1 = r"$\mathrm{RMSD} = %.5f $" % (metrics["rmsd"])
	#line2 = r"$m: %.1f +/- %.1f; c: %.1f +/- %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	#line2 = r"$m=%.1f \pm %.1f; c=%.1f \pm %.1f \, [10^{-3}]$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	line2 = r"$10^3 \mu=%.1f \pm %.1f $" % (metrics["m"]*1000.0, metrics["merr"]*1000.0)
	line3 = r"$10^3 c=%.1f \pm %.1f $" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0)
	
	ax.annotate(line1, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -9), textcoords='offset points', ha='left', va='top', fontsize=12)
	ax.annotate(line2, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -22), textcoords='offset points', ha='left', va='top', fontsize=12)
	ax.annotate(line3, xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -36), textcoords='offset points', ha='left', va='top', fontsize=12)


fig = plt.figure(figsize=(11.5, 7))
plt.subplots_adjust(
	left  = 0.08,  # the left side of the subplots of the figure
	right = 0.90,    # the right side of the subplots of the figure
	bottom = 0.1,   # the bottom of the subplots of the figure
	top = 0.90,      # the top of the subplots of the figure
	wspace = 0.15,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
	hspace = 0.25,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
	)

idlinekwargs = {"color":"black", "ls":"-"}

#==================================================================================================

ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_bias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
addmetrics(ax, tru_s1, pre_s1_bias)
ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
#ax.set_xlabel("")
#ax.set_xticklabels([])


ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])
addmetrics(ax, tru_s1, pre_s1_wbias)
#ax.set_xlabel("")
#ax.set_xticklabels([])
ax.set_ylabel("")
ax.set_yticklabels([])


ax = fig.add_subplot(2, 3, 3)
pos1 = ax.get_position() # get the original position 
pos2 = [pos1.x0 + 0.05, pos1.y0,  pos1.width, pos1.height] 
ax.set_position(pos2)
megalut.plot.scatter.scatter(ax, cat, adamom_flux, adamom_sigma, featc=Feature("pre_s1w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_1$"), cmap="plasma_r", rasterized = True)
#megalut.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=Feature("pre_s1w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_1$"), cmap="plasma_r", rasterized = True)


#==================================================================================================

ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_bias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
addmetrics(ax, tru_s2, pre_s2_bias)


ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_wbias, showidline=True, idlinekwargs=idlinekwargs, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
addmetrics(ax, tru_s2, pre_s2_wbias)
ax.set_ylabel("")
ax.set_yticklabels([])


ax = fig.add_subplot(2, 3, 6)
pos1 = ax.get_position() # get the original position 
pos2 = [pos1.x0 + 0.05, pos1.y0,  pos1.width, pos1.height] 
ax.set_position(pos2)
#megalut.plot.scatter.scatter(ax, cat, adamom_flux, adamom_sigma, featc=Feature("pre_s2w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_2$"), cmap="plasma_r", rasterized = True)
megalut.plot.scatter.scatter(ax, cat, tru_sb, tru_rad, featc=Feature("pre_s2w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_2$"), cmap="plasma_r", rasterized = True)


#==================================================================================================

#plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_wstudy"), fig, fancy=True, pdf_transparence=True)
plt.show()


