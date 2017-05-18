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
valprecatpath = os.path.join(traindir, "valprewcat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)


for comp in [component,component2]:
	rea = -20
	ebarmode = "scatter"
	
	cat["pre_s{}w_norm".format(comp)] = cat["pre_s{}w".format(comp)] / np.max(cat["pre_s{}w".format(comp)])

	megalut.tools.table.addrmsd(cat, "pre_s{}".format(comp), "tru_s{}".format(comp))
	megalut.tools.table.addstats(cat, "pre_s{}".format(comp), "pre_s{}w".format(comp))
	cat["pre_s{}_wbias".format(comp)] = cat["pre_s{}_wmean".format(comp)] - cat["tru_s{}".format(comp)]

resr = 0.039
symthres = 0.004

#==================================================================================================

fig = plt.figure(figsize=(8, 7))

ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')

ax.set_title("Without weights")
ax.title.set_position([.5, 1.1])
ax.set_xlabel("")
ax.set_xticklabels([])

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", nicename="True shear $g_1$"), Feature("pre_s1_wbias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')
ax.set_title("With weights")
ax.title.set_position([.5, 1.1])

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s1"),  Feature("pre_s1_wbias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax.set_xlabel("")
ax.set_xticklabels([])
ax.set_ylabel("")
ax.set_yticklabels([])

ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_bias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_bias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax = fig.add_subplot(2, 2, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", nicename="True shear $g_2$"), Feature("pre_s2_wbias", -resr, resr, nicename="Shear bias"), showidline=True, yisres=True)
ax.fill_between([-1, 1], -symthres, symthres, alpha=0.2, facecolor='darkgrey')

metrics = megalut.tools.metrics.metrics(cat,  Feature("tru_s2"),  Feature("pre_s2_wbias"), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3c=%.1f \pm %.1f$" % \
	(metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')


ax.set_ylabel("")
ax.set_yticklabels([])

plt.tight_layout()

megalut.plot.figures.savefig(os.path.join(outdir, "overall_bias"), fig, fancy=True, pdf_transparence=True)

#==================================================================================================

fig = plt.figure(figsize=(5, 7))

ax1 = fig.add_subplot(2, 1, 1)
cat["pre_wmean"] = (cat["pre_s1w_norm"] + cat["pre_s2w_norm"])/2.
cat["pre_wdelta"] = np.abs((cat["pre_s1w_norm"] - cat["pre_s2w_norm"]))
megalut.plot.scatter.scatter(ax1, cat, Feature("tru_rad", nicename=r"R [px]", rea=rea), Feature("tru_flux", nicename="F [counts]", rea=rea), featc=Feature("pre_s1w_norm", rea=rea, nicename=r"Weights $w_1$"), cmap="inferno")

ax1.set_xlabel("")
ax1.set_xticklabels([])

xmin, xmax = ax1.get_xlim()

ax2 = fig.add_subplot(2, 1, 2)
megalut.plot.scatter.scatter(ax2, cat, Feature("tru_rad", nicename=r"R [px]", rea=rea), Feature("tru_flux", nicename="F [counts]", rea=rea), featc=Feature("pre_s2w_norm", rea=rea, nicename=r"Weights $w_2$"), cmap="inferno")
ax2.set_xlim([xmin, xmax])

print cat["pre_s1w_norm", "pre_s2w_norm"]

plt.tight_layout()
megalut.plot.figures.savefig(os.path.join(outdir, "weights"), fig, fancy=True, pdf_transparence=True)
plt.show()

exit()

#--------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(8.5, 3))
plt.subplots_adjust(wspace=0.0)
plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(right=0.92)
plt.subplots_adjust(left=0.11)

#------------------------------------------------------------
maxy = cat["pre_s{}_bias".format(component)].max() * 1.06
miny = cat["pre_s{}_bias".format(component)].min() * 1.02

maxsnr = cat["snr_mean".format(component)].max()
minsnr = cat["snr_mean".format(component)].min()

minshear = -0.12
maxshear = 0.12
#------------------------------------------------------------

ax = fig.add_subplot(1, 2, 1)
ax.fill_between([-1, 1], -2e-3, 2e-3, alpha=0.2, facecolor='darkgrey')
ax.axhline(0, ls='--', color='k')
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_s{}_bias".format(component)), \
	featc=Feature("snr_mean"), marker='.', cmap="plasma", hidecbar=False, vmin=minsnr, vmax=maxsnr)
ax.set_xlabel(r"True shear $g_{%s}$" % component)
ax.set_ylabel(r"Shear bias")


metrics = megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_s{}_bias".format(component)), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f;\,10^3c=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, \
	metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
#ax.annotate(r"$10^3c=%.1f \pm %.1f$" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')
ax.set_ylim([miny, maxy])
ax.set_xlim([minshear, maxshear])

#------------------------------------------------------------

ax = fig.add_subplot(1, 2, 2)
ax.fill_between([-1, 1], -2e-3, 2e-3, alpha=0.2, facecolor='darkgrey')
ax.axhline(0, ls='--', color='k')
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_s{}_bias".format(component2)), 
	featc=Feature("snr_mean", nicename="S/N"), marker='.', cmap="plasma", vmin=minsnr, vmax=maxsnr)
ax.set_xlabel(r"True shear $g_{%s}$" % component2)
metrics = megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_s{}_bias".format(component2)), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3m=%.1f \pm %.1f;\,10^3c=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, \
	metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.set_ylim([miny, maxy])
ax.set_xlim([minshear, maxshear])
ax.set_yticklabels([])
ax.set_ylabel("")

#megalut.plot.figures.savefig(os.path.join(outdir, "overall_bias"), fig, fancy=True, pdf_transparence=True)

plt.show()
