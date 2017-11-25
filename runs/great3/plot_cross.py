import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)


outdirplots = os.path.join('.', "plots")

megalut.plot.figures.set_fancy(14)

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

									
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)

order = ['fGC', 'CGC', 'RGC', 'fSC', 'CSC', 'RSC']
metrics = [metrics_12, metrics_pluscross]
outname = ["12", "pc"]
labels = [{1:'1', 2:'2'}, {1:'+', 2:'\\times'}]
colours = [{1:'k', 2:'r'}, {1:'#8080FE', 2:'darkorange'}]
colours = ['k', 'orange', 'limegreen', 'turquoise', "royalblue", 'r', "#a65628", "#f781bf", "#4daf4a"]
markers = ['o','*',"D",'s','8','p']

import matplotlib.transforms as mtransforms

lintreshy = 2e-3
lintreshx = 2e-4


for imet, metric in enumerate(metrics):
	
	fig = plt.figure(figsize=(15,4.5))
	plt.subplots_adjust(wspace=0.16)
	plt.subplots_adjust(hspace=0.4)
	plt.subplots_adjust(right=0.98)
	plt.subplots_adjust(top=0.97)
	
	for comp in [1,2]:
	
		ax = fig.add_subplot(1, 2, comp)
		
		trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
		ax.fill_between([0, 1], -lintreshy, lintreshy, alpha=0.2, facecolor='darkgrey', transform=trans)
		ax.axvspan(-lintreshx, lintreshx, alpha=0.2, facecolor='darkgrey')
		ax.axhline(0, ls='--', color='k')
		ax.axvline(0, ls='--', color='k')
		
		ax.set_ylabel(r"Multiplicative bias $\mu_{%s}$" % labels[imet][comp])
		ax.set_xlabel(r"Additive bias $c_{%s}$" % labels[imet][comp])
	
		for ibranch, branch in enumerate(order):
		
		
			ax.errorbar(metric[branch]['c{}'.format(comp)] * 1e-3, metric[branch]['m{}'.format(comp)] * 1e-3, \
					xerr=metric[branch]['c{}err'.format(comp)], yerr=metric[branch]['c{}err'.format(comp)], \
					fmt=markers[ibranch], color=colours[ibranch], label=branch)
	
	
		ax.set_yscale('symlog', linthreshy=lintreshy)
		ax.set_xscale('symlog', linthreshx=lintreshx)
	
		ax.set_ylim([-1e-0, 1e-0])
		ticks = np.concatenate([np.arange(-lintreshy, lintreshy, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
		s = ax.yaxis._scale
		ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
		ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
		ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
		
		ax.set_xlim([-1e-0, 1e-0])
		ticks = np.concatenate([np.arange(-lintreshx, lintreshx, 1e-4)])#, np.arange(lintresh, 1e-2, 9)])
		s = ax.xaxis._scale
		ax.xaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
		ticks = np.concatenate([ticks, ax.xaxis.get_minor_locator().tick_values(-.1, .1)])
		ax.xaxis.set_minor_locator(ticker.FixedLocator(ticks))
		
		plt.legend(loc="best", handletextpad=0.15,fontsize="small", framealpha=0.5, columnspacing=0.1, ncol=2, numpoints=1)
		
	megalut.plot.figures.savefig(os.path.join(outdirplots, "great3_cross_plot_{}".format(outname[imet])), fig, fancy=True, pdf_transparence=True)
plt.show()
