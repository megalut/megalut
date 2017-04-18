"""
Plots the figure of the paper 
"""

import includes
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


traindir = os.path.join(includes.workdir, "train_simple")
outdir = os.path.join(traindir, "plots")

megalut.plot.figures.set_fancy(14)

component = "1"
component2 = "2"
main_pred = "s{}".format(component)
maincol = "tru_{}".format(main_pred)
main_feat = Feature(maincol)

outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)


for comp in [component,component2]:
	rea = -20
	ebarmode = "scatter"
	
	#cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	#megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	#cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]

resr = 0.015
symthres = 0.004

#=======================================================================================
fig = plt.figure(figsize=(8, 3.5))

ax = fig.add_subplot(1, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(1, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')

ax.set_ylabel("")
ax.set_yticklabels([])

plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(outdir, "overall_bias"), fig, fancy=True, pdf_transparence=True)
plt.show()

