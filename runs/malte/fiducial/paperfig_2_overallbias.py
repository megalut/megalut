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
	
	logger.info("Weights exist")
	
	
	cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]


resr = 0.015
symthres = 0.002

#==================================================================================================

fig = plt.figure(figsize=(8, 7))

ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True, rasterized = True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')

ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
#ax.set_xlabel("")
ax.set_xticklabels([])

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_wbias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True, rasterized = True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_wbias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


#ax.set_xlabel("")
ax.set_xticklabels([])
ax.set_ylabel("")
ax.set_yticklabels([])

ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True, rasterized = True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(2, 2, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_wbias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True, rasterized = True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_wbias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax.set_ylabel("")
ax.set_yticklabels([])

plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_plot_5a"), fig, fancy=True, pdf_transparence=True)

#==================================================================================================

rea=1

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
megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "_plot_5b"), fig, fancy=True, pdf_transparence=True)
plt.show()

