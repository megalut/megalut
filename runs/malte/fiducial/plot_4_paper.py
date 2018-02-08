"""
Plots the figure of the paper 
"""

import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import config

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

valname = "{}_on_{}".format(config.datasets["ts"], config.datasets["vs"])
valcat = os.path.join(config.valdir, valname + ".pkl")
cat = megalut.tools.io.readpickle(valcat)


megalut.plot.figures.set_fancy(14)

"""
megalut.tools.table.addstats(cat, "snr")
s = megalut.tools.table.Selector("ok", [
	#("min", "snr_mean", 1.8),
	("min", "snr_mean", 31.),
	#("min", "tru_rad", 2.5),
	("max", "adamom_frac", 0.01)
	]
	)

cat = s.select(cat)
"""

print megalut.tools.table.info(cat)


for comp in ["1", "2"]:
	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))

resr = 0.015
symthres = 0.002

#=======================================================================================
fig = plt.figure(figsize=(8, 3.5))

ax = fig.add_subplot(1, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(1, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')

ax.set_ylabel("")
ax.set_yticklabels([])

plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(config.valdir, valname + "plot_4"), fig, fancy=True, pdf_transparence=True)
plt.show()

