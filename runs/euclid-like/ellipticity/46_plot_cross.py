import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

from sky.utils import flux2mag

import logging
logger = logging.getLogger(__name__)


traindir = os.path.join(config.workdir, "train_simple")
outdir = os.path.join(traindir, "plots")

megalut.plot.figures.set_fancy(14)

component = "1"
component2 = "2"
main_pred = "s{}".format(component)
maincol = "tru_{}".format(main_pred)
main_feat = Feature(maincol)

# Quick and dirty fix
main_pred2 = "s{}".format(component2)
maincol2 = "tru_{}".format(main_pred2)
main_feat2 = Feature(maincol2)

nbins = 3
ncbins = 3

param_feats = [
		Feature("snr_mean", nicename=r"S/N", low=0),
		Feature("tru_mag", nicename=r"\emph{VIS}-like AB mag", low=19.5, high=24.5),
		Feature("tru_rad", nicename=r"$R_{hl}$ [arcsec]"),
		Feature("tru_sersicn", nicename=r"$n$"),
		Feature("tru_g", nicename=r"$e$"),
		]

formatters = ['%d', '%d', '%0.1f', '%0.1f', '%0.1f', '%d']


outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)
print megalut.tools.table.info(cat)

for comp in [component,component2]:
	cat["pre_g{}".format(comp)] = cat["pre_g{}_adamom".format(comp)]
	megalut.tools.table.addstats(cat, "pre_g{}".format(comp))
	megalut.tools.table.addrmsd(cat, "pre_g{}".format(comp), "tru_s{}".format(comp))

megalut.tools.table.addstats(cat, "snr")


cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

s = megalut.tools.table.Selector("ok", [
	("min", "snr_mean", 10),
	("in", "tru_rad", 0.1, 2.),
	("max", "adamom_frac", 0.01)
	]
	)

cat = s.select(cat)


isubfig = 1
ncol = 1
nlines = 1
fig = plt.figure()#figsize=(4,4))
plt.subplots_adjust(wspace=0.16)
plt.subplots_adjust(hspace=0.27)
plt.subplots_adjust(right=0.98)
plt.subplots_adjust(top=0.98)
import matplotlib.transforms as mtransforms
no_legend = True

assert "res" not in cat.colnames
lintreshy = 2e-3
lintreshx = 2e-4

coln = 0

colours = {1:'k', 2:'r', 'mean':'g'}
labels = {1:'Component 1', 2:'Component 2', 'mean':'Average'}

metrics = {
	1:megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_g1_bias"), pre_is_res=True),
	2:megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_g2_bias"), pre_is_res=True),
	'mean':{}
	}

for k in metrics[1].keys():
	metrics['mean'][k] = (metrics[1][k] + metrics[2][k]) / 2. 

for iplot, comp in enumerate([1,2, 'mean']):
	
	ax = fig.add_subplot(111)
	
	trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
	ax.fill_between([0, 1], -lintreshy, lintreshy, alpha=0.2, facecolor='darkgrey', transform=trans)
	ax.axvspan(-lintreshx, lintreshx, alpha=0.2, facecolor='darkgrey')
	ax.axhline(0, ls='--', color='k')
	ax.axvline(0, ls='--', color='k')
	
	ax.set_ylabel(r"Multiplicative bias $\mu$")
	ax.set_xlabel(r"Additive bias $c$")
	
	ax.errorbar(metrics[comp]['c'], metrics[comp]['m'], xerr=metrics[comp]['cerr'], yerr=metrics[comp]['merr'], fmt='x', color=colours[comp], label=labels[comp])
	
	
	ax.set_yscale('symlog', linthreshy=lintreshy)
	ax.set_xscale('symlog', linthreshx=lintreshx)
	
	ax.set_ylim([-1e-1, 1e-1])
	ticks = np.concatenate([np.arange(-lintreshy, lintreshy, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
	s = ax.yaxis._scale
	ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
	ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
	ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
	
	ax.set_xlim([-1e-1, 1e-1])
	ticks = np.concatenate([np.arange(-lintreshx, lintreshx, 1e-4)])#, np.arange(lintresh, 1e-2, 9)])
	s = ax.xaxis._scale
	ax.xaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
	ticks = np.concatenate([ticks, ax.xaxis.get_minor_locator().tick_values(-.1, .1)])
	ax.xaxis.set_minor_locator(ticker.FixedLocator(ticks))
	
	plt.legend(loc="best", handletextpad=0.15,fontsize="medium", framealpha=0.5, columnspacing=0.1, ncol=1, numpoints=1)
	
megalut.plot.figures.savefig(os.path.join(outdir, "cross_bias"), fig, fancy=True, pdf_transparence=True)
plt.show()
