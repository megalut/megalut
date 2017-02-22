"""
Validation plot
"""

import megalut
import megalutgreat3
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt
import numpy as np

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)


spname = "G3CGCSersics_statell"

#predname = "ada4_sum55_valid"
component = 1 # which shear component


def main():


	for subfield in config.great3.subfields:
		
		measdir = config.great3.path("simmeas","%03i" % subfield)
		catpath = os.path.join(measdir, spname, "groupmeascat_cases_pred_wpred.pkl")
		cat = megalut.tools.io.readpickle(catpath)
		#print megalut.tools.table.info(cat)
		#cat = cat[0:1]
	
		plotpath = None
		#plotpath = config.great3.path("ml","%03i" % subfield, "valplot_{}_comp{}.png".format(predname, component))
		
		plot(cat, component, filepath=plotpath)
		logger.info("Plotted to {}".format(plotpath))




def plot(cat, component, filepath=None):
	
	rea = "all"
	ebarmode = "scatter"
	
	if component == 1:
	
		cat["pre_g1"] = cat["pre_g1_adamom"]
		cat["pre_g1w_norm"] = cat["pre_g1w"] / np.max(cat["pre_g1w"])

		megalut.tools.table.addrmsd(cat, "pre_g1", "tru_g1")
		megalut.tools.table.addstats(cat, "pre_g1", "pre_g1w")
		
		pre_gcw = Feature("pre_g1w", rea=rea)
		pre_gcw_norm = Feature("pre_g1w_norm", rea=rea)
		
		pre_gc = Feature("pre_g1", rea=rea)
		
		pre_gc_bias = Feature("pre_g1_bias")
		pre_gc_mean = Feature("pre_g1_mean")
		pre_gc_wmean = Feature("pre_g1_wmean")
		tru_gc = Feature("tru_g1")
		
		
	elif component == 2:
		pass
		
		
	

	fig = plt.figure(figsize=(24, 12))

	ax = fig.add_subplot(3, 5, 1)
	megalut.plot.hist.hist(ax, cat, pre_gcw)
	
	ax = fig.add_subplot(3, 5, 2)
	megalut.plot.hist.hist(ax, cat, pre_gcw_norm)
	
	ax = fig.add_subplot(3, 5, 3)
	megalut.plot.scatter.scatter(ax, cat, Feature("adamom_sigma", rea=rea), Feature("adamom_flux", rea=rea), featc=pre_gcw)

	ax = fig.add_subplot(3, 5, 4)
	megalut.plot.scatter.scatter(ax, cat, Feature("snr", rea=rea), pre_gcw)
	
	
	
	ax = fig.add_subplot(3, 5, 6)
	megalut.plot.scatter.scatter(ax, cat, tru_gc, pre_gc_mean, showidline=True, metrics=True)
	ax.set_title("Without weights")

	ax = fig.add_subplot(3, 5, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_gc, pre_gc_wmean, showidline=True, metrics=True)
	ax.set_title("With weights")
	
	
	
	#ax = fig.add_subplot(3, 5, 3)
	#megalut.plot.scatter.scatter(ax, cat, Feature("tru_rad", rea=rea), Feature("tru_flux", rea=rea), featc=Feature("pre_g1w", rea=rea))

	
	"""
	ax = fig.add_subplot(3, 5, 1)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  pre_gc_mean, featc=snr_mean, showidline=True, metrics=True)
	
	ax = fig.add_subplot(3, 5, 2)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("snr_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 3)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_rad"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 4)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_sersicn"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 5)
	megalut.plot.scatter.scatter(ax, cat, tru_sc, Feature("tru_g"), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 6)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_sb"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 7)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_frac"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 8)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("tru_flux"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 9)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux", rea=1), pre_gc_bias)
	#megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_flux_mean"), pre_gc_bias)
	ax = fig.add_subplot(3, 5, 10)
	megalut.plot.scatter.scatter(ax, cat, tru_sc,  Feature("adamom_sigma", rea=1), pre_gc_bias)

	
	ax = fig.add_subplot(3, 5, 11)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sb"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 12)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_flux"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 13)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_rad"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 14)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_sersicn"), ncbins=3, equalcount=True, ebarmode=ebarmode)
	ax = fig.add_subplot(3, 5, 15)
	megalut.plot.bin.res(ax, cat, tru_sc, pre_gc_mean, Feature("tru_g"), ncbins=3, equalcount=True, ebarmode=ebarmode)

	"""
	
	
	plt.tight_layout()

	if filepath:
		plt.savefig(filepath)
	else:
		plt.show()
	plt.close(fig) # Helps releasing memory when calling in large loops.


if __name__ == "__main__":
    main()
	
