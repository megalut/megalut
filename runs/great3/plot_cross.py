import os
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.transforms as mtransforms

import megalut.plot
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


outdirplots = os.path.join('.', "plots")

megalut.plot.figures.set_fancy(16)

metrics_12 = {
	'fGC':{'m1':-1.50, 'm1err':2.78, 'm2':3.18, 'm2err':2.04, 'c1':0.02, 'c1err':0.08, 'c2':0.01, 'c2err':0.06},
	'CGC':{'m1':4.34, 'm1err':3.52, 'm2':1.99, 'm2err':3.03, 'c1':0.02, 'c1err':0.09, 'c2':-0.11, 'c2err':0.08},
	'RGC':{'m1':-5.42, 'm1err':3.15, 'm2':-6.40, 'm2err':3.15, 'c1':0.12, 'c1err':0.09, 'c2':-0.11, 'c2err':0.08},
	'fSC':{'m1':-0.97, 'm1err':1.49, 'm2':-1.87, 'm2err':1.50, 'c1':-0.04, 'c1err':0.04, 'c2':-0.00, 'c2err':0.05},
	'CSC':{'m1':-3.11, 'm1err':3.55, 'm2':-3.73, 'm2err':3.78, 'c1':-0.19, 'c1err':0.09, 'c2':-0.00, 'c2err':0.09},
	'RSC':{'m1':-5.49, 'm1err':3.15, 'm2':-6.40, 'm2err':3.15, 'c1':0.04, 'c1err':0.08, 'c2':0.04, 'c2err':0.08},
	}
																		
metrics_pluscross = { 
	'fGC':{'m1':1.97, 'm1err':2.28, 'm2':-0.30, 'm2err':2.62, 'c1':0.08, 'c1err':0.07, 'c2':-0.02, 'c2err':0.07},
	'CGC':{'m1':1.58, 'm1err':3.43, 'm2':3.70, 'm2err':3.06, 'c1':-0.03, 'c1err':0.09, 'c2':-0.16, 'c2err':0.08},
	'RGC':{'m1':-3.84, 'm1err':3.34, 'm2':-7.98, 'm2err':3.79, 'c1':0.29, 'c1err':0.08, 'c2':-0.02, 'c2err':0.09},
	'fSC':{'m1':-1.55, 'm1err':1.41, 'm2':-1.18, 'm2err':1.57, 'c1':0.07, 'c1err':0.04, 'c2':-0.02, 'c2err':0.04},
	'CSC':{'m1':-0.04, 'm1err':3.73, 'm2':-5.37, 'm2err':3.52, 'c1':-0.35, 'c1err':0.09, 'c2':-0.09, 'c2err':0.09},
	'RSC':{'m1':-3.77, 'm1err':3.08, 'm2':-7.70, 'm2err':3.25, 'c1':-0.01, 'c1err':0.08, 'c2':-0.08, 'c2err':0.08},
	}


metrics_mean = {}
for key in metrics_12.keys():
	metrics_mean[key] = {}
	metrics_mean[key]['m1'] = (metrics_12[key]['m1'] + metrics_12[key]['m2'])/2
	metrics_mean[key]['m1err'] = (metrics_12[key]['m1err'] + metrics_12[key]['m2err'])/2
	metrics_mean[key]['c1'] = metrics_pluscross[key]['c1']
	metrics_mean[key]['c1err'] = metrics_pluscross[key]['c1err']
						
print metrics_mean
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
	

order = ['fGC', 'CGC', 'RGC', 'fSC', 'CSC', 'RSC']
metrics = [metrics_12, metrics_pluscross, metrics_mean]
outname = ["12", "pc", "mmean"]
xlabels = [{1:'c_1', 2:'c_2'}, {1:'c_+', 2:'c_\\times'}, {1:"c_+"}]
ylabels = [{1:'\\mu_1', 2:'\\mu_2'}, {1:'\\mu_+', 2:'\\mu_\\times'}, {1:"\\langle\\mu\\rangle"}]
colours = ['k', 'orange', 'limegreen', 'turquoise', "royalblue", 'r', "#a65628", "#f781bf", "#4daf4a"]
colours = ['maroon', 'navy', 'darkgreen', 'tomato', "steelblue", 'lime', "#a65628", "#f781bf", "#4daf4a"]
markers = ['o','^',"D"] * 2#,'o','*','D']
ls = ['-','-',"-", '--', '--', '--']#,'o','*','D']

lintreshy = 2e-3
lintreshx = 2e-4

assert len(order) <= len(markers)
assert len(order) <= len(colours)
assert len(metrics) <= len(outname)
assert len(metrics) <= len(xlabels)
assert len(metrics) <= len(ylabels)

for imet, metric in enumerate(metrics):
	
	fig = plt.figure(figsize=(7*len(xlabels[imet]), 4.5))
	plt.subplots_adjust(wspace=0.2)
	plt.subplots_adjust(hspace=0.4)
	plt.subplots_adjust(right=0.98)
	plt.subplots_adjust(top=0.96)
	plt.subplots_adjust(bottom=0.12)
	plt.subplots_adjust(left=0.15)
	
	for comp in range(1, 1+len(xlabels[imet])):
	
		ax = fig.add_subplot(1, len(xlabels[imet]), comp)
		
		trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
		ax.fill_between([0, 1], -lintreshy, lintreshy, alpha=0.2, facecolor='darkgrey', transform=trans)
		ax.axvspan(-lintreshx, lintreshx, alpha=0.2, facecolor='darkgrey')
		ax.axhline(0, ls='--', color='k')
		ax.axvline(0, ls='--', color='k')
		
		ax.set_ylabel(r"Multiplicative bias ${%s}$" % ylabels[imet][comp])
		ax.set_xlabel(r"Additive bias ${%s}$" % xlabels[imet][comp])
	
		for ibranch, branch in enumerate(order):
		
		
			_,capsstuff,barlinecols = ax.errorbar(metric[branch]['c{}'.format(comp)] * 1e-3, metric[branch]['m{}'.format(comp)] * 1e-3, \
					xerr=metric[branch]['c{}err'.format(comp)] * 1e-3, yerr=metric[branch]['m{}err'.format(comp)] * 1e-3, \
					fmt=markers[ibranch], color=colours[ibranch], label=branch, elinewidth=1.5)
			
			barlinecols[0].set_linestyle(ls[ibranch])
			barlinecols[1].set_linestyle(ls[ibranch])
			for cap in capsstuff:
				cap.set_markeredgewidth(2)
			
	
		ax.set_yscale('symlog', linthreshy=lintreshy)
		ax.set_xscale('symlog', linthreshx=lintreshx)
	
		ax.set_ylim([-5e-1, 5e-1])
		ticks = np.concatenate([np.arange(-lintreshy, lintreshy, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
		s = ax.yaxis._scale
		ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
		ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
		ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
		
		ax.set_xlim([-5e-1, 5e-1])
		ticks = np.concatenate([np.arange(-lintreshx, lintreshx, 1e-4)])#, np.arange(lintresh, 1e-2, 9)])
		s = ax.xaxis._scale
		ax.xaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
		ticks = np.concatenate([ticks, ax.xaxis.get_minor_locator().tick_values(-.1, .1)])
		ax.xaxis.set_minor_locator(ticker.FixedLocator(ticks))
		
		plt.legend(loc="best", handletextpad=0.15,fontsize="small", framealpha=0.5, columnspacing=0.1, ncol=2, numpoints=1)
		
	megalut.plot.figures.savefig(os.path.join(outdirplots, "great3_cross_plot_{}".format(outname[imet])), fig, fancy=True, pdf_transparence=True)
plt.show()
