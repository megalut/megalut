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


import argparse


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('mode', type=str, help='Should I run on vo or vs')
args = parser.parse_args()

if args.mode == "vs":
		
	valname = "{}_on_{}".format(config.datasets["ts"], config.datasets["vs"])
	valcatpath = os.path.join(config.valdir, valname + ".pkl")

elif args.mode == "vo":
	

	sconfname = os.path.splitext(os.path.basename(config.shearconflist[0][1]))[0] # extracts e.g. "sum55"
	wconfname = os.path.splitext(os.path.basename(config.weightconflist[0][1]))[0] # extracts e.g. "sum55w"
	valname = "{}_and_{}_with_{}_{}_on_{}".format(config.datasets["ts"], config.datasets["tw"], sconfname, wconfname, config.datasets["vo"])
	valcatpath = os.path.join(config.valdir, valname + ".pkl")


else:
	logger.info("Unknown mode")
	exit()


cat = megalut.tools.io.readpickle(valcatpath)


megalut.plot.figures.set_fancy(14)

print megalut.tools.table.info(cat)

#megalut.tools.table.addstats(cat, "snr")
#print megalut.tools.table.info(cat)

for comp in ["1","2"]:

	# We mask negative SNR etc
	newmask = cat["snr"] < 0.0
	
	#print np.sum(newmask)
	
	#exit()
	oldmask = cat["pre_s{}".format(comp)].mask
	combimask = np.logical_or(oldmask, newmask)
	cat["pre_s{}".format(comp)].mask = combimask

	# If no weights are in the catalog (or not yet), we add ones
	if not "pre_s{}w".format(comp) in cat.colnames:
		
		# First putting all weights to 1.0:
		cat["pre_s{}w".format(comp)] = np.ones(cat["adamom_g1"].shape)
		logger.info("Setting weights to one")
		
		# Keeping only the best half of SNR
		#megalut.tools.table.addstats(cat, "snr")
		#for row in cat:
		#	row["pre_s{}w".format(comp)] = np.array(row["snr"] > row["snr_med"], dtype=np.float)
		
		# Keeping the best half of sigma
		#megalut.tools.table.addstats(cat, "adamom_sigma")
		#for row in cat:
		#	row["pre_s{}w".format(comp)] = np.array(row["adamom_sigma"] > row["adamom_sigma_med"], dtype=np.float)
	
	#logger.info("Weights exist")
	
	
	cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]


resr = 0.015
symthres = 0.002
wplotrea = -50
snr = Feature("snr", nicename="S/N", rea=wplotrea)
tru_rad = Feature("tru_rad", nicename=r"$R$ [pix]", rea=wplotrea)
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

#==================================================================================================

fig = plt.figure(figsize=(12, 7))

ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_bias, showidline=True, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

addmetrics(ax, tru_s1, pre_s1_bias)


ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
#ax.set_xlabel("")
#ax.set_xticklabels([])

ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_s1, pre_s1_wbias, showidline=True, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])

addmetrics(ax, tru_s1, pre_s1_wbias)


#ax.set_xlabel("")
#ax.set_xticklabels([])
ax.set_ylabel("")
ax.set_yticklabels([])

ax = fig.add_subplot(2, 3, 3)

megalut.plot.scatter.scatter(ax, cat, tru_rad, snr, featc=Feature("pre_s1w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_1$"), cmap="plasma_r", rasterized = True)

#ax.set_xlabel("")
#ax.set_xticklabels([])

#==================================================================================================

ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_bias, showidline=True, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

addmetrics(ax, tru_s2, pre_s2_bias)


ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, tru_s2, pre_s2_wbias, showidline=True, yisres=True)
#ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

addmetrics(ax, tru_s2, pre_s2_wbias)


ax.set_ylabel("")
ax.set_yticklabels([])

ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, cat, tru_rad, snr, featc=Feature("pre_s2w_norm", 0, 1, rea=wplotrea, nicename=r"Weight $w_2$"), cmap="plasma_r", rasterized = True)

plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_wstudy"), fig, fancy=True, pdf_transparence=True)
plt.show()
#==================================================================================================

"""
rea=-100

fig = plt.figure(figsize=(5, 7))

ax1 = fig.add_subplot(2, 1, 1)
cat["pre_wmean"] = (cat["pre_s1w_norm"] + cat["pre_s2w_norm"])/2.
cat["pre_wdelta"] = np.abs((cat["pre_s1w_norm"] - cat["pre_s2w_norm"]))
megalut.plot.scatter.scatter(ax1, cat, Feature("tru_rad", nicename=r"$R$ [px]", rea=rea), Feature("snr", nicename="S/N", rea=rea), featc=Feature("pre_s1w_norm", 0, 1, rea=rea, nicename=r"Weights $w_1$"), cmap="plasma_r", rasterized = True)

ax1.set_xlabel("")
ax1.set_xticklabels([])

xmin, xmax = ax1.get_xlim()

ax2 = fig.add_subplot(2, 1, 2)
megalut.plot.scatter.scatter(ax2, cat, Feature("tru_rad", nicename=r"$R$ [px]", rea=rea), Feature("snr", nicename="S/N", rea=rea), featc=Feature("pre_s2w_norm", 0, 1, rea=rea, nicename=r"Weights $w_2$"), cmap="plasma_r", rasterized = True)
ax2.set_xlim([xmin, xmax])

print cat["pre_s1w_norm", "pre_s2w_norm"]

plt.tight_layout()
megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_bias_b"), fig, fancy=True, pdf_transparence=True)
plt.show()
"""

